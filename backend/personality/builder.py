from sqlalchemy.orm import Session
from typing import List, Optional, Callable

from backend.database.models import Document, PersonalityProfile as DBPersonalityProfile
from backend.personality.ai_analyzer import AnalysisOrchestrator
from backend.personality.profile import PersonalityProfile
from backend.logging_config import get_logger, PerformanceTimer

logger = get_logger(__name__)


class PersonalityProfileManager:
    """Manage personality profile creation and updates using AI-powered analysis"""
    
    @staticmethod
    def create_from_documents(
        db: Session,
        progress_callback: Optional[Callable[[str, int, int], None]] = None
    ) -> PersonalityProfile:
        """Create personality profile from all documents using AI analysis"""
        logger.info("personality_profile_creation_started")
        
        # Get all processed documents
        documents = db.query(Document).filter(
            Document.processed_at.isnot(None)
        ).all()
        
        if not documents:
            logger.warning("no_processed_documents_for_profile")
            raise ValueError("No processed documents found. Upload and process data first.")
        
        logger.info("documents_retrieved_for_profile", document_count=len(documents))
        
        # Extract text from document chunks
        texts = []
        for doc in documents:
            for chunk in doc.chunks:
                if chunk.content and chunk.content.strip():
                    texts.append(chunk.content)
        
        if not texts:
            raise ValueError("No text content found in documents")
        
        logger.info("text_extracted_for_profile", text_count=len(texts))
        
        # Run AI-powered analysis
        orchestrator = AnalysisOrchestrator()
        
        with PerformanceTimer(logger, "ai_personality_analysis", text_count=len(texts)):
            profile = orchestrator.analyze(texts, progress_callback)
        
        logger.info("personality_profile_analyzed", 
                   version=profile.version,
                   overall_confidence=profile.overall_confidence)
        
        # Save to database
        try:
            db_profile = DBPersonalityProfile(
                version=profile.version,
                profile_data=profile.model_dump(),
                is_active=True
            )
            
            # Deactivate old profiles
            old_count = db.query(DBPersonalityProfile).update({'is_active': False})
            logger.debug("old_profiles_deactivated", count=old_count)
            
            db.add(db_profile)
            db.commit()
            db.refresh(db_profile)
            
            logger.info("personality_profile_saved", 
                       version=profile.version, 
                       profile_id=db_profile.id)
            
            return profile
        except Exception as e:
            logger.error("personality_profile_save_failed", error=str(e), exc_info=True)
            db.rollback()
            raise
    
    @staticmethod
    def get_active_profile(db: Session) -> PersonalityProfile:
        """Get the currently active personality profile"""
        logger.debug("fetching_active_personality_profile")
        
        db_profile = db.query(DBPersonalityProfile).filter(
            DBPersonalityProfile.is_active == True
        ).first()
        
        if not db_profile:
            logger.warning("no_active_personality_profile_found")
            raise ValueError("No active personality profile found. Create one first.")
        
        logger.debug("active_personality_profile_retrieved", 
                    profile_id=db_profile.id, 
                    version=db_profile.version)
        
        return PersonalityProfile(**db_profile.profile_data)
    
    @staticmethod
    def update_profile(db: Session, profile: PersonalityProfile) -> PersonalityProfile:
        """Update existing profile with manual adjustments"""
        logger.info("personality_profile_update_started", current_version=profile.version)
        
        try:
            # Deactivate old profiles
            old_count = db.query(DBPersonalityProfile).update({'is_active': False})
            logger.debug("old_profiles_deactivated", count=old_count)
            
            # Create new version
            new_version = profile.version + 1
            db_profile = DBPersonalityProfile(
                version=new_version,
                profile_data=profile.model_dump(),
                is_active=True
            )
            
            db.add(db_profile)
            db.commit()
            db.refresh(db_profile)
            
            logger.info("personality_profile_updated", 
                       old_version=profile.version, 
                       new_version=new_version)
            
            return PersonalityProfile(**db_profile.profile_data)
        except Exception as e:
            logger.error("personality_profile_update_failed", error=str(e), exc_info=True)
            db.rollback()
            raise
    
    @staticmethod
    def refresh_profile(
        db: Session,
        progress_callback: Optional[Callable[[str, int, int], None]] = None
    ) -> PersonalityProfile:
        """Re-analyze all documents and create a fresh profile"""
        logger.info("personality_profile_refresh_started")
        return PersonalityProfileManager.create_from_documents(db, progress_callback)
