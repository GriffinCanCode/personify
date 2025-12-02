from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Virtual Griffin"
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:3001"]
    
    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/personify"
    
    # Vector Store
    CHROMA_PERSIST_DIR: str = "./data/chromadb"
    
    # OpenAI
    OPENAI_API_KEY: str = ""
    # text-embedding-3-large: Best quality (3072 dims, 8191 token limit)
    # Alternative: text-embedding-3-small (1536 dims, faster, cheaper)
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-large"
    OPENAI_CHAT_MODEL: str = "gpt-4o"
    
    # Embedding Settings
    EMBEDDING_BATCH_SIZE: int = 100  # Texts per API call (max 2048)
    EMBEDDING_CACHE_SIZE: int = 1000  # LRU cache for embeddings
    
    # Anthropic
    ANTHROPIC_API_KEY: str = ""
    
    # File Storage
    UPLOAD_DIR: str = "./data/uploads"
    PROCESSED_DIR: str = "./data/processed"
    
    # RAG Configuration (optimized for text-embedding-3-large)
    CHUNK_SIZE: int = 1000  # Tokens per chunk (max 8191 for model)
    CHUNK_OVERLAP: int = 200  # Overlap for context continuity
    RETRIEVAL_K: int = 7  # Top-K results for RAG
    
    # AI Personality Analysis Configuration
    PERSONALITY_ANALYSIS_MODEL: str = "gpt-4o"  # Model for personality analysis
    ANALYSIS_BATCH_SIZE: int = 50  # Max text samples per analysis
    ANALYSIS_MAX_TOKENS: int = 2000  # Max tokens per LLM analysis call
    ENABLE_VALIDATION_PASS: bool = False  # Enable Pass 3 validation (future)
    
    # Logging Configuration
    LOG_LEVEL: str = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    LOG_JSON: bool = False  # JSON logs for production, human-readable for dev
    LOG_FILE: str = ""  # Optional log file path (e.g., "./logs/app.log")
    ENVIRONMENT: str = "development"  # development, staging, production
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()

