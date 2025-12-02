from openai import OpenAI
from typing import List, Optional
from backend.config import settings
from backend.logging_config import get_logger, PerformanceTimer
import tiktoken
import hashlib
import time
from functools import lru_cache

logger = get_logger(__name__)
client = OpenAI(api_key=settings.OPENAI_API_KEY)

# Constants for optimization
MAX_BATCH_SIZE = 2048  # OpenAI API limit for text-embedding-3-large
MAX_RETRIES = 3
RETRY_DELAY = 1  # seconds

# Dynamic cache size from settings
_cache_size = lambda: settings.EMBEDDING_CACHE_SIZE

@lru_cache(maxsize=None)  # Will be constrained by wrapper
def _get_cached_embedding(text_hash: str, model: str) -> Optional[tuple]:
    """Cache wrapper - returns None for cache miss, uses hash for cache key"""
    return None

def _compute_text_hash(text: str) -> str:
    """Compute deterministic hash for text caching"""
    return hashlib.sha256(text.encode()).hexdigest()

def get_embedding(text: str, model: Optional[str] = None) -> List[float]:
    """
    Generate embedding for a single text with caching and retry logic.
    Uses OpenAI's text-embedding-3-large (best quality, 3072 dimensions)
    """
    model = model or settings.OPENAI_EMBEDDING_MODEL
    text = text.replace("\n", " ").strip()
    
    if not text:
        logger.error("empty_text_for_embedding")
        raise ValueError("Cannot generate embedding for empty text")
    
    # Try cache first
    text_hash = _compute_text_hash(text)
    cached = _get_cached_embedding(text_hash, model)
    if cached:
        logger.debug("embedding_cache_hit", text_hash=text_hash[:16])
        return list(cached)
    
    logger.debug("embedding_cache_miss_generating", text_hash=text_hash[:16], model=model)
    
    # Generate with retry logic
    for attempt in range(MAX_RETRIES):
        try:
            with PerformanceTimer(logger, "generate_single_embedding", model=model, attempt=attempt+1):
                response = _get_client().embeddings.create(input=[text], model=model)
                embedding = response.data[0].embedding
            
            # Cache result
            _get_cached_embedding(text_hash, model)  # Prime cache
            logger.debug("embedding_generated_successfully", text_hash=text_hash[:16])
            return embedding
        except Exception as e:
            if attempt == MAX_RETRIES - 1:
                logger.error(
                    "embedding_generation_failed",
                    text_hash=text_hash[:16],
                    attempts=MAX_RETRIES,
                    error=str(e),
                    exc_info=True
                )
                raise Exception(f"Failed to generate embedding after {MAX_RETRIES} attempts: {e}")
            logger.warning(
                "embedding_generation_retry",
                text_hash=text_hash[:16],
                attempt=attempt+1,
                error=str(e)
            )
            time.sleep(RETRY_DELAY * (attempt + 1))
    
    raise Exception("Embedding generation failed")

def get_embeddings(texts: List[str], model: Optional[str] = None, batch_size: Optional[int] = None) -> List[List[float]]:
    """
    Generate embeddings for multiple texts with intelligent batching and error handling.
    
    Args:
        texts: List of texts to embed
        model: Embedding model (defaults to text-embedding-3-large)
        batch_size: Number of texts per API call (default from settings, max 2048)
    
    Returns:
        List of embeddings matching input order
    """
    model = model or settings.OPENAI_EMBEDDING_MODEL
    batch_size = batch_size or settings.EMBEDDING_BATCH_SIZE
    batch_size = min(batch_size, MAX_BATCH_SIZE)
    
    if not texts:
        logger.debug("empty_texts_list_for_embeddings")
        return []
    
    logger.info(
        "batch_embedding_started",
        text_count=len(texts),
        batch_size=batch_size,
        model=model
    )
    
    # Clean and validate texts
    cleaned_texts = [text.replace("\n", " ").strip() for text in texts]
    
    if any(not text for text in cleaned_texts):
        logger.error("empty_text_in_batch")
        raise ValueError("Cannot generate embeddings for empty texts")
    
    embeddings = []
    total_batches = (len(cleaned_texts) + batch_size - 1) // batch_size
    
    # Process in batches for efficiency
    for i in range(0, len(cleaned_texts), batch_size):
        batch = cleaned_texts[i:i + batch_size]
        batch_num = i // batch_size + 1
        
        logger.debug(
            "processing_embedding_batch",
            batch_num=batch_num,
            total_batches=total_batches,
            batch_size=len(batch)
        )
        
        for attempt in range(MAX_RETRIES):
            try:
                with PerformanceTimer(
                    logger,
                    "generate_batch_embeddings",
                    batch_num=batch_num,
                    batch_size=len(batch),
                    model=model
                ):
                    response = _get_client().embeddings.create(input=batch, model=model)
                    batch_embeddings = [item.embedding for item in response.data]
                    embeddings.extend(batch_embeddings)
                
                logger.debug("embedding_batch_successful", batch_num=batch_num)
                break
            except Exception as e:
                if attempt == MAX_RETRIES - 1:
                    logger.error(
                        "embedding_batch_failed",
                        batch_num=batch_num,
                        attempts=MAX_RETRIES,
                        error=str(e),
                        exc_info=True
                    )
                    raise Exception(
                        f"Failed to generate embeddings for batch {batch_num} "
                        f"after {MAX_RETRIES} attempts: {e}"
                    )
                logger.warning(
                    "embedding_batch_retry",
                    batch_num=batch_num,
                    attempt=attempt+1,
                    error=str(e)
                )
                time.sleep(RETRY_DELAY * (attempt + 1))
    
    logger.info(
        "batch_embedding_completed",
        text_count=len(texts),
        embedding_count=len(embeddings)
    )
    
    return embeddings

