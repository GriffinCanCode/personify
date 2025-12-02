from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List

from backend.database.connection import get_db
from backend.database.models import Conversation, Message
from backend.conversation.engine import ConversationEngine

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
    engine = ConversationEngine(db)
    
    try:
        result = engine.chat(
            query=request.message,
            conversation_id=request.conversation_id
        )
        
        if 'error' in result:
            raise HTTPException(status_code=400, detail=result.get('response'))
        
        return ChatResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/conversations")
async def get_conversations(
    db: Session = Depends(get_db)
):
    """Get all conversations"""
    conversations = db.query(Conversation).order_by(
        Conversation.updated_at.desc()
    ).all()
    
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

@router.get("/conversations/{conversation_id}")
async def get_conversation(
    conversation_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific conversation with all messages"""
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id
    ).first()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
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

