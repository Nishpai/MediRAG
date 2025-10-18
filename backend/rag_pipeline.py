"""
RAG Pipeline for Medical FAQ Bot
Handles document loading, embedding creation, vector store management, and query processing.
Uses Google Gemini 2.0 Flash for AI responses.
"""

import os
import time
from typing import List, Dict, Tuple
from functools import lru_cache
from langchain_text_splitters import CharacterTextSplitter
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_classic.chains.retrieval_qa.base import RetrievalQA
from langchain_core.prompts import PromptTemplate
from langchain_core.documents import Document
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MedicalRAGPipeline:
    """
    Main RAG pipeline class for handling medical FAQ queries.
    Implements document loading, embedding, retrieval, and answer generation.
    """
    
    def __init__(self, data_path: str, vectorstore_path: str, gemini_api_key: str):
        """
        Initialize the RAG pipeline.
        
        Args:
            data_path: Path to the medical FAQ data file
            vectorstore_path: Path to store/load FAISS index
            gemini_api_key: Google Gemini API key for embeddings and chat
        """
        self.data_path = data_path
        self.vectorstore_path = vectorstore_path
        self.gemini_api_key = gemini_api_key
        
        # Initialize embedding model (using HuggingFace for local embeddings)
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        
        # Initialize Google Gemini for chat
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp",
            temperature=0.3,
            google_api_key=gemini_api_key
        )
        
        self.vectorstore = None
        self.qa_chain = None
        
        # Query cache for improved performance
        self.query_cache = {}
    
    def load_documents(self) -> List[Document]:
        """
        Load and chunk medical FAQ documents from the data file.
        
        Returns:
            List of Document objects with chunked text
        """
        logger.info(f"Loading documents from {self.data_path}")
        
        try:
            with open(self.data_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Split content into chunks for better retrieval
            text_splitter = CharacterTextSplitter(
                separator="\n\n",
                chunk_size=800,
                chunk_overlap=100,
                length_function=len
            )
            
            chunks = text_splitter.split_text(content)
            
            # Convert chunks to Document objects
            documents = [
                Document(page_content=chunk, metadata={"source": self.data_path})
                for chunk in chunks
            ]
            
            logger.info(f"Loaded {len(documents)} document chunks")
            return documents
            
        except Exception as e:
            logger.error(f"Error loading documents: {str(e)}")
            raise
    
    def create_embeddings(self, documents: List[Document]) -> None:
        """
        Create embeddings and build FAISS vector store.
        
        Args:
            documents: List of Document objects to embed
        """
        logger.info("Creating embeddings and building vector store...")
        
        try:
            # Create FAISS vector store from documents
            self.vectorstore = FAISS.from_documents(
                documents=documents,
                embedding=self.embeddings
            )
            
            # Save the vector store locally
            self.vectorstore.save_local(self.vectorstore_path)
            logger.info(f"Vector store saved to {self.vectorstore_path}")
            
        except Exception as e:
            logger.error(f"Error creating embeddings: {str(e)}")
            raise
    
    def load_vectorstore(self) -> bool:
        """
        Load existing FAISS vector store from disk.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if os.path.exists(self.vectorstore_path):
                logger.info(f"Loading vector store from {self.vectorstore_path}")
                self.vectorstore = FAISS.load_local(
                    self.vectorstore_path,
                    self.embeddings,
                    allow_dangerous_deserialization=True
                )
                return True
            else:
                logger.warning(f"Vector store not found at {self.vectorstore_path}")
                return False
                
        except Exception as e:
            logger.error(f"Error loading vector store: {str(e)}")
            return False
    
    def build_vectorstore(self) -> None:
        """
        Complete pipeline to build vector store from scratch.
        Loads documents, creates embeddings, and saves the index.
        """
        logger.info("Building vector store from scratch...")
        documents = self.load_documents()
        self.create_embeddings(documents)
        self._initialize_qa_chain()
        logger.info("Vector store build complete")
    
    def _initialize_qa_chain(self) -> None:
        """
        Initialize the QA chain with custom prompt template.
        """
        # Custom prompt template for medical assistant
        prompt_template = """You are a knowledgeable, friendly medical assistant. 
Your role is to provide helpful, accurate information about medical topics based on the context provided.

Important guidelines:
- Answer based ONLY on the provided context
- If you're unsure or the context doesn't contain relevant information, clearly state "I don't have enough information to answer that question reliably."
- Be empathetic and professional in your tone
- Do not provide medical advice or diagnoses
- Recommend consulting healthcare professionals for serious concerns

Context:
{context}

Question: {question}

Answer:"""
        
        PROMPT = PromptTemplate(
            template=prompt_template,
            input_variables=["context", "question"]
        )
        
        # Create retrieval QA chain
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.vectorstore.as_retriever(
                search_kwargs={"k": 3}  # Retrieve top 3 most relevant chunks
            ),
            return_source_documents=True,
            chain_type_kwargs={"prompt": PROMPT}
        )
        
        logger.info("QA chain initialized")
    
    def ask_question(self, query: str) -> Dict:
        """
        Process a user query and return an answer with sources.
        
        Args:
            query: User's medical question
            
        Returns:
            Dictionary containing answer, sources, confidence, and latency
        """
        # Check cache first
        if query in self.query_cache:
            logger.info(f"Cache hit for query: {query[:50]}...")
            cached_result = self.query_cache[query].copy()
            cached_result['cached'] = True
            return cached_result
        
        # Ensure QA chain is initialized
        if not self.qa_chain:
            if not self.load_vectorstore():
                raise Exception("Vector store not found. Please build the index first.")
            self._initialize_qa_chain()
        
        # Time the query processing
        start_time = time.time()
        
        try:
            logger.info(f"Processing query: {query[:50]}...")
            
            # Execute the QA chain
            result = self.qa_chain.invoke({"query": query})
            
            # Extract answer and source documents
            answer = result['result']
            source_docs = result.get('source_documents', [])
            
            # Process sources for frontend display
            sources = []
            for i, doc in enumerate(source_docs[:3]):  # Top 3 sources
                sources.append({
                    'id': i + 1,
                    'content': doc.page_content[:200] + "...",  # First 200 chars
                    'full_content': doc.page_content
                })
            
            # Calculate confidence score (simple heuristic based on source similarity)
            confidence = self._calculate_confidence(query, source_docs)
            
            # Calculate latency
            latency = round(time.time() - start_time, 2)
            
            response = {
                'answer': answer,
                'sources': sources,
                'confidence': confidence,
                'latency': latency,
                'cached': False
            }
            
            # Cache the result (LRU cache with max 100 entries)
            if len(self.query_cache) >= 100:
                # Remove oldest entry
                self.query_cache.pop(next(iter(self.query_cache)))
            self.query_cache[query] = response.copy()
            
            logger.info(f"Query processed successfully in {latency}s")
            return response
            
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            raise
    
    def _calculate_confidence(self, query: str, source_docs: List[Document]) -> float:
        """
        Calculate confidence score based on retrieved document relevance.
        
        Args:
            query: User query
            source_docs: Retrieved source documents
            
        Returns:
            Confidence score between 0.0 and 1.0
        """
        if not source_docs:
            return 0.0
        
        # Simple heuristic: more sources = higher confidence (up to 0.95)
        # In production, you'd use actual similarity scores
        base_confidence = min(0.6 + (len(source_docs) * 0.15), 0.95)
        
        # Check if query terms appear in sources
        query_terms = set(query.lower().split())
        source_text = ' '.join([doc.page_content.lower() for doc in source_docs])
        matches = sum(1 for term in query_terms if term in source_text)
        match_ratio = matches / len(query_terms) if query_terms else 0
        
        # Adjust confidence based on term matches
        confidence = base_confidence * (0.7 + 0.3 * match_ratio)
        
        return round(confidence, 2)
    
    def get_stats(self) -> Dict:
        """
        Get statistics about the vector store and cache.
        
        Returns:
            Dictionary with stats
        """
        stats = {
            'vectorstore_exists': self.vectorstore is not None,
            'cache_size': len(self.query_cache),
            'data_path': self.data_path
        }
        
        if self.vectorstore:
            stats['document_count'] = len(self.vectorstore.docstore._dict)
        
        return stats
