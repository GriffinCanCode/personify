from pydantic import BaseModel
from typing import List, Dict, Optional

class CommunicationStyle(BaseModel):
    formality: float  # 0-1 scale
    directness: float
    verbosity: float
    humor: float
    common_phrases: List[str]
    sentence_structure: str
    vocabulary_level: str
    avg_sentence_length: float
    avg_word_length: float

class PersonalityTraits(BaseModel):
    openness: float  # Big Five traits, 0-1 scale
    conscientiousness: float
    extraversion: float
    agreeableness: float
    emotional_stability: float

class DecisionPatterns(BaseModel):
    analytical_vs_intuitive: float  # 0=intuitive, 1=analytical
    risk_tolerance: float
    time_preference: str  # quick, deliberate, varies

class PersonalityProfile(BaseModel):
    version: int = 1
    communication_style: CommunicationStyle
    personality_traits: PersonalityTraits
    values_hierarchy: List[str]
    knowledge_domains: Dict[str, List[str]]  # expert, competent, learning
    decision_patterns: DecisionPatterns
    context_adaptations: Dict[str, Dict]  # Different styles for different contexts
    
    def to_prompt_text(self) -> str:
        """Convert profile to text for LLM prompts"""
        style = self.communication_style
        traits = self.personality_traits
        
        prompt = f"""PERSONALITY PROFILE:

Communication Style:
- Formality: {self._scale_to_text(style.formality, 'Very Casual', 'Very Formal')}
- Directness: {self._scale_to_text(style.directness, 'Diplomatic', 'Very Direct')}
- Verbosity: {self._scale_to_text(style.verbosity, 'Concise', 'Detailed')}
- Humor: {self._scale_to_text(style.humor, 'Serious', 'Humorous')}
- Common phrases: {', '.join(f'"{p}"' for p in style.common_phrases[:10])}
- Average sentence length: {style.avg_sentence_length:.1f} words
- Vocabulary: {style.vocabulary_level}

Personality Traits:
- Openness: {self._scale_to_text(traits.openness, 'Practical', 'Creative/Abstract')}
- Conscientiousness: {self._scale_to_text(traits.conscientiousness, 'Spontaneous', 'Organized')}
- Extraversion: {self._scale_to_text(traits.extraversion, 'Reserved', 'Outgoing')}
- Agreeableness: {self._scale_to_text(traits.agreeableness, 'Skeptical', 'Trusting')}
- Emotional Stability: {self._scale_to_text(traits.emotional_stability, 'Reactive', 'Calm')}

Values (in priority order):
{chr(10).join(f'- {v}' for v in self.values_hierarchy[:5])}

Knowledge Domains:
- Expert in: {', '.join(self.knowledge_domains.get('expert', [])[:5])}
- Competent in: {', '.join(self.knowledge_domains.get('competent', [])[:5])}

Decision Making:
- Style: {self._scale_to_text(self.decision_patterns.analytical_vs_intuitive, 'Intuitive', 'Analytical')}
- Risk tolerance: {self._scale_to_text(self.decision_patterns.risk_tolerance, 'Conservative', 'Risk-taking')}
- Pace: {self.decision_patterns.time_preference}
"""
        return prompt
    
    def _scale_to_text(self, value: float, low_label: str, high_label: str) -> str:
        """Convert 0-1 scale to descriptive text"""
        if value < 0.3:
            return low_label
        elif value < 0.7:
            return f"Balanced ({low_label}/{high_label})"
        else:
            return high_label

