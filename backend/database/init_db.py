from backend.database.connection import engine, Base
from backend.database.models import Document, Chunk, Conversation, Message, Feedback, PersonalityProfile

def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully")

if __name__ == "__main__":
    init_db()

