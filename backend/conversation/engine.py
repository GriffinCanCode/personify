from typing import Dict, Optional
from openai import OpenAI
from sqlalchemy.orm import Session

from backend.config import settings
from backend.personality.builder import PersonalityProfileManager
from backend.vectorstore.retrieval import retriever
from backend.conversation.context import ConversationContext, ContextClassifier
from backend.conversation.prompt_builder import PromptBuilder
from backend.conversation.validator import ResponseValidator
from backend.database.models import Conversation, Message

class ConversationEngine:
    """Main RAG conversation engine for Virtual Griffin"""
    
    def __init__(self, db: Session):
        self.db = db
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        
        # Load personality profile
        try:
            self.personality_profile = PersonalityProfileManager.get_active_profile(db)
        except ValueError:
            self.personality_profile = None
        
        # Initialize components
        if self.personality_profile:
            self.prompt_builder = PromptBuilder(self.personality_profile)
            self.validator = ResponseValidator(self.personality_profile)
        else:
            self.prompt_builder = None
            self.validator = None
    
    def chat(
        self,
        query: str,
        conversation_id: Optional[int] = None
    ) -> Dict:
        """
        Main chat method - handles a user query and returns Virtual Griffin's response.
        
        Args:
            query: User's question/message
            conversation_id: Optional existing conversation ID
        
        Returns:
            Dict with:
            - response: Virtual Griffin's response
            - confidence_score: Confidence in response quality
            - conversation_id: Conversation ID
            - message_id: Message ID
            - retrieved_chunks: Sources used
        """
        if not self.personality_profile:
            return {
                'response': "Please create a personality profile first by uploading and processing your documents.",
                'error': 'no_profile'
            }
        
        # Get or create conversation
        conversation = self._get_or_create_conversation(conversation_id)
        conversation_context = self._build_context(conversation)
        
        # Classify query context
        context = ContextClassifier.classify(query, conversation_context.messages)
        
        # Retrieve relevant chunks from vector store
        retrieved_chunks = retriever.retrieve_with_diversity(query, k=7)
        
        # Build prompt
        messages = self.prompt_builder.build_messages(
            query=query,
            retrieved_chunks=retrieved_chunks,
            context=context,
            conversation_history=conversation_context.messages
        )
        
        # Generate response
        response_text = self._generate_response(messages)
        
        # Validate response
        validation = self.validator.validate(response_text)
        
        # Save to database
        user_message = Message(
            conversation_id=conversation.id,
            role='user',
            content=query,
            metadata={'context': context}
        )
        
        assistant_message = Message(
            conversation_id=conversation.id,
            role='assistant',
            content=response_text,
            confidence_score=validation['confidence_score'],
            retrieved_chunks=[
                {
                    'id': chunk['id'],
                    'content': chunk['content'][:200],  # Truncated for storage
                    'metadata': chunk.get('metadata', {})
                }
                for chunk in retrieved_chunks[:5]
            ],
            metadata={
                'validation': validation,
                'model': settings.OPENAI_CHAT_MODEL
            }
        )
        
        self.db.add(user_message)
        self.db.add(assistant_message)
        self.db.commit()
        self.db.refresh(assistant_message)
        
        return {
            'response': response_text,
            'confidence_score': validation['confidence_score'],
            'style_match': validation['style_match'],
            'conversation_id': conversation.id,
            'message_id': assistant_message.id,
            'retrieved_chunks': retrieved_chunks[:5],
            'validation_issues': validation.get('issues', [])
        }
    
    def _get_or_create_conversation(self, conversation_id: Optional[int]) -> Conversation:
        """Get existing conversation or create new one"""
        if conversation_id:
            conversation = self.db.query(Conversation).filter(
                Conversation.id == conversation_id
            ).first()
            if conversation:
                return conversation
        
        # Create new conversation
        conversation = Conversation(title="New Conversation")
        self.db.add(conversation)
        self.db.commit()
        self.db.refresh(conversation)
        return conversation
    
    def _build_context(self, conversation: Conversation) -> ConversationContext:
        """Build conversation context from database"""
        context = ConversationContext(conversation_id=conversation.id)
        
        for message in conversation.messages:
            context.add_message(message.role, message.content)
        
        return context
    
    def _generate_response(self, messages: list) -> str:
        """Generate response using OpenAI API"""
        response = self.client.chat.completions.create(
            model=settings.OPENAI_CHAT_MODEL,
            messages=messages,
            temperature=0.7,
            max_tokens=1000
        )
        
        return response.choices[0].message.content

