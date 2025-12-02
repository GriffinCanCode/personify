from typing import List, Dict, Optional
from pydantic import BaseModel

class ConversationContext(BaseModel):
    """Manages context for a conversation"""
    conversation_id: Optional[int] = None
    messages: List[Dict] = []
    max_history: int = 10
    
    def add_message(self, role: str, content: str):
        """Add a message to context"""
        self.messages.append({
            'role': role,
            'content': content
        })
        
        # Keep only recent messages
        if len(self.messages) > self.max_history * 2:  # * 2 for user + assistant pairs
            self.messages = self.messages[-self.max_history * 2:]
    
    def get_history_text(self) -> str:
        """Get conversation history as text"""
        if not self.messages:
            return "No previous conversation."
        
        history = []
        for msg in self.messages[-10:]:  # Last 10 messages
            role = msg['role'].capitalize()
            content = msg['content']
            history.append(f"{role}: {content}")
        
        return '\n'.join(history)
    
    def get_messages_for_llm(self) -> List[Dict]:
        """Format messages for LLM API"""
        return self.messages[-10:]

class ContextClassifier:
    """Classify context of user queries"""
    
    @staticmethod
    def classify(query: str, conversation_history: List[Dict] = None) -> Dict:
        """
        Classify the context of a query.
        
        Returns:
        - formality: casual, neutral, professional
        - topic: detected topic category
        - intent: question, statement, request
        """
        query_lower = query.lower()
        
        # Formality detection
        formal_indicators = ['please', 'would you', 'could you', 'kindly']
        casual_indicators = ['hey', 'what\'s', 'gonna', 'wanna', 'yeah']
        
        formality = 'neutral'
        if any(ind in query_lower for ind in formal_indicators):
            formality = 'professional'
        elif any(ind in query_lower for ind in casual_indicators):
            formality = 'casual'
        
        # Intent detection
        question_words = ['what', 'why', 'how', 'when', 'where', 'who', 'which']
        
        intent = 'statement'
        if query.strip().endswith('?'):
            intent = 'question'
        elif any(query_lower.startswith(qw) for qw in question_words):
            intent = 'question'
        elif any(word in query_lower for word in ['please', 'can you', 'could you']):
            intent = 'request'
        
        return {
            'formality': formality,
            'intent': intent,
            'query_length': len(query.split())
        }

