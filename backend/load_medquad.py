"""
MedQuAD Data Loader
Converts MedQuAD XML files to text format for the RAG pipeline.
Processes 47,457 medical Q&A pairs from trusted sources.
"""

import os
import xml.etree.ElementTree as ET
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def extract_qa_from_xml(xml_file: str) -> list:
    """
    Extract Q&A pairs from a MedQuAD XML file.
    
    Args:
        xml_file: Path to XML file
        
    Returns:
        List of (question, answer) tuples
    """
    qa_pairs = []
    
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        
        # Find all QAPairs
        for qa_pair in root.findall('.//QAPair'):
            question = qa_pair.find('Question')
            answer = qa_pair.find('Answer')
            
            if question is not None and answer is not None:
                q_text = question.text if question.text else ""
                a_text = answer.text if answer.text else ""
                
                # Clean up text
                q_text = q_text.strip()
                a_text = a_text.strip()
                
                if q_text and a_text:
                    qa_pairs.append((q_text, a_text))
        
    except Exception as e:
        logger.error(f"Error parsing {xml_file}: {str(e)}")
    
    return qa_pairs


def process_medquad_collection(medquad_path: str, output_file: str, max_docs: int = None):
    """
    Process entire MedQuAD collection and create unified text file.
    
    Args:
        medquad_path: Path to MedQuAD directory
        output_file: Output text file path
        max_docs: Maximum number of Q&A pairs to include (None = all)
    """
    logger.info(f"Processing MedQuAD collection from {medquad_path}")
    
    all_qa_pairs = []
    xml_files_found = 0
    
    # Collections in MedQuAD
    collections = [
        '1_CancerGov_QA',
        '2_GARD_QA',
        '3_GHR_QA',
        '4_MPlus_Health_Topics_QA',
        '5_NIDDK_QA',
        '6_NINDS_QA',
        '7_Genetic_QA',
        '8_CDC_QA',
        '9_MPlusDrugs_QA',
        '10_MPlus_ADAM_QA',
        '11_MPlusHerbsSupplements_QA'
    ]
    
    # Process each collection
    for collection in collections:
        collection_path = os.path.join(medquad_path, collection)
        
        if not os.path.exists(collection_path):
            logger.warning(f"Collection not found: {collection_path}")
            continue
        
        logger.info(f"Processing collection: {collection}")
        
        # Find all XML files in collection
        for root_dir, dirs, files in os.walk(collection_path):
            for file in files:
                if file.endswith('.xml'):
                    xml_file = os.path.join(root_dir, file)
                    xml_files_found += 1
                    
                    qa_pairs = extract_qa_from_xml(xml_file)
                    all_qa_pairs.extend(qa_pairs)
                    
                    if xml_files_found % 100 == 0:
                        logger.info(f"Processed {xml_files_found} files, {len(all_qa_pairs)} Q&A pairs extracted")
    
    logger.info(f"Total files processed: {xml_files_found}")
    logger.info(f"Total Q&A pairs extracted: {len(all_qa_pairs)}")
    
    # Limit if specified
    if max_docs and len(all_qa_pairs) > max_docs:
        logger.info(f"Limiting to {max_docs} Q&A pairs")
        all_qa_pairs = all_qa_pairs[:max_docs]
    
    # Write to output file
    logger.info(f"Writing to {output_file}")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("MEDICAL FAQ DATABASE (MedQuAD)\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Source: MedQuAD - Medical Question Answering Dataset\n")
        f.write(f"Total Q&A Pairs: {len(all_qa_pairs)}\n")
        f.write("=" * 80 + "\n\n")
        
        for i, (question, answer) in enumerate(all_qa_pairs, 1):
            f.write(f"Q: {question}\n")
            f.write(f"A: {answer}\n\n")
            
            if i % 1000 == 0:
                logger.info(f"Written {i}/{len(all_qa_pairs)} Q&A pairs")
    
    logger.info(f"✅ Successfully created {output_file}")
    logger.info(f"📊 Total Q&A pairs: {len(all_qa_pairs)}")
    
    return len(all_qa_pairs)


