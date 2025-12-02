"""
LLM Prompt Library for AI-Powered Personality Analysis

Each prompt is designed to extract deep, nuanced patterns rather than surface-level features.
Prompts output structured JSON for reliable parsing.
"""

# ============================================================================
# PASS 1: Pattern Extraction Prompts
# ============================================================================

WRITING_STYLE_EXTRACTION_PROMPT = """Analyze the following writing samples to extract deep patterns about the author's writing style.

Go beyond surface metrics. Look for:
- RHYTHM: How does the writing flow? Is it staccato or flowing? Does sentence length vary rhythmically or uniformly?
- VOICE: What makes this voice distinctive? What would you recognize if you saw it elsewhere?
- STYLISTIC FINGERPRINTS: What are the signature moves? Metaphor types? Transition patterns? Emphasis techniques?
- TONAL CHARACTER: What's the default emotional coloring? How does tone shift?

WRITING SAMPLES:
{text_samples}

Respond with a JSON object (no markdown):
{{
    "rhythm": {{
        "pacing_description": "natural language description of the writing pace and flow",
        "sentence_variation": "how sentence length varies",
        "paragraph_style": "how paragraphs are organized",
        "flow_characteristics": ["key flow traits"]
    }},
    "stylistic_markers": {{
        "signature_phrases": ["distinctive phrases they use repeatedly"],
        "metaphor_patterns": ["types of metaphors/analogies they favor"],
        "transition_style": "how they bridge between ideas",
        "emphasis_patterns": ["how they convey emphasis"],
        "punctuation_habits": "notable punctuation patterns"
    }},
    "tonal_range": {{
        "default_tone": "primary tonal quality",
        "tonal_shifts": {{"context": "tone in that context"}},
        "emotional_coloring": "how emotion colors the writing",
        "formality_spectrum": "formality range and default"
    }},
    "linguistic_fingerprints": ["unique language patterns that identify this writer"],
    "vocabulary_character": "description of vocabulary sophistication and character",
    "voice_description": "2-3 sentence summary of their distinctive writing voice",
    "confidence": 0.0 to 1.0
}}"""


COGNITIVE_EXTRACTION_PROMPT = """Analyze the following writing samples to understand how this person thinks and reasons.

Look for:
- REASONING PATTERNS: Do they reason deductively (principles to specifics) or inductively (examples to patterns)? Linear or associative?
- MENTAL MODELS: What frameworks do they use to understand the world? What analogies recur?
- PROBLEM SOLVING: How do they approach problems? Break down vs. holistic? Analytical vs. intuitive?
- IDEA CONNECTIONS: How do they link concepts? Through hierarchy, networks, narrative?

WRITING SAMPLES:
{text_samples}

Respond with a JSON object (no markdown):
{{
    "reasoning_patterns": {{
        "primary_mode": "deductive/inductive/abductive/mixed",
        "logical_style": "linear/associative/dialectical",
        "evidence_preference": "how evidence is weighted and used",
        "abstraction_level": "preference for concrete vs abstract"
    }},
    "mental_models": {{
        "identified_frameworks": ["named frameworks they reference"],
        "implicit_models": ["underlying mental models they use"],
        "analogical_sources": ["domains they draw analogies from"]
    }},
    "problem_solving_style": "their approach to tackling problems",
    "idea_connection_style": "how they link and build upon ideas",
    "learning_approach": "how they process new information",
    "complexity_preference": "their tolerance for and attraction to complexity",
    "thinking_description": "2-3 sentence summary of their thinking style",
    "confidence": 0.0 to 1.0
}}"""


EMOTIONAL_EXTRACTION_PROMPT = """Analyze the following writing samples to understand this person's emotional patterns and what drives them.

Look beyond keywords. Identify:
- TRIGGERS: What topics/situations make them light up? What frustrates them? What genuinely motivates them?
- PASSION: Where does their writing come alive? What do they engage with deeply vs. superficially?
- EXPRESSION: How do emotions manifest in their writing? Explicit or implicit? Restrained or expressive?
- VALUES: What values are revealed through emotional emphasis?

WRITING SAMPLES:
{text_samples}

Respond with a JSON object (no markdown):
{{
    "triggers": {{
        "excites": ["topics/situations that generate genuine enthusiasm"],
        "frustrates": ["pain points and sources of frustration"],
        "motivates": ["core drivers - what pushes them forward"],
        "calms": ["sources of comfort or stability"]
    }},
    "passion_map": {{
        "high_passion": ["topics with deep, visible passion"],
        "moderate_interest": ["areas of steady engagement"],
        "emerging_curiosity": ["growing or developing interests"]
    }},
    "expression_patterns": "how emotions are expressed in their writing",
    "emotional_vocabulary": ["characteristic emotional words and phrases"],
    "values_from_emotion": ["values inferred from what evokes emotion"],
    "emotional_baseline": "their default emotional state in writing",
    "emotional_description": "2-3 sentence summary of their emotional patterns",
    "confidence": 0.0 to 1.0
}}"""


