from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Dict, Any

from backend.database.connection import get_db
from backend.personality.builder import PersonalityProfileManager
from backend.personality.profile import PersonalityProfile
from backend.logging_config import get_logger, PerformanceTimer

logger = get_logger(__name__)
router = APIRouter(prefix="/personality", tags=["personality"])

@router.get("/profile")
async def get_profile(
    db: Session = Depends(get_db)
):
    """Get the active personality profile"""
    logger.debug("fetching_personality_profile")
    
    try:
        profile = PersonalityProfileManager.get_active_profile(db)
        logger.info("personality_profile_retrieved", profile_version=profile.version if hasattr(profile, 'version') else None)
        return profile.model_dump()
    except ValueError as e:
        logger.warning("personality_profile_not_found", error=str(e))
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error("personality_profile_fetch_error", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze")
async def analyze_and_create_profile(
    db: Session = Depends(get_db)
):
    """Analyze documents and create personality profile"""
    logger.info("personality_analysis_started")
    
    try:
        with PerformanceTimer(logger, "personality_analysis"):
            profile = PersonalityProfileManager.create_from_documents(db)
        
        logger.info("personality_profile_created", profile_version=profile.version if hasattr(profile, 'version') else None)
        
        return {
            'status': 'success',
            'message': 'Personality profile created successfully',
            'profile': profile.model_dump()
        }
    except ValueError as e:
        logger.warning("personality_analysis_validation_error", error=str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("personality_analysis_error", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

class ProfileUpdate(BaseModel):
    profile_data: Dict[str, Any]

@router.put("/profile")
async def update_profile(
    update: ProfileUpdate,
    db: Session = Depends(get_db)
):
    """Update personality profile with manual adjustments"""
    logger.info("personality_profile_update_started")
    
    try:
        profile = PersonalityProfile(**update.profile_data)
        updated = PersonalityProfileManager.update_profile(db, profile)
        
        logger.info("personality_profile_updated", profile_version=updated.version if hasattr(updated, 'version') else None)
        
        return {
            'status': 'success',
            'message': 'Profile updated successfully',
            'profile': updated.model_dump()
        }
    except Exception as e:
        logger.error("personality_profile_update_error", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

