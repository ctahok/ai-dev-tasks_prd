#!/usr/bin/env python3
"""
Test Script for Azerbaijani Court Case Sorter
Tests the system with sample documents and demonstrates functionality
"""

import os
import sys
import logging
from pathlib import Path

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.document_processor import DocumentProcessor
from app.database import DatabaseManager
from app.rag_system import RAGSystem
from app.ai_bot import AIBot

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_document_processing():
    """Test document processing with sample files"""
    print("🧪 Testing Document Processing...")
    print("=" * 50)

    processor = DocumentProcessor()

    # Test with sample PDF files
    sample_files = [
        "sample1.pdf",
        "sample2.pdf",
        "sample3.pdf"
    ]

    for sample_file in sample_files:
        if os.path.exists(sample_file):
            print(f"\n📄 Processing {sample_file}...")

            try:
                doc_data = processor.process_document(sample_file)

                if doc_data:
                    metadata = doc_data.get('metadata', {})
                    print("✅ Successfully processed!")
                    print(f"   📋 Case Number: {metadata.get('case_number', 'N/A')}")
                    print(f"   🏛️  Court: {metadata.get('court_name', 'N/A')}")
                    print(f"   👨‍⚖️ Judge: {metadata.get('judge', 'N/A')}")
                    print(f"   📅 Year: {metadata.get('year', 'N/A')}")
                    print(f"   📝 Decision Type: {metadata.get('decision_type', 'N/A')}")
                    print(f"   📊 Text Length: {len(doc_data.get('text_content', ''))} characters")

                    if metadata.get('parties'):
                        print(f"   👥 Parties: {', '.join(metadata['parties'][:2])}")

                else:
                    print(f"❌ Failed to process {sample_file}")

            except Exception as e:
                print(f"❌ Error processing {sample_file}: {str(e)}")
        else:
            print(f"⚠️  Sample file not found: {sample_file}")

def test_database_operations():
    """Test database operations"""
    print("\n🗄️  Testing Database Operations...")
    print("=" * 50)

    try:
        db_manager = DatabaseManager()

        # Get database statistics
        stats = db_manager.get_stats()
        print("📊 Database Statistics:")
        print(f"   📁 Total Documents: {stats.get('total_documents', 0)}")
        print(f"   ✅ Processed: {stats.get('processed_documents', 0)}")
        print(f"   ❌ Failed: {stats.get('failed_documents', 0)}")

        # Test filter options
        filter_options = db_manager.get_filter_options()
        print("\n🔍 Available Filters:")
        for filter_type, options in filter_options.items():
            if options:
                print(f"   {filter_type}: {len(options)} options")

    except Exception as e:
        print(f"❌ Database test failed: {str(e)}")

def test_rag_system():
    """Test RAG system functionality"""
    print("\n🧠 Testing RAG System...")
    print("=" * 50)

    try:
        rag_system = RAGSystem()

        # Get RAG system statistics
        stats = rag_system.get_stats()
        print("📊 RAG System Statistics:")
        print(f"   📁 Total Documents: {stats.get('total_documents', 0)}")
        print(f"   🤖 Model: {stats.get('model_name', 'N/A')}")

        # Test search functionality
        test_queries = [
            "Hakim Fikrət Hüseynov",
            "Ağdam rayon məhkəməsi",
            "2025-ci il qərarları"
        ]

        print("\n🔍 Testing Search Queries:")
        for query in test_queries:
            print(f"\n   Query: '{query}'")
            try:
                results = rag_system.search_documents(query, n_results=3)
                print(f"   Results: {len(results)} found")
                if results:
                    for i, result in enumerate(results[:2], 1):
                        metadata = result.get('metadata', {})
                        print(f"      {i}. {metadata.get('case_number', 'Unknown')} - {metadata.get('judge', 'Unknown')}")
            except Exception as e:
                print(f"      Error: {str(e)}")

    except Exception as e:
        print(f"❌ RAG system test failed: {str(e)}")

def test_ai_bot():
    """Test AI bot functionality"""
    print("\n🤖 Testing AI Bot...")
    print("=" * 50)

    try:
        ai_bot = AIBot()

        # Test chat functionality
        test_messages = [
            "Salam",
            "Hakim Fikrət Hüseynov haqqında məlumat verin",
            "Ağdam rayon məhkəməsinin qərarları"
        ]

        print("💬 Testing Chat Messages:")
        for message in test_messages:
            print(f"\n   User: {message}")
            try:
                response = ai_bot.chat(message)
                print(f"   Bot: {response}")
            except Exception as e:
                print(f"   Error: {str(e)}")

        # Test query analysis
        print("\n🔍 Testing Query Analysis:")
        test_queries = [
            "Hakim Niftəliyev Mahir Şamiloğlunun qərarları",
            "2025-ci il mülki işlər"
        ]

        for query in test_queries:
            print(f"\n   Query: '{query}'")
            try:
                validation = ai_bot.validate_query(query)
                print(f"   Valid: {validation.get('is_valid', False)}")
                print(f"   Has Judge: {validation.get('has_judge', False)}")
                print(f"   Has Court: {validation.get('has_court', False)}")
                print(f"   Has Year: {validation.get('has_year', False)}")
            except Exception as e:
                print(f"   Error: {str(e)}")

    except Exception as e:
        print(f"❌ AI bot test failed: {str(e)}")

def test_full_pipeline():
    """Test the complete pipeline with sample documents"""
    print("\n🔄 Testing Full Pipeline...")
    print("=" * 50)

    try:
        # Initialize components
        processor = DocumentProcessor()
        db_manager = DatabaseManager()
        rag_system = RAGSystem()

        # Process sample documents
        sample_files = ["sample1.pdf", "sample2.pdf", "sample3.pdf"]
        processed_count = 0

        for sample_file in sample_files:
            if os.path.exists(sample_file):
                print(f"\n📄 Processing {sample_file}...")

                doc_data = processor.process_document(sample_file)
                if doc_data:
                    # Store in database
                    doc_id = db_manager.store_document(doc_data)
                    print(f"   ✅ Stored with ID: {doc_id}")

                    # Add to RAG system
                    rag_system.add_document(doc_id, doc_data)
                    print("   ✅ Added to RAG system")
                    processed_count += 1

        print(f"\n📊 Pipeline completed: {processed_count}/{len(sample_files)} documents processed")

        # Test search after processing
        if processed_count > 0:
            print("\n🔍 Testing search after processing:")
            test_query = "Ağdam rayon məhkəməsi"
            results = rag_system.search_documents(test_query, n_results=5)
            print(f"   Search for '{test_query}': {len(results)} results found")

    except Exception as e:
        print(f"❌ Full pipeline test failed: {str(e)}")

def main():
    """Main test function"""
    print("🇦🇿 Azerbaijani Court Case Sorter - System Test")
    print("=" * 60)
    print("This script tests all components of the court case sorter system")
    print("Make sure sample PDF files are in the same directory as this script")
    print("=" * 60)

    try:
        # Run all tests
        test_document_processing()
        test_database_operations()
        test_rag_system()
        test_ai_bot()
        test_full_pipeline()

        print("\n" + "=" * 60)
        print("✅ All tests completed!")
        print("🎉 The Azerbaijani Court Case Sorter system is ready to use!")
        print("\nTo start the web application, run:")
        print("   python main.py")
        print("\nThen open your browser and navigate to:")
        print("   http://localhost:8000")
        print("\nDefault login credentials:")
        print("   Username: admin")
        print("   Password: admin123")

    except KeyboardInterrupt:
        print("\n\n⏹️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test suite failed with error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