def merge_with_existing(original_file: str, medquad_file: str, merged_file: str):
    """
    Merge existing FAQs with MedQuAD data.
    
    Args:
        original_file: Original medical_faqs.txt
        medquad_file: New MedQuAD data file
        merged_file: Output merged file
    """
    logger.info("Merging original FAQs with MedQuAD data...")
    
    with open(merged_file, 'w', encoding='utf-8') as outfile:
        # Write header
        outfile.write("COMPREHENSIVE MEDICAL FAQ DATABASE\n")
        outfile.write("=" * 80 + "\n\n")
        
        # Copy original file
        if os.path.exists(original_file):
            logger.info(f"Including original FAQs from {original_file}")
            outfile.write("=== ORIGINAL CURATED FAQS ===\n\n")
            with open(original_file, 'r', encoding='utf-8') as infile:
                outfile.write(infile.read())
            outfile.write("\n\n")
        
        # Copy MedQuAD file
        if os.path.exists(medquad_file):
            logger.info(f"Including MedQuAD data from {medquad_file}")
            outfile.write("=== MEDQUAD MEDICAL Q&A DATABASE ===\n\n")
            with open(medquad_file, 'r', encoding='utf-8') as infile:
                # Skip the header from MedQuAD file
                lines = infile.readlines()
                start_idx = 0
                for i, line in enumerate(lines):
                    if line.startswith("Q:"):
                        start_idx = i
                        break
                outfile.writelines(lines[start_idx:])
    
    logger.info(f"✅ Merged file created: {merged_file}")


def main():
    """Main execution function"""
    
    # Paths
    base_dir = Path(__file__).parent
    medquad_path = base_dir / 'data' / 'MedQuAD'
    
    # Output files
    medquad_output = base_dir / 'data' / 'medical_faqs_medquad.txt'
    original_faqs = base_dir / 'data' / 'medical_faqs.txt'
    merged_output = base_dir / 'data' / 'medical_faqs_complete.txt'
    
    print("\n" + "=" * 80)
    print("🏥 MedQuAD Data Loader for MediRAG")
    print("=" * 80 + "\n")
    
    # Check if MedQuAD exists
    if not medquad_path.exists():
        print("❌ MedQuAD directory not found!")
        print(f"Expected location: {medquad_path}")
        print("\nPlease download MedQuAD first:")
        print("cd backend/data")
        print("git clone https://github.com/abachaa/MedQuAD.git")
        return
    
    # Ask user for options
    print("Select an option:")
    print("1. Process ALL MedQuAD data (~47k Q&A pairs) - RECOMMENDED")
    print("2. Process LIMITED data (10k Q&A pairs) - Faster")
    print("3. Process LIMITED data (5k Q&A pairs) - Quick test")
    
    choice = input("\nEnter choice (1-3) [default: 1]: ").strip() or "1"
    
    max_docs = None
    if choice == "2":
        max_docs = 10000
    elif choice == "3":
        max_docs = 5000
    
    # Process MedQuAD
    print("\n" + "=" * 80)
    print("📥 Processing MedQuAD dataset...")
    print("=" * 80 + "\n")
    
    total_pairs = process_medquad_collection(
        str(medquad_path),
        str(medquad_output),
        max_docs=max_docs
    )
    
    # Merge with existing
    print("\n" + "=" * 80)
    print("🔀 Merging with existing FAQs...")
    print("=" * 80 + "\n")
    
    merge_with_existing(
        str(original_faqs),
        str(medquad_output),
        str(merged_output)
    )
    
    # Summary
    print("\n" + "=" * 80)
    print("✅ SUCCESS!")
    print("=" * 80)
    print(f"\n📊 Statistics:")
    print(f"   • MedQuAD Q&A pairs: {total_pairs:,}")
    print(f"   • Output file: {merged_output}")
    print(f"\n📁 Files created:")
    print(f"   • {medquad_output.name} - MedQuAD only")
    print(f"   • {merged_output.name} - Complete database")
    print(f"\n🚀 Next Steps:")
    print(f"   1. Replace backend/data/medical_faqs.txt with {merged_output.name}")
    print(f"   2. Restart the Flask backend")
    print(f"   3. The vector store will rebuild automatically with new data!")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
