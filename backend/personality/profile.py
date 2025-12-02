from pydantic import BaseModel, Field
from typing import List, Dict, Optional


# ============================================================================
# Writing Style Profile
# ============================================================================

class RhythmPattern(BaseModel):
    """Captures writing rhythm and pacing patterns"""
    pacing_description: str = Field(description="Natural language description of writing pace")
    sentence_variation: str = Field(description="How sentence length varies - uniform, varied, rhythmic")
    paragraph_style: str = Field(description="Paragraph organization patterns")
    flow_characteristics: List[str] = Field(default_factory=list, description="Key flow traits")


class StylisticMarkers(BaseModel):
    """Unique stylistic fingerprints"""
    signature_phrases: List[str] = Field(default_factory=list, description="Distinctive recurring phrases")
    metaphor_patterns: List[str] = Field(default_factory=list, description="Types of metaphors used")
    transition_style: str = Field(description="How ideas are bridged")
    emphasis_patterns: List[str] = Field(default_factory=list, description="How emphasis is conveyed")
    punctuation_habits: str = Field(description="Notable punctuation patterns")


class TonalRange(BaseModel):
    """Tonal characteristics across contexts"""
    default_tone: str = Field(description="Primary tonal quality")
    tonal_shifts: Dict[str, str] = Field(default_factory=dict, description="Tone changes by context")
    emotional_coloring: str = Field(description="How emotion colors writing")
    formality_spectrum: str = Field(description="Range and default formality level")


class WritingStyleProfile(BaseModel):
    """Complete writing style analysis"""
    rhythm: RhythmPattern
    stylistic_markers: StylisticMarkers
    tonal_range: TonalRange
    linguistic_fingerprints: List[str] = Field(default_factory=list, description="Unique language patterns")
    vocabulary_character: str = Field(description="Vocabulary sophistication and character")
    voice_description: str = Field(description="Natural language summary of writing voice")
    confidence: float = Field(ge=0, le=1, description="Confidence in this analysis")


# ============================================================================
# Cognitive Profile
# ============================================================================

class ReasoningPatterns(BaseModel):
    """How reasoning is structured"""
    primary_mode: str = Field(description="Deductive, inductive, abductive, or mixed")
    logical_style: str = Field(description="Linear, associative, dialectical")
    evidence_preference: str = Field(description="How evidence is weighted and used")
    abstraction_level: str = Field(description="Concrete to abstract thinking preference")


class MentalModels(BaseModel):
    """Mental frameworks used"""
    identified_frameworks: List[str] = Field(default_factory=list, description="Named frameworks referenced")
    implicit_models: List[str] = Field(default_factory=list, description="Underlying mental models")
    analogical_sources: List[str] = Field(default_factory=list, description="Domains used for analogies")


class CognitiveProfile(BaseModel):
    """Complete cognitive pattern analysis"""
    reasoning_patterns: ReasoningPatterns
    mental_models: MentalModels
    problem_solving_style: str = Field(description="Approach to problem solving")
    idea_connection_style: str = Field(description="How ideas are linked and built upon")
    learning_approach: str = Field(description="How new information is processed")
    complexity_preference: str = Field(description="Tolerance for and attraction to complexity")
    thinking_description: str = Field(description="Natural language summary of thinking style")
    confidence: float = Field(ge=0, le=1, description="Confidence in this analysis")


# ============================================================================
# Emotional Profile
# ============================================================================

class EmotionalTriggers(BaseModel):
    """What evokes emotional responses"""
    excites: List[str] = Field(default_factory=list, description="Topics/situations that generate enthusiasm")
    frustrates: List[str] = Field(default_factory=list, description="Pain points and frustrations")
    motivates: List[str] = Field(default_factory=list, description="Core motivational drivers")
    calms: List[str] = Field(default_factory=list, description="Sources of comfort/stability")


class PassionMap(BaseModel):
    """Intensity of engagement by topic"""
    high_passion: List[str] = Field(default_factory=list, description="Topics with deep passion")
    moderate_interest: List[str] = Field(default_factory=list, description="Areas of steady interest")
    emerging_curiosity: List[str] = Field(default_factory=list, description="Growing interests")