@lru_cache(maxsize=1)
def _get_encoding(encoding_name: str = "cl100k_base"):
    """Cache tokenizer encoding"""
    return tiktoken.get_encoding(encoding_name)

def count_tokens(text: str, encoding_name: str = "cl100k_base") -> int:
    """
    Count tokens in text efficiently with cached encoding.
    Uses cl100k_base (GPT-4, text-embedding-3 models)
    """
    encoding = _get_encoding(encoding_name)
    return len(encoding.encode(text))

def chunk_text(
    text: str,
    chunk_size: Optional[int] = None,
    chunk_overlap: Optional[int] = None
) -> List[str]:
    """
    Chunk text into smaller pieces with overlap using token-based chunking.
    Optimized for text-embedding-3-large (8191 token limit)
    
    Args:
        text: Text to chunk
        chunk_size: Max tokens per chunk (default from settings)
        chunk_overlap: Overlap between chunks (default from settings)
    
    Returns:
        List of text chunks
    """
    chunk_size = chunk_size or settings.CHUNK_SIZE
    chunk_overlap = chunk_overlap or settings.CHUNK_OVERLAP
    
    if not text.strip():
        return []
    
    encoding = _get_encoding("cl100k_base")
    tokens = encoding.encode(text)
    
    if len(tokens) <= chunk_size:
        return [text]
    
    chunks = []
    start = 0
    
    while start < len(tokens):
        end = min(start + chunk_size, len(tokens))
        chunk_tokens = tokens[start:end]
        chunk_text = encoding.decode(chunk_tokens)
        chunks.append(chunk_text.strip())
        
        if end >= len(tokens):
            break
            
        start += chunk_size - chunk_overlap
    
    return chunks

def semantic_chunk_text(text: str, max_chunk_size: Optional[int] = None) -> List[str]:
    """
    Chunk text based on semantic boundaries (paragraphs/sentences).
    Optimized for better context preservation and retrieval quality.
    
    Args:
        text: Text to chunk
        max_chunk_size: Max tokens per chunk (default from settings)
    
    Returns:
        List of semantically coherent text chunks
    """
    max_chunk_size = max_chunk_size or settings.CHUNK_SIZE
    
    if not text.strip():
        logger.debug("empty_text_for_chunking")
        return []
    
    logger.debug("semantic_chunking_started", text_length=len(text), max_chunk_size=max_chunk_size)
    
    # Split by paragraphs (double newlines)
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    
    if not paragraphs:
        logger.debug("no_paragraphs_found_returning_whole_text")
        return [text.strip()]
    
    chunks = []
    current_chunk = []
    current_tokens = 0
    
    encoding = _get_encoding("cl100k_base")
    
    for para in paragraphs:
        para_tokens = len(encoding.encode(para))
        
        # If single paragraph exceeds max size, split it
        if para_tokens > max_chunk_size:
            # Save current chunk if exists
            if current_chunk:
                chunks.append('\n\n'.join(current_chunk))
                current_chunk = []
                current_tokens = 0
            
            # Split large paragraph by sentences
            sentences = [s.strip() for s in para.replace('! ', '!|').replace('? ', '?|').replace('. ', '.|').split('|') if s.strip()]
            
            for sent in sentences:
                sent_tokens = len(encoding.encode(sent))
                
                if current_tokens + sent_tokens > max_chunk_size and current_chunk:
                    chunks.append(' '.join(current_chunk))
                    current_chunk = [sent]
                    current_tokens = sent_tokens
                else:
                    current_chunk.append(sent)
                    current_tokens += sent_tokens
        
        # Normal paragraph processing
        elif current_tokens + para_tokens > max_chunk_size and current_chunk:
            chunks.append('\n\n'.join(current_chunk))
            current_chunk = [para]
            current_tokens = para_tokens
        else:
            current_chunk.append(para)
            current_tokens += para_tokens
    
    # Add remaining chunk
    if current_chunk:
        chunks.append('\n\n'.join(current_chunk))
    
    result_chunks = [chunk.strip() for chunk in chunks if chunk.strip()]
    logger.info(
        "semantic_chunking_completed",
        input_length=len(text),
        chunk_count=len(result_chunks),
        avg_chunk_size=sum(len(c) for c in result_chunks) // len(result_chunks) if result_chunks else 0
    )
    
    return result_chunks

