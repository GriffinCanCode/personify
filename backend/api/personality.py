from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Dict, Any

from backend.database.connection import get_db
from backend.personality.builder import PersonalityProfileManager
from backend.personality.profile import PersonalityProfile

router = APIRouter(prefix="/personality", tags=["personality"])

@router.get("/profile")
async def get_profile(
    db: Session = Depends(get_db)
):
    """Get the active personality profile"""
    try:
        profile = PersonalityProfileManager.get_active_profile(db)
        return profile.model_dump()
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/analyze")
async def analyze_and_create_profile(
    db: Session = Depends(get_db)
):
    """Analyze documents and create personality profile"""
    try:
        profile = PersonalityProfileManager.create_from_documents(db)
        return {
            'status': 'success',
            'message': 'Personality profile created successfully',
            'profile': profile.model_dump()
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class ProfileUpdate(BaseModel):
    profile_data: Dict[str, Any]

@router.put("/profile")
async def update_profile(
    update: ProfileUpdate,
    db: Session = Depends(get_db)
):
    """Update personality profile with manual adjustments"""
    try:
        profile = PersonalityProfile(**update.profile_data)
        updated = PersonalityProfileManager.update_profile(db, profile)
        return {
            'status': 'success',
            'message': 'Profile updated successfully',
            'profile': updated.model_dump()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