class EmotionalProfile(BaseModel):
    """Complete emotional pattern analysis"""
    triggers: EmotionalTriggers
    passion_map: PassionMap
    expression_patterns: str = Field(description="How emotions are expressed in writing")
    emotional_vocabulary: List[str] = Field(default_factory=list, description="Characteristic emotional words")
    values_from_emotion: List[str] = Field(default_factory=list, description="Values inferred from emotional emphasis")
    emotional_baseline: str = Field(description="Default emotional state in writing")
    emotional_description: str = Field(description="Natural language summary of emotional patterns")
    confidence: float = Field(ge=0, le=1, description="Confidence in this analysis")


# ============================================================================
# Interest Profile
# ============================================================================

class Interest(BaseModel):
    """A single interest with depth information"""
    topic: str = Field(description="The interest area")
    depth: float = Field(ge=0, le=1, description="Depth of engagement 0-1")
    evidence: List[str] = Field(default_factory=list, description="What indicates this interest")
    context: str = Field(description="How this interest manifests")


class InterestProfile(BaseModel):
    """Complete interest and desire analysis"""
    genuine_interests: List[Interest] = Field(default_factory=list, description="Core interests with depth scores")
    curiosities: List[str] = Field(default_factory=list, description="Active areas of exploration")
    aspirations: List[str] = Field(default_factory=list, description="Goals and desires inferred from writing")
    topic_affinities: Dict[str, float] = Field(default_factory=dict, description="Topic engagement scores")
    learning_trajectories: List[str] = Field(default_factory=list, description="Knowledge pursuit patterns")
    interest_description: str = Field(description="Natural language summary of interests")
    confidence: float = Field(ge=0, le=1, description="Confidence in this analysis")


# ============================================================================
# Worldview Profile
# ============================================================================

class CoreBeliefs(BaseModel):
    """Fundamental beliefs and assumptions"""
    explicit_beliefs: List[str] = Field(default_factory=list, description="Directly stated beliefs")
    implicit_assumptions: List[str] = Field(default_factory=list, description="Underlying assumptions")
    values_hierarchy: List[str] = Field(default_factory=list, description="Core values in priority order")


class WorldviewProfile(BaseModel):
    """Complete worldview analysis"""
    core_beliefs: CoreBeliefs
    philosophical_leanings: List[str] = Field(default_factory=list, description="Philosophical orientations")
    framing_patterns: str = Field(description="How problems and opportunities are framed")
    unique_perspectives: List[str] = Field(default_factory=list, description="Distinctive viewpoints")
    domain_lenses: Dict[str, str] = Field(default_factory=dict, description="Perspective by domain")
    epistemology: str = Field(description="How they approach knowledge and truth")
    worldview_description: str = Field(description="Natural language summary of worldview")
    confidence: float = Field(ge=0, le=1, description="Confidence in this analysis")


# ============================================================================
# Social Profile
# ============================================================================

class CommunicationDynamics(BaseModel):
    """How communication unfolds"""
    initiation_style: str = Field(description="How conversations are started")
    response_patterns: str = Field(description="How responses are structured")
    engagement_depth: str = Field(description="Typical depth of engagement")
    directness_level: str = Field(description="Communication directness")


class SocialProfile(BaseModel):
    """Complete social pattern analysis"""
    communication_dynamics: CommunicationDynamics
    collaboration_style: str = Field(description="How they work with others")
    authority_positioning: str = Field(description="How expertise/authority is conveyed")
    audience_adaptation: Dict[str, str] = Field(default_factory=dict, description="Style shifts by audience")
    relational_patterns: List[str] = Field(default_factory=list, description="Relationship building patterns")
    conflict_approach: str = Field(description="How disagreement is handled")
    social_description: str = Field(description="Natural language summary of social patterns")
    confidence: float = Field(ge=0, le=1, description="Confidence in this analysis")


# ============================================================================
# Complete Personality Profile
# ============================================================================

class AnalysisMetadata(BaseModel):
    """Metadata about the analysis process"""
    model_config = {"protected_namespaces": ()}
    
    documents_analyzed: int = Field(description="Number of documents processed")
    total_tokens_analyzed: int = Field(description="Approximate tokens analyzed")
    analysis_duration_seconds: float = Field(description="Time taken for analysis")
    model_used: str = Field(description="LLM model used for analysis")


