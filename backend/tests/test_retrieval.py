import pytest
from backend.vectorstore.embeddings import semantic_chunk_text, chunk_text, count_tokens

def test_chunk_text():
    text = "This is a test. " * 200  # Long text
    chunks = chunk_text(text, chunk_size=100, chunk_overlap=20)
    
    assert len(chunks) > 1
    assert all(isinstance(chunk, str) for chunk in chunks)

def test_semantic_chunk_text():
    text = """
    This is the first paragraph. It has multiple sentences.
    
    This is the second paragraph. It's separate from the first.
    
    And here is a third paragraph.
    """
    
    chunks = semantic_chunk_text(text, max_chunk_size=500)
    
    assert len(chunks) >= 1
    assert all(isinstance(chunk, str) for chunk in chunks)

def test_count_tokens():
    text = "This is a simple test sentence."
    token_count = count_tokens(text)
    
    assert token_count > 0
    assert isinstance(token_count, int)
    assert token_count < len(text)  # Tokens should be less than characters

