from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from backend.database.connection import get_db
from backend.database.models import Feedback, Message

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
    # Validate message exists
    message = db.query(Message).filter(Message.id == request.message_id).first()
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    # Validate rating
    if request.rating < 1 or request.rating > 5:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
    
    # Check if feedback already exists
    existing = db.query(Feedback).filter(
        Feedback.message_id == request.message_id
    ).first()
    
    if existing:
        # Update existing feedback
        existing.rating = request.rating
        existing.comment = request.comment
    else:
        # Create new feedback
        feedback = Feedback(
            message_id=request.message_id,
            rating=request.rating,
            comment=request.comment
        )
        db.add(feedback)
    
    db.commit()
    
    return {
        'status': 'success',
        'message': 'Feedback submitted successfully'
    }

@router.get("/stats")
async def get_feedback_stats(
    db: Session = Depends(get_db)
):
    """Get feedback statistics"""
    feedback_records = db.query(Feedback).all()
    
    if not feedback_records:
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
    
    return {
        'total_feedback': total,
        'average_rating': round(avg_rating, 2),
        'rating_distribution': rating_dist
    }

