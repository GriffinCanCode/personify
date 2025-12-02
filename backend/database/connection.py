from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from backend.config import settings
from backend.logging_config import get_logger

logger = get_logger(__name__)

logger.info("initializing_database_connection", database_url=settings.DATABASE_URL.split('@')[-1])  # Log without credentials

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    logger.debug("database_session_created")
    try:
        yield db
    finally:
        db.close()
        logger.debug("database_session_closed")

