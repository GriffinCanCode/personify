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
from backend.logging_config import get_logger, PerformanceTimer

logger = get_logger(__name__)

class ConversationEngine:
    """Main RAG conversation engine for Virtual Griffin"""
    
    def __init__(self, db: Session):
        self.db = db
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        
        logger.debug("initializing_conversation_engine")
        
        # Load personality profile
        try:
            self.personality_profile = PersonalityProfileManager.get_active_profile(db)
            logger.info("personality_profile_loaded_for_conversation")
        except ValueError:
            logger.warning("no_personality_profile_available_for_conversation")
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
        logger.info(
            "chat_processing_started",
            query_length=len(query),
            conversation_id=conversation_id
        )
        
        if not self.personality_profile:
            logger.warning("chat_attempted_without_personality_profile")
            return {
                'response': "Please create a personality profile first by uploading and processing your documents.",
                'error': 'no_profile'
            }
        
        try:
            # Get or create conversation
            with PerformanceTimer(logger, "get_or_create_conversation"):
                conversation = self._get_or_create_conversation(conversation_id)
                conversation_context = self._build_context(conversation)
            
            # Classify query context
            with PerformanceTimer(logger, "classify_query_context"):
                context = ContextClassifier.classify(query, conversation_context.messages)
            logger.debug("query_context_classified", context=context)
            
            # Retrieve relevant chunks from vector store
            with PerformanceTimer(logger, "retrieve_chunks", k=7):
                retrieved_chunks = retriever.retrieve_with_diversity(query, k=7)
            logger.info("chunks_retrieved", chunk_count=len(retrieved_chunks))
            
            # Build prompt
            with PerformanceTimer(logger, "build_prompt"):
                messages = self.prompt_builder.build_messages(
                    query=query,
                    retrieved_chunks=retrieved_chunks,
                    context=context,
                    conversation_history=conversation_context.messages
                )
            
            # Generate response
            with PerformanceTimer(logger, "generate_llm_response", model=settings.OPENAI_CHAT_MODEL):
                response_text = self._generate_response(messages)
            logger.info("llm_response_generated", response_length=len(response_text))
            
            # Validate response
            with PerformanceTimer(logger, "validate_response"):
                validation = self.validator.validate(response_text)
            logger.info(
                "response_validated",
                confidence_score=validation['confidence_score'],
                style_match=validation['style_match']
            )
            
            # Save to database
            with PerformanceTimer(logger, "save_conversation_to_db"):
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
            
            logger.info(
                "chat_processing_completed",
                conversation_id=conversation.id,
                message_id=assistant_message.id
            )
            
            return {
                'response': response_text,
                'confidence_score': validation['confidence_score'],
                'style_match': validation['style_match'],
                'conversation_id': conversation.id,
                'message_id': assistant_message.id,
                'retrieved_chunks': retrieved_chunks[:5],
                'validation_issues': validation.get('issues', [])
            }
        except Exception as e:
            logger.error(
                "chat_processing_error",
                error=str(e),
                conversation_id=conversation_id,
                exc_info=True
            )
            raise
    
    def _get_or_create_conversation(self, conversation_id: Optional[int]) -> Conversation:
        """Get existing conversation or create new one"""
        if conversation_id:
            conversation = self.db.query(Conversation).filter(
                Conversation.id == conversation_id
            ).first()
            if conversation:
                logger.debug("existing_conversation_retrieved", conversation_id=conversation_id)
                return conversation
        
        # Create new conversation
        conversation = Conversation(title="New Conversation")
        self.db.add(conversation)
        self.db.commit()
        self.db.refresh(conversation)
        logger.info("new_conversation_created", conversation_id=conversation.id)
        return conversation
    
    def _build_context(self, conversation: Conversation) -> ConversationContext:
        """Build conversation context from database"""
        context = ConversationContext(conversation_id=conversation.id)
        
        for message in conversation.messages:
            context.add_message(message.role, message.content)
        
        logger.debug("conversation_context_built", conversation_id=conversation.id, message_count=len(conversation.messages))
        return context
    
    def _generate_response(self, messages: list) -> str:
        """Generate response using OpenAI API"""
        logger.debug("calling_openai_api", model=settings.OPENAI_CHAT_MODEL, message_count=len(messages))
        
        response = self.client.chat.completions.create(
            model=settings.OPENAI_CHAT_MODEL,
            messages=messages,
            temperature=0.7,
            max_tokens=1000
        )
        
        logger.debug(
            "openai_api_response_received",
            model=settings.OPENAI_CHAT_MODEL,
            finish_reason=response.choices[0].finish_reason
        )
        
        return response.choices[0].message.content

