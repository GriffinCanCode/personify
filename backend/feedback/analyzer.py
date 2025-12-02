from sqlalchemy.orm import Session
from backend.database.models import Feedback, Message
from typing import List, Dict

class FeedbackAnalyzer:
    """Analyze feedback patterns to improve system"""
    
    @staticmethod
    def analyze_low_rated_responses(db: Session, threshold: int = 3) -> List[Dict]:
        """Get messages with low ratings for analysis"""
        feedbacks = db.query(Feedback).filter(
            Feedback.rating <= threshold
        ).all()
        
        results = []
        for feedback in feedbacks:
            message = db.query(Message).filter(
                Message.id == feedback.message_id
            ).first()
            
            if message:
                results.append({
                    'message_id': message.id,
                    'content': message.content,
                    'rating': feedback.rating,
                    'comment': feedback.comment,
                    'confidence_score': message.confidence_score,
                    'retrieved_chunks': message.retrieved_chunks
                })
        
        return results
    
    @staticmethod
    def identify_improvement_areas(db: Session) -> Dict:
        """Identify areas where the system needs improvement"""
        low_rated = FeedbackAnalyzer.analyze_low_rated_responses(db)
        
        if not low_rated:
            return {'needs_improvement': False}
        
        # Analyze patterns in low-rated responses
        avg_confidence = sum(r['confidence_score'] or 0 for r in low_rated) / len(low_rated)
        
        return {
            'needs_improvement': True,
            'low_rated_count': len(low_rated),
            'avg_confidence_of_low_rated': round(avg_confidence, 2),
            'suggestion': 'Consider uploading more diverse data or rebuilding personality profile'
        }