INTEREST_EXTRACTION_PROMPT = """Analyze the following writing samples to understand this person's genuine interests, desires, and aspirations.

Don't just count topic mentions. Look for:
- GENUINE INTEREST: Where do they go deep? What shows authentic engagement vs. passing mention?
- CURIOSITY: What are they actively exploring or learning?
- ASPIRATIONS: What goals or desires can you infer from their writing?
- PATTERNS: How do their interests connect? What's the underlying thread?

WRITING SAMPLES:
{text_samples}

Respond with a JSON object (no markdown):
{{
    "genuine_interests": [
        {{
            "topic": "interest area",
            "depth": 0.0 to 1.0,
            "evidence": ["what indicates this interest"],
            "context": "how this interest manifests"
        }}
    ],
    "curiosities": ["areas they're actively exploring"],
    "aspirations": ["goals, desires, ambitions inferred from writing"],
    "topic_affinities": {{"topic": 0.0 to 1.0}},
    "learning_trajectories": ["knowledge pursuit patterns"],
    "interest_description": "2-3 sentence summary of their interests and what drives them",
    "confidence": 0.0 to 1.0
}}"""


WORLDVIEW_EXTRACTION_PROMPT = """Analyze the following writing samples to understand this person's worldview, beliefs, and unique perspective.

Look for:
- BELIEFS: What do they believe about how the world works? What assumptions underlie their thinking?
- VALUES: What do they prioritize? What trade-offs do they make?
- FRAMING: How do they frame problems and opportunities? Through what lens?
- PERSPECTIVE: What's unique about how they see things?

WRITING SAMPLES:
{text_samples}

Respond with a JSON object (no markdown):
{{
    "core_beliefs": {{
        "explicit_beliefs": ["beliefs they directly state"],
        "implicit_assumptions": ["assumptions underlying their writing"],
        "values_hierarchy": ["values in priority order"]
    }},
    "philosophical_leanings": ["philosophical orientations - optimism/pragmatism/etc"],
    "framing_patterns": "how they typically frame problems and opportunities",
    "unique_perspectives": ["distinctive viewpoints they hold"],
    "domain_lenses": {{"domain": "their perspective on it"}},
    "epistemology": "how they approach knowledge and truth",
    "worldview_description": "2-3 sentence summary of their worldview",
    "confidence": 0.0 to 1.0
}}"""


SOCIAL_EXTRACTION_PROMPT = """Analyze the following writing samples to understand this person's social and communication patterns.

Look for:
- COMMUNICATION STYLE: How do they engage? Direct or indirect? Formal or casual?
- COLLABORATION: How do they work with others? Lead, follow, partner?
- AUTHORITY: How do they position expertise? Confident, humble, collaborative?
- ADAPTATION: How does their style shift for different audiences?

WRITING SAMPLES:
{text_samples}

Respond with a JSON object (no markdown):
{{
    "communication_dynamics": {{
        "initiation_style": "how they start conversations or topics",
        "response_patterns": "how they structure responses",
        "engagement_depth": "typical depth of engagement",
        "directness_level": "direct to indirect spectrum"
    }},
    "collaboration_style": "how they work with others",
    "authority_positioning": "how expertise/authority is conveyed",
    "audience_adaptation": {{"audience_type": "style adaptation"}},
    "relational_patterns": ["patterns in how they build/maintain relationships"],
    "conflict_approach": "how they handle disagreement",
    "social_description": "2-3 sentence summary of their social patterns",
    "confidence": 0.0 to 1.0
}}"""


# ============================================================================
# PASS 2: Synthesis Prompt
# ============================================================================

SYNTHESIS_PROMPT = """You are synthesizing a personality profile from multiple analysis dimensions.

You have analyzed this person across six dimensions:
1. Writing Style
2. Cognitive Patterns  
3. Emotional Patterns
4. Interests
5. Worldview
6. Social Patterns

RAW ANALYSIS DATA:
{raw_analyses}

Your task is to:
1. Identify the ESSENCE - What is the core of this person? Write a compelling one-paragraph summary.
2. Extract KEY CHARACTERISTICS - What are the 5-7 most distinguishing traits?
3. Note CONTEXT VARIATIONS - How does this personality adapt to different contexts?
4. Resolve any contradictions - If dimensions conflict, determine what's core vs. situational.
5. Calculate OVERALL CONFIDENCE based on consistency and evidence strength.

Respond with a JSON object (no markdown):
{{
    "personality_essence": "One compelling paragraph capturing who this person is",
    "key_characteristics": ["The 5-7 most distinguishing traits"],
    "context_variations": {{
        "professional": "how personality manifests professionally",
        "personal": "how personality manifests personally",
        "creative": "how personality manifests in creative contexts"
    }},
    "contradictions_resolved": ["any conflicts identified and how they were resolved"],
    "overall_confidence": 0.0 to 1.0
}}"""


# ============================================================================
# Helper: Get all extraction prompts
# ============================================================================

EXTRACTION_PROMPTS = {
    "writing_style": WRITING_STYLE_EXTRACTION_PROMPT,
    "cognitive": COGNITIVE_EXTRACTION_PROMPT,
    "emotional": EMOTIONAL_EXTRACTION_PROMPT,
    "interests": INTEREST_EXTRACTION_PROMPT,
    "worldview": WORLDVIEW_EXTRACTION_PROMPT,
    "social": SOCIAL_EXTRACTION_PROMPT,
}

DIMENSION_NAMES = {
    "writing_style": "Writing Style",
    "cognitive": "Cognitive Patterns",
    "emotional": "Emotional Patterns",
    "interests": "Interests & Desires",
    "worldview": "Worldview & Beliefs",
    "social": "Social Dynamics",
}

