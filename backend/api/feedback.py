from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from backend.database.connection import get_db
from backend.database.models import Feedback, Message
from backend.logging_config import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/feedback", tags=["feedback"])

class FeedbackRequest(BaseModel):
    message_id: int
    rating: int  # 1-5
    comment: Optional[str] = None

@router.post("")
async def submit_feedback(
    request: FeedbackRequest,
    db: Session = Depends(get_db)
):
    """Submit feedback on a message"""
    logger.info("feedback_submission", message_id=request.message_id, rating=request.rating)
    
    try:
        # Validate message exists
        message = db.query(Message).filter(Message.id == request.message_id).first()
        if not message:
            logger.warning("feedback_message_not_found", message_id=request.message_id)
            raise HTTPException(status_code=404, detail="Message not found")
        
        # Validate rating
        if request.rating < 1 or request.rating > 5:
            logger.warning("invalid_feedback_rating", rating=request.rating)
            raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
        
        # Check if feedback already exists
        existing = db.query(Feedback).filter(
            Feedback.message_id == request.message_id
        ).first()
        
        if existing:
            # Update existing feedback
            logger.info("updating_existing_feedback", message_id=request.message_id, old_rating=existing.rating, new_rating=request.rating)
            existing.rating = request.rating
            existing.comment = request.comment
        else:
            # Create new feedback
            logger.info("creating_new_feedback", message_id=request.message_id)
            feedback = Feedback(
                message_id=request.message_id,
                rating=request.rating,
                comment=request.comment
            )
            db.add(feedback)
        
        db.commit()
        
        logger.info("feedback_submitted_successfully", message_id=request.message_id, rating=request.rating)
        
        return {
            'status': 'success',
            'message': 'Feedback submitted successfully'
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error("feedback_submission_error", message_id=request.message_id, error=str(e), exc_info=True)
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
async def get_feedback_stats(
    db: Session = Depends(get_db)
):
    """Get feedback statistics"""
    logger.debug("fetching_feedback_stats")
    
    try:
        feedback_records = db.query(Feedback).all()
        
        if not feedback_records:
            logger.info("no_feedback_records_found")
            return {
                'total_feedback': 0,
                'average_rating': 0,
                'rating_distribution': {}
            }
        
        total = len(feedback_records)
        avg_rating = sum(f.rating for f in feedback_records) / total
        
        rating_dist = {}
        for i in range(1, 6):
            count = sum(1 for f in feedback_records if f.rating == i)
            rating_dist[i] = count
        
        logger.info("feedback_stats_calculated", total=total, average_rating=avg_rating)
        
        return {
            'total_feedback': total,
            'average_rating': round(avg_rating, 2),
            'rating_distribution': rating_dist
        }
    except Exception as e:
        logger.error("feedback_stats_error", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

