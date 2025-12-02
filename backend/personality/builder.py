from sqlalchemy.orm import Session
from typing import List
from backend.database.models import Document, PersonalityProfile as DBPersonalityProfile
from backend.personality.analyzer import ProfileBuilder as AnalyzerProfileBuilder
from backend.personality.profile import PersonalityProfile

class PersonalityProfileManager:
    """Manage personality profile creation and updates"""
    
    @staticmethod
    def create_from_documents(db: Session) -> PersonalityProfile:
        """Create personality profile from all documents in database"""
        # Get all processed documents
        documents = db.query(Document).filter(
            Document.processed_at.isnot(None)
        ).all()
        
        if not documents:
            raise ValueError("No processed documents found. Upload and process data first.")
        
        # Extract text from documents
        texts = []
        for doc in documents:
            # Get chunks from document
            for chunk in doc.chunks:
                if chunk.content:
                    texts.append(chunk.content)
        
        # Build profile
        profile = AnalyzerProfileBuilder.build_profile(texts)
        
        # Save to database
        db_profile = DBPersonalityProfile(
            version=profile.version,
            profile_data=profile.model_dump(),
            is_active=True
        )
        
        # Deactivate old profiles
        db.query(DBPersonalityProfile).update({'is_active': False})
        
        db.add(db_profile)
        db.commit()
        db.refresh(db_profile)
        
        return profile
    
    @staticmethod
    def get_active_profile(db: Session) -> PersonalityProfile:
        """Get the currently active personality profile"""
        db_profile = db.query(DBPersonalityProfile).filter(
            DBPersonalityProfile.is_active == True
        ).first()
        
        if not db_profile:
            raise ValueError("No active personality profile found. Create one first.")
        
        return PersonalityProfile(**db_profile.profile_data)
    
    @staticmethod
    def update_profile(db: Session, profile: PersonalityProfile) -> PersonalityProfile:
        """Update existing profile with manual adjustments"""
        # Deactivate old profiles
        db.query(DBPersonalityProfile).update({'is_active': False})
        
        # Create new version
        db_profile = DBPersonalityProfile(
            version=profile.version + 1,
            profile_data=profile.model_dump(),
            is_active=True
        )
        
        db.add(db_profile)
        db.commit()
        db.refresh(db_profile)
        
        return PersonalityProfile(**db_profile.profile_data)

