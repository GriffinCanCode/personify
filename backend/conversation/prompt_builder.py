from typing import List, Dict
from backend.personality.profile import PersonalityProfile

class PromptBuilder:
    """Build prompts for the conversation engine"""
    
    def __init__(self, personality_profile: PersonalityProfile):
        self.profile = personality_profile
    
    def build_system_prompt(self) -> str:
        """Build the system prompt that defines Virtual Griffin"""
        profile_text = self.profile.to_prompt_text()
        
        system_prompt = f"""You are Virtual Griffin, an identical digital twin of Griffin Strier.

Your purpose is to respond EXACTLY as Griffin would - matching his writing style, personality, knowledge, and thinking patterns. You are not a helpful assistant; you ARE Griffin in digital form.

{profile_text}

CRITICAL INSTRUCTIONS:
1. Match Griffin's Communication Style:
   - Use his exact level of formality, directness, and verbosity
   - Incorporate his common phrases naturally
   - Mirror his sentence structure and vocabulary
   - Maintain his characteristic humor level

2. Embody His Personality:
   - Reflect his personality traits in your responses
   - Prioritize topics according to his values
   - Respond with his level of openness, conscientiousness, etc.

3. Knowledge Boundaries:
   - Speak confidently on his expert domains
   - Be honest about unfamiliarity with topics outside his knowledge
   - Reference his actual experiences when relevant

4. Think Like Griffin:
   - Use his decision-making patterns
   - Apply his analytical/intuitive balance
   - Maintain his risk tolerance in suggestions

5. Authenticity:
   - This is not roleplay - you ARE Griffin
   - Don't say "Griffin would think..." - just think it
   - Be genuine, not performative

You will be provided with relevant examples of how Griffin has actually responded to similar queries. Use these to calibrate your response, but synthesize naturally - don't copy verbatim.
"""
        return system_prompt
    
    def build_user_prompt(
        self,
        query: str,
        retrieved_chunks: List[Dict],
        context: Dict,
        conversation_history: str = None
    ) -> str:
        """Build the user prompt with query and context"""
        # Format retrieved examples
        examples_text = self._format_retrieved_examples(retrieved_chunks)
        
        # Add conversation history if exists
        history_text = ""
        if conversation_history:
            history_text = f"\nRECENT CONVERSATION:\n{conversation_history}\n"
        
        # Build complete prompt
        user_prompt = f"""
{history_text}
RELEVANT EXAMPLES OF HOW GRIFFIN HAS RESPONDED/WRITTEN:

{examples_text}

CURRENT QUERY CONTEXT:
- Formality: {context.get('formality', 'neutral')}
- Intent: {context.get('intent', 'unknown')}

USER QUERY: {query}

Respond as Griffin would, naturally incorporating his style and thinking patterns shown in the examples above. Be authentic and genuine.
"""
        return user_prompt
    
    def _format_retrieved_examples(self, chunks: List[Dict]) -> str:
        """Format retrieved chunks as examples"""
        if not chunks:
            return "(No directly relevant examples found - rely on personality profile)"
        
        formatted = []
        for i, chunk in enumerate(chunks[:7], 1):
            content = chunk['content']
            metadata = chunk.get('metadata', {})
            
            source_type = metadata.get('source_type', 'unknown')
            context = metadata.get('context', 'unknown')
            
            example = f"Example {i} (from {source_type}, {context} context):\n{content}\n"
            formatted.append(example)
        
        return '\n'.join(formatted)
    
    def build_messages(
        self,
        query: str,
        retrieved_chunks: List[Dict],
        context: Dict,
        conversation_history: List[Dict] = None
    ) -> List[Dict]:
        """Build complete message array for LLM API"""
        messages = [
            {
                'role': 'system',
                'content': self.build_system_prompt()
            }
        ]
        
        # Add conversation history
        if conversation_history:
            messages.extend(conversation_history[-6:])  # Last 6 messages (3 exchanges)
        
        # Add current query with context
        history_str = None
        if conversation_history:
            history_str = '\n'.join(
                f"{m['role'].capitalize()}: {m['content']}" 
                for m in conversation_history[-4:]
            )
        
        user_prompt = self.build_user_prompt(
            query=query,
            retrieved_chunks=retrieved_chunks,
            context=context,
            conversation_history=history_str
        )
        
        messages.append({
            'role': 'user',
            'content': user_prompt
        })
        
        return messages

