"""
Flask Backend for Medical FAQ Bot
Provides REST API endpoints for chat interface and vector store management.
"""

import os
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from rag_pipeline import MedicalRAGPipeline

# Load environment variables from .env file in the backend directory
env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path=env_path)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

# Configuration
DATA_PATH = os.path.join(os.path.dirname(__file__), 'data', 'medical_faqs.txt')
VECTORSTORE_PATH = os.path.join(os.path.dirname(__file__), 'vectorstore')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# Validate API key
if not GEMINI_API_KEY:
    logger.error("GEMINI_API_KEY not found in environment variables")
    raise ValueError("GEMINI_API_KEY must be set in .env file")

# Initialize RAG pipeline
rag_pipeline = None

def initialize_pipeline():
    """
    Initialize the RAG pipeline on server startup.
    Loads existing vector store or builds a new one if needed.
    """
    global rag_pipeline
    
    try:
        logger.info("Initializing RAG pipeline with Google Gemini 2.0 Flash...")
        rag_pipeline = MedicalRAGPipeline(
            data_path=DATA_PATH,
            vectorstore_path=VECTORSTORE_PATH,
            gemini_api_key=GEMINI_API_KEY
        )
        
        # Try to load existing vector store
        if not rag_pipeline.load_vectorstore():
            logger.info("Vector store not found, building from scratch...")
            rag_pipeline.build_vectorstore()
        else:
            # Initialize QA chain after loading
            rag_pipeline._initialize_qa_chain()
            logger.info("Vector store loaded successfully")
        
        logger.info("RAG pipeline initialized successfully")
        return True
        
    except Exception as e:
        logger.error(f"Failed to initialize RAG pipeline: {str(e)}")
        return False


@app.route('/', methods=['GET'])
def health_check():
    """
    Health check endpoint.
    Returns server status and pipeline information.
    """
    if rag_pipeline:
        stats = rag_pipeline.get_stats()
        return jsonify({
            'status': 'running',
            'message': 'Medical FAQ Bot API is operational',
            'stats': stats
        }), 200
    else:
        return jsonify({
            'status': 'error',
            'message': 'RAG pipeline not initialized'
        }), 503


@app.route('/ask', methods=['POST'])
def ask_question():
    """
    Main endpoint for processing user queries.
    
    Request JSON:
        {
            "query": "What are the symptoms of diabetes?"
        }
    
    Response JSON:
        {
            "answer": "...",
            "sources": [...],
            "confidence": 0.85,
            "latency": 1.3,
            "cached": false
        }
    """
    try:
        # Validate request
        if not request.is_json:
            return jsonify({
                'error': 'Request must be JSON'
            }), 400
        
        data = request.get_json()
        query = data.get('query', '').strip()
        
        # Validate query
        if not query:
            return jsonify({
                'error': 'Query field is required and cannot be empty'
            }), 400
        
        if len(query) > 500:
            return jsonify({
                'error': 'Query is too long (max 500 characters)'
            }), 400
        
        # Sanitize input (basic security)
        query = query.replace('<', '').replace('>', '')
        
        # Check if pipeline is initialized
        if not rag_pipeline:
            return jsonify({
                'error': 'RAG pipeline not initialized'
            }), 503
        
        # Log query (for analytics)
        logger.info(f"Received query: {query[:100]}...")
        
        # Process query through RAG pipeline
        result = rag_pipeline.ask_question(query)
        
        # Check confidence threshold
        if result['confidence'] < 0.4:
            result['answer'] = "Sorry, I couldn't find reliable information to answer your question. Please try rephrasing or ask about a different medical topic."
            result['low_confidence'] = True
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        return jsonify({
            'error': 'An error occurred while processing your query',
            'details': str(e)
        }), 500


@app.route('/build_index', methods=['POST'])
def build_index():
    """
    Endpoint to rebuild the vector store index.
    Useful when medical FAQ data is updated.
    
    Optional POST body:
        {
            "password": "admin_password"  # For security
        }
    """
    try:
        # Optional: Add authentication
        # data = request.get_json() or {}
        # password = data.get('password', '')
        # if password != os.getenv('ADMIN_PASSWORD'):
        #     return jsonify({'error': 'Unauthorized'}), 401
        
        logger.info("Rebuilding vector store index...")
        
        if not rag_pipeline:
            return jsonify({
                'error': 'RAG pipeline not initialized'
            }), 503
        
        # Rebuild the vector store
        rag_pipeline.build_vectorstore()
        
        return jsonify({
            'message': 'Vector store rebuilt successfully',
            'stats': rag_pipeline.get_stats()
        }), 200
        
    except Exception as e:
        logger.error(f"Error rebuilding index: {str(e)}")
        return jsonify({
            'error': 'Failed to rebuild index',
            'details': str(e)
        }), 500


@app.route('/stats', methods=['GET'])
def get_stats():
    """
    Get statistics about the RAG pipeline.
    """
    try:
        if not rag_pipeline:
            return jsonify({
                'error': 'RAG pipeline not initialized'
            }), 503
        
        stats = rag_pipeline.get_stats()
        return jsonify(stats), 200
        
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        return jsonify({
            'error': 'Failed to retrieve stats',
            'details': str(e)
        }), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'error': 'Endpoint not found'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({
        'error': 'Internal server error'
    }), 500


if __name__ == '__main__':
    # Initialize pipeline on startup
    if initialize_pipeline():
        logger.info("Starting Flask server...")
        # Run the server
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=True  # Set to False in production
        )
    else:
        logger.error("Failed to start server due to initialization errors")