class PersonalityProfile(BaseModel):
    """Complete AI-analyzed personality profile"""
    version: int = 2  # Version 2 indicates new AI-powered schema
    
    # Six core dimensions
    writing_style: WritingStyleProfile
    cognitive: CognitiveProfile
    emotional: EmotionalProfile
    interests: InterestProfile
    worldview: WorldviewProfile
    social: SocialProfile
    
    # Synthesis
    personality_essence: str = Field(description="One-paragraph essence capturing the whole person")
    key_characteristics: List[str] = Field(default_factory=list, description="Top distinguishing traits")
    context_variations: Dict[str, str] = Field(default_factory=dict, description="How personality shifts by context")
    
    # Metadata
    analysis_metadata: Optional[AnalysisMetadata] = None
    overall_confidence: float = Field(ge=0, le=1, description="Overall profile confidence")

    def to_prompt_text(self) -> str:
        """Convert profile to rich text for LLM prompts"""
        sections = [
            "PERSONALITY PROFILE",
            "=" * 50,
            "",
            "## ESSENCE",
            self.personality_essence,
            "",
            "## KEY CHARACTERISTICS",
            *[f"- {c}" for c in self.key_characteristics[:7]],
            "",
            "## WRITING VOICE",
            self.writing_style.voice_description,
            f"- Rhythm: {self.writing_style.rhythm.pacing_description}",
            f"- Tone: {self.writing_style.tonal_range.default_tone}",
            f"- Vocabulary: {self.writing_style.vocabulary_character}",
            "",
            "Signature phrases and patterns:",
            *[f'  - "{p}"' for p in self.writing_style.stylistic_markers.signature_phrases[:5]],
            "",
            "## THINKING PATTERNS",
            self.cognitive.thinking_description,
            f"- Reasoning: {self.cognitive.reasoning_patterns.primary_mode}",
            f"- Problem-solving: {self.cognitive.problem_solving_style}",
            f"- Connects ideas: {self.cognitive.idea_connection_style}",
            "",
            "## EMOTIONAL LANDSCAPE",
            self.emotional.emotional_description,
            "",
            "What excites:",
            *[f"  - {e}" for e in self.emotional.triggers.excites[:4]],
            "",
            "What frustrates:",
            *[f"  - {f}" for f in self.emotional.triggers.frustrates[:3]],
            "",
            "Core motivations:",
            *[f"  - {m}" for m in self.emotional.triggers.motivates[:4]],
            "",
            "## INTERESTS & PASSIONS",
            self.interests.interest_description,
            "",
            "Deep interests:",
            *[f"  - {i.topic} (depth: {i.depth:.0%})" for i in self.interests.genuine_interests[:5]],
            "",
            "Aspirations:",
            *[f"  - {a}" for a in self.interests.aspirations[:4]],
            "",
            "## WORLDVIEW",
            self.worldview.worldview_description,
            "",
            "Core values:",
            *[f"  - {v}" for v in self.worldview.core_beliefs.values_hierarchy[:5]],
            "",
            "Philosophical leanings:",
            *[f"  - {p}" for p in self.worldview.philosophical_leanings[:3]],
            "",
            "## SOCIAL DYNAMICS",
            self.social.social_description,
            f"- Communication style: {self.social.communication_dynamics.directness_level}",
            f"- Collaboration: {self.social.collaboration_style}",
            f"- Authority: {self.social.authority_positioning}",
        ]
        
        # Add context variations if present
        if self.context_variations:
            sections.extend([
                "",
                "## CONTEXT ADAPTATIONS",
                *[f"- In {ctx}: {desc}" for ctx, desc in list(self.context_variations.items())[:4]],
            ])
        
        return "\n".join(sections)

    def get_dimension_confidence(self) -> Dict[str, float]:
        """Get confidence scores for each dimension"""
        return {
            "writing_style": self.writing_style.confidence,
            "cognitive": self.cognitive.confidence,
            "emotional": self.emotional.confidence,
            "interests": self.interests.confidence,
            "worldview": self.worldview.confidence,
            "social": self.social.confidence,
        }
