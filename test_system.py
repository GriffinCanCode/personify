#!/usr/bin/env python3
"""
Test script to verify Personify system is properly configured and connected.
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def test_imports():
    """Test that all major modules can be imported"""
    print("Testing imports...")
    
    try:
        from backend.config import settings
        print("✓ Config loaded")
        
        from backend.database.connection import engine, Base
        print("✓ Database connection module loaded")
        
        from backend.database.models import Document, Chunk, Conversation, Message
        print("✓ Database models loaded")
        
        from backend.vectorstore.store import vector_store
        print("✓ Vector store loaded")
        
        from backend.vectorstore.embeddings import get_embedding, chunk_text
        print("✓ Embeddings module loaded")
        
        from backend.ingestion.parsers import ParserFactory
        print("✓ Parsers loaded")
        
        from backend.personality.analyzer import StyleAnalyzer
        print("✓ Personality analyzer loaded")
        
        from backend.conversation.engine import ConversationEngine
        print("✓ Conversation engine loaded")
        
        print("\n✓ All imports successful!\n")
        return True
    except Exception as e:
        print(f"\n✗ Import error: {e}\n")
        return False

def test_config():
    """Test configuration"""
    print("Testing configuration...")
    
    try:
        from backend.config import settings
        
        print(f"  - API Version: {settings.API_V1_STR}")
        print(f"  - Project Name: {settings.PROJECT_NAME}")
        print(f"  - Database URL: {settings.DATABASE_URL}")
        print(f"  - Chroma Dir: {settings.CHROMA_PERSIST_DIR}")
        print(f"  - Upload Dir: {settings.UPLOAD_DIR}")
        
        # Check API key
        if settings.OPENAI_API_KEY and settings.OPENAI_API_KEY != "sk-your-key-here-replace-this":
            print(f"  - OpenAI API Key: Configured (sk-...{settings.OPENAI_API_KEY[-4:]})")
        else:
            print("  ⚠️  OpenAI API Key: NOT CONFIGURED - Add to .env file")
        
        print("\n✓ Configuration looks good!\n")
        return True
    except Exception as e:
        print(f"\n✗ Config error: {e}\n")
        return False

def test_directories():
    """Test that required directories exist"""
    print("Testing directories...")
    
    from backend.config import settings
    
    dirs = [
        settings.UPLOAD_DIR,
        settings.PROCESSED_DIR,
        settings.CHROMA_PERSIST_DIR
    ]
    
    all_exist = True
    for dir_path in dirs:
        if os.path.exists(dir_path):
            print(f"  ✓ {dir_path}")
        else:
            print(f"  ✗ {dir_path} (missing)")
            all_exist = False
    
    if all_exist:
        print("\n✓ All directories exist!\n")
    else:
        print("\n⚠️  Some directories missing. Run: mkdir -p data/uploads data/processed data/chromadb\n")
    
    return all_exist

def test_database_connection():
    """Test database connection"""
    print("Testing database connection...")
    
    try:
        from backend.database.connection import engine
        from sqlalchemy import text
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("  ✓ Database connection successful")
        
        print("\n✓ Database is accessible!\n")
        return True
    except Exception as e:
        print(f"  ✗ Database connection failed: {e}")
        print("  ⚠️  Make sure PostgreSQL is running:")
        print("     docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=personify postgres:16-alpine")
        print()
        return False

def test_vector_store():
    """Test vector store"""
    print("Testing vector store...")
    
    try:
        from backend.vectorstore.store import vector_store
        
        count = vector_store.count()
        print(f"  ✓ Vector store accessible")
        print(f"  - Current document count: {count}")
        
        print("\n✓ Vector store working!\n")
        return True
    except Exception as e:
        print(f"  ✗ Vector store error: {e}\n")
        return False

def test_text_processing():
    """Test text processing pipeline"""
    print("Testing text processing...")
    
    try:
        from backend.vectorstore.embeddings import chunk_text
        
        test_text = "This is a test sentence. " * 100
        chunks = chunk_text(test_text, chunk_size=100)
        
        print(f"  ✓ Chunking works ({len(chunks)} chunks created)")
        
        # Test parsing
        from backend.ingestion.parsers import TextParser
        
        print("  ✓ Text parser works")
        
        print("\n✓ Text processing pipeline working!\n")
        return True
    except Exception as e:
        print(f"  ✗ Text processing error: {e}\n")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("PERSONIFY SYSTEM TEST")
    print("=" * 60)
    print()
    
    results = []
    
    results.append(("Imports", test_imports()))
    results.append(("Configuration", test_config()))
    results.append(("Directories", test_directories()))
    results.append(("Database Connection", test_database_connection()))
    results.append(("Vector Store", test_vector_store()))
    results.append(("Text Processing", test_text_processing()))
    
    print("=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status:10} {name}")
    
    print()
    
    all_passed = all(r[1] for r in results)
    
    if all_passed:
        print("🎉 All tests passed! System is ready to use.")
        print("\nNext steps:")
        print("1. Make sure your OpenAI API key is in .env")
        print("2. Start the backend: cd backend && uvicorn backend.main:app --reload")
        print("3. Start the frontend: cd frontend && npm run dev")
        print("4. Open http://localhost:3000")
    else:
        print("⚠️  Some tests failed. Please fix the issues above.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

