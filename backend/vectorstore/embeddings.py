from openai import OpenAI
from typing import List
from backend.config import settings
import tiktoken

client = OpenAI(api_key=settings.OPENAI_API_KEY)

def get_embedding(text: str, model: str = None) -> List[float]:
    """Generate embedding for a single text"""
    model = model or settings.OPENAI_EMBEDDING_MODEL
    text = text.replace("\n", " ")
    response = client.embeddings.create(input=[text], model=model)
    return response.data[0].embedding

def get_embeddings(texts: List[str], model: str = None) -> List[List[float]]:
    """Generate embeddings for multiple texts"""
    model = model or settings.OPENAI_EMBEDDING_MODEL
    texts = [text.replace("\n", " ") for text in texts]
    response = client.embeddings.create(input=texts, model=model)
    return [item.embedding for item in response.data]

def count_tokens(text: str, model: str = "cl100k_base") -> int:
    """Count tokens in text"""
    encoding = tiktoken.get_encoding(model)
    return len(encoding.encode(text))

def chunk_text(
    text: str,
    chunk_size: int = None,
    chunk_overlap: int = None
) -> List[str]:
    """
    Chunk text into smaller pieces with overlap.
    Uses token-based chunking for more accurate sizing.
    """
    chunk_size = chunk_size or settings.CHUNK_SIZE
    chunk_overlap = chunk_overlap or settings.CHUNK_OVERLAP
    
    encoding = tiktoken.get_encoding("cl100k_base")
    tokens = encoding.encode(text)
    
    chunks = []
    start = 0
    
    while start < len(tokens):
        end = start + chunk_size
        chunk_tokens = tokens[start:end]
        chunk_text = encoding.decode(chunk_tokens)
        chunks.append(chunk_text)
        
        start += chunk_size - chunk_overlap
    
    return chunks

def semantic_chunk_text(text: str, max_chunk_size: int = None) -> List[str]:
    """
    Chunk text based on semantic boundaries (paragraphs/sentences).
    More intelligent than fixed-size chunking.
    """
    max_chunk_size = max_chunk_size or settings.CHUNK_SIZE
    
    # Split by double newlines (paragraphs)
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    
    chunks = []
    current_chunk = []
    current_size = 0
    
    for para in paragraphs:
        para_tokens = count_tokens(para)
        
        if current_size + para_tokens > max_chunk_size and current_chunk:
            # Save current chunk and start new one
            chunks.append('\n\n'.join(current_chunk))
            current_chunk = [para]
            current_size = para_tokens
        else:
            current_chunk.append(para)
            current_size += para_tokens
    
    # Add remaining chunk
    if current_chunk:
        chunks.append('\n\n'.join(current_chunk))
    
    return chunks

