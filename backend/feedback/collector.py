from sqlalchemy.orm import Session
from backend.database.models import Feedback, Message
from typing import Optional

class FeedbackCollector:
    """Collect and manage user feedback on responses"""
    
    @staticmethod
    def submit_feedback(
        db: Session,
        message_id: int,
        rating: int,
        comment: Optional[str] = None
    ) -> Feedback:
        """Submit feedback for a message"""
        # Check if feedback already exists
        existing = db.query(Feedback).filter(
            Feedback.message_id == message_id
        ).first()
        
        if existing:
            existing.rating = rating
            existing.comment = comment
            db.commit()
            db.refresh(existing)
            return existing
        
        feedback = Feedback(
            message_id=message_id,
            rating=rating,
            comment=comment
        )
        db.add(feedback)
        db.commit()
        db.refresh(feedback)
        
        return feedback
    
    @staticmethod
    def get_feedback_stats(db: Session) -> dict:
        """Get aggregated feedback statistics"""
        feedbacks = db.query(Feedback).all()
        
        if not feedbacks:
            return {
                'total': 0,
                'average_rating': 0,
                'distribution': {}
            }
        
        total = len(feedbacks)
        avg_rating = sum(f.rating for f in feedbacks) / total
        
        distribution = {}
        for i in range(1, 6):
            distribution[i] = sum(1 for f in feedbacks if f.rating == i)
        
        return {
            'total': total,
            'average_rating': round(avg_rating, 2),
            'distribution': distribution
        }

