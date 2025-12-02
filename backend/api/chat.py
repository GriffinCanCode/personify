from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List

from backend.database.connection import get_db
from backend.database.models import Conversation, Message
from backend.conversation.engine import ConversationEngine
from backend.logging_config import get_logger, PerformanceTimer

logger = get_logger(__name__)
router = APIRouter(prefix="/chat", tags=["chat"])

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[int] = None

class ChatResponse(BaseModel):
    response: str
    confidence_score: float
    style_match: float
    conversation_id: int
    message_id: int
    validation_issues: List[str] = []

@router.post("/message", response_model=ChatResponse)
async def send_message(
    request: ChatRequest,
    db: Session = Depends(get_db)
):
    """Send a message to Virtual Griffin"""
    logger.info(
        "chat_message_received",
        message_length=len(request.message),
        conversation_id=request.conversation_id
    )
    
    engine = ConversationEngine(db)
    
    try:
        with PerformanceTimer(logger, "chat_message_processing", conversation_id=request.conversation_id):
            result = engine.chat(
                query=request.message,
                conversation_id=request.conversation_id
            )
        
        if 'error' in result:
            logger.warning("chat_error", error=result.get('error'), response=result.get('response'))
            raise HTTPException(status_code=400, detail=result.get('response'))
        
        logger.info(
            "chat_response_generated",
            conversation_id=result['conversation_id'],
            message_id=result['message_id'],
            confidence_score=result['confidence_score']
        )
        
        return ChatResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        logger.error("chat_processing_error", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/conversations")
async def get_conversations(
    db: Session = Depends(get_db)
):
    """Get all conversations"""
    logger.debug("fetching_all_conversations")
    
    try:
        conversations = db.query(Conversation).order_by(
            Conversation.updated_at.desc()
        ).all()
        
        logger.info("conversations_fetched", count=len(conversations))
        
        return [
            {
                'id': conv.id,
                'title': conv.title,
                'created_at': conv.created_at.isoformat(),
                'updated_at': conv.updated_at.isoformat() if conv.updated_at else None,
                'message_count': len(conv.messages)
            }
            for conv in conversations
        ]
    except Exception as e:
        logger.error("conversation_fetch_error", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/conversations/{conversation_id}")
async def get_conversation(
    conversation_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific conversation with all messages"""
    logger.debug("fetching_conversation", conversation_id=conversation_id)
    
    try:
        conversation = db.query(Conversation).filter(
            Conversation.id == conversation_id
        ).first()
        
        if not conversation:
            logger.warning("conversation_not_found", conversation_id=conversation_id)
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        logger.info(
            "conversation_fetched",
            conversation_id=conversation_id,
            message_count=len(conversation.messages)
        )
        
        return {
            'id': conversation.id,
            'title': conversation.title,
            'created_at': conversation.created_at.isoformat(),
            'messages': [
                {
                    'id': msg.id,
                    'role': msg.role,
                    'content': msg.content,
                    'confidence_score': msg.confidence_score,
                    'created_at': msg.created_at.isoformat()
                }
                for msg in conversation.messages
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "conversation_fetch_error",
            conversation_id=conversation_id,
            error=str(e),
            exc_info=True
        )
        raise HTTPException(status_code=500, detail=str(e))

