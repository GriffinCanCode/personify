from typing import List, Dict
from backend.personality.profile import PersonalityProfile


class PromptBuilder:
    """Build prompts for the conversation engine using AI-analyzed personality profiles"""
    
    def __init__(self, personality_profile: PersonalityProfile):
        self.profile = personality_profile
    
    def build_system_prompt(self) -> str:
        """Build the system prompt that defines Virtual Griffin"""
        profile_text = self.profile.to_prompt_text()
        
        # Build style guidance from writing style analysis
        style = self.profile.writing_style
        style_guidance = self._build_style_guidance()
        
        # Build cognitive guidance
        cognitive_guidance = self._build_cognitive_guidance()
        
        system_prompt = f"""You are Virtual Griffin, an identical digital twin of Griffin Strier.

Your purpose is to respond EXACTLY as Griffin would - matching his writing style, personality, knowledge, and thinking patterns. You are not a helpful assistant; you ARE Griffin in digital form.

{profile_text}

{style_guidance}

{cognitive_guidance}

CRITICAL INSTRUCTIONS:

1. EMBODY THE WRITING VOICE:
   - Use Griffin's distinctive rhythm and pacing
   - Incorporate his signature phrases naturally (don't force them)
   - Match his tonal quality and emotional coloring
   - Mirror his vocabulary sophistication and word choices
   - Follow his paragraph and sentence structure patterns

2. THINK LIKE GRIFFIN:
   - Use his reasoning style: {self.profile.cognitive.reasoning_patterns.primary_mode}
   - Apply his mental models and frameworks
   - Connect ideas the way he does: {self.profile.cognitive.idea_connection_style}
   - Approach problems his way: {self.profile.cognitive.problem_solving_style}

3. EXPRESS AUTHENTIC EMOTION:
   - Show genuine enthusiasm for topics that excite him
   - Reflect his values through emotional emphasis
   - Maintain his emotional baseline: {self.profile.emotional.emotional_baseline}

4. STAY TRUE TO HIS WORLDVIEW:
   - Frame things through his perspective
   - Reflect his core values and beliefs
   - Apply his philosophical leanings naturally

5. ADAPT SOCIALLY AS HE WOULD:
   - Match his communication directness: {self.profile.social.communication_dynamics.directness_level}
   - Position authority as he does: {self.profile.social.authority_positioning}
   - Engage at his typical depth: {self.profile.social.communication_dynamics.engagement_depth}

6. AUTHENTICITY:
   - This is not roleplay - you ARE Griffin
   - Don't say "Griffin would think..." - just think it
   - Be genuine, not performative
   - When uncertain, admit it as Griffin would

You will be provided with relevant examples of how Griffin has actually responded to similar queries. Use these to calibrate your response, but synthesize naturally - don't copy verbatim.
"""
        return system_prompt
    
    def _build_style_guidance(self) -> str:
        """Build specific writing style guidance"""
        style = self.profile.writing_style
        markers = style.stylistic_markers
        
        signature_phrases = markers.signature_phrases[:8]
        phrases_text = ", ".join(f'"{p}"' for p in signature_phrases) if signature_phrases else "(none identified)"
        
        return f"""WRITING STYLE GUIDANCE:

Voice Character: {style.voice_description}

Rhythm & Flow:
- Pacing: {style.rhythm.pacing_description}
- Sentence variation: {style.rhythm.sentence_variation}
- Paragraph style: {style.rhythm.paragraph_style}

Signature Patterns:
- Phrases to naturally incorporate: {phrases_text}
- Transition style: {markers.transition_style}
- Emphasis patterns: {', '.join(markers.emphasis_patterns[:4]) if markers.emphasis_patterns else 'standard'}
- Metaphor tendencies: {', '.join(markers.metaphor_patterns[:3]) if markers.metaphor_patterns else 'varied'}

Tone:
- Default: {style.tonal_range.default_tone}
- Emotional coloring: {style.tonal_range.emotional_coloring}
- Formality: {style.tonal_range.formality_spectrum}"""

    def _build_cognitive_guidance(self) -> str:
        """Build cognitive pattern guidance"""
        cog = self.profile.cognitive
        
        frameworks = cog.mental_models.identified_frameworks[:5]
        frameworks_text = ", ".join(frameworks) if frameworks else "(none explicitly identified)"
        
        return f"""COGNITIVE PATTERNS:

Thinking Style: {cog.thinking_description}

Reasoning:
- Primary mode: {cog.reasoning_patterns.primary_mode}
- Logical style: {cog.reasoning_patterns.logical_style}
- Evidence handling: {cog.reasoning_patterns.evidence_preference}

Mental Models & Frameworks:
- Uses: {frameworks_text}
- Draws analogies from: {', '.join(cog.mental_models.analogical_sources[:4]) if cog.mental_models.analogical_sources else 'varied domains'}

Complexity: {cog.complexity_preference}
Learning approach: {cog.learning_approach}"""

    def build_user_prompt(
        self,
        query: str,
        retrieved_chunks: List[Dict],
        context: Dict,
        conversation_history: str = None
    ) -> str:
        """Build the user prompt with query and context"""
        examples_text = self._format_retrieved_examples(retrieved_chunks)
        
        history_text = ""
        if conversation_history:
            history_text = f"\nRECENT CONVERSATION:\n{conversation_history}\n"
        
        # Add relevant emotional/interest context if query matches known patterns
        context_hints = self._get_context_hints(query)
        
        user_prompt = f"""
{history_text}
RELEVANT EXAMPLES OF HOW GRIFFIN HAS RESPONDED/WRITTEN:

{examples_text}

CURRENT QUERY CONTEXT:
- Formality: {context.get('formality', 'neutral')}
- Intent: {context.get('intent', 'unknown')}
{context_hints}

USER QUERY: {query}

Respond as Griffin would, naturally incorporating his style and thinking patterns shown in the examples above. Be authentic and genuine.
"""
        return user_prompt
    
    def _get_context_hints(self, query: str) -> str:
        """Get contextual hints based on query matching known patterns"""
        hints = []
        query_lower = query.lower()
        
        # Check if query relates to high-passion topics
        for topic in self.profile.emotional.passion_map.high_passion[:5]:
            if topic.lower() in query_lower:
                hints.append(f"- Note: This topic ({topic}) is a HIGH PASSION area - show genuine enthusiasm")
                break
        
        # Check for topics that frustrate
        for frustration in self.profile.emotional.triggers.frustrates[:3]:
            if any(word in query_lower for word in frustration.lower().split()[:2]):
                hints.append(f"- Note: This may touch on a frustration point - authentic reaction expected")
                break
        
        return "\n".join(hints)
    
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
