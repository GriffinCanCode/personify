"""
AI-Powered Personality Analysis Engine

Multi-pass LLM analysis for deep personality extraction:
- Pass 1: Extract patterns for each dimension
- Pass 2: Synthesize into coherent profile
"""

import json
import time
from typing import List, Dict, Optional, Callable
from anthropic import Anthropic

from backend.config import settings
from backend.personality.profile import (
    PersonalityProfile, WritingStyleProfile, CognitiveProfile,
    EmotionalProfile, InterestProfile, WorldviewProfile, SocialProfile,
    RhythmPattern, StylisticMarkers, TonalRange, ReasoningPatterns,
    MentalModels, EmotionalTriggers, PassionMap, Interest, CoreBeliefs,
    CommunicationDynamics, AnalysisMetadata
)
from backend.personality.prompts import EXTRACTION_PROMPTS, SYNTHESIS_PROMPT, DIMENSION_NAMES
from backend.logging_config import get_logger, PerformanceTimer

logger = get_logger(__name__)


class PatternExtractor:
    """Pass 1: Extract patterns for each personality dimension using LLM"""
    
    def __init__(self, client: Anthropic, model: str):
        self.client = client
        self.model = model
    
    def extract_dimension(
        self, 
        dimension: str, 
        text_samples: List[str],
        max_tokens: Optional[int] = None
    ) -> Dict:
        """Extract patterns for a single dimension"""
        max_tokens = max_tokens or settings.ANALYSIS_MAX_TOKENS
        prompt_template = EXTRACTION_PROMPTS.get(dimension)
        if not prompt_template:
            raise ValueError(f"Unknown dimension: {dimension}")
        
        # Combine text samples with separators
        combined_text = "\n\n---\n\n".join(text_samples)
        prompt = prompt_template.format(text_samples=combined_text)
        
        logger.debug(f"extracting_{dimension}", sample_count=len(text_samples))
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                system="You are an expert psychologist and linguistic analyst. Analyze writing samples to extract deep personality patterns. Always respond with valid JSON only, no markdown.",
                messages=[{"role": "user", "content": prompt}]
            )
            
            content = response.content[0].text.strip()
            # Handle potential markdown code blocks
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
                content = content.strip()
            
            return json.loads(content)
            
        except json.JSONDecodeError as e:
            logger.error(f"json_parse_error_{dimension}", error=str(e))
            raise ValueError(f"Failed to parse {dimension} analysis: {e}")
        except Exception as e:
            logger.error(f"extraction_error_{dimension}", error=str(e), exc_info=True)
            raise

    def extract_all_dimensions(
        self, 
        text_samples: List[str],
        progress_callback: Optional[Callable[[str, int, int], None]] = None
    ) -> Dict[str, Dict]:
        """Extract patterns for all dimensions"""
        results = {}
        dimensions = list(EXTRACTION_PROMPTS.keys())
        total = len(dimensions)
        
        for i, dimension in enumerate(dimensions):
            if progress_callback:
                progress_callback(DIMENSION_NAMES[dimension], i + 1, total)
            
            with PerformanceTimer(logger, f"extract_{dimension}"):
                results[dimension] = self.extract_dimension(dimension, text_samples)
            
            logger.info(f"dimension_extracted", 
                       dimension=dimension, 
                       confidence=results[dimension].get("confidence", 0))
        
        return results


class ProfileSynthesizer:
    """Pass 2: Synthesize raw patterns into coherent personality profile"""
    
    def __init__(self, client: Anthropic, model: str):
        self.client = client
        self.model = model
    
    def synthesize(self, raw_analyses: Dict[str, Dict]) -> Dict:
        """Synthesize all dimension analyses into a coherent profile"""
        formatted_analyses = json.dumps(raw_analyses, indent=2)
        prompt = SYNTHESIS_PROMPT.format(raw_analyses=formatted_analyses)
        
        logger.info("synthesizing_profile")
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                system="You are synthesizing a comprehensive personality profile. Be insightful and specific. Respond with valid JSON only.",
                messages=[{"role": "user", "content": prompt}]
            )
            
            content = response.content[0].text.strip()
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
                content = content.strip()
            
            return json.loads(content)
            
        except json.JSONDecodeError as e:
            logger.error("synthesis_json_error", error=str(e))
            raise ValueError(f"Failed to parse synthesis: {e}")
        except Exception as e:
            logger.error("synthesis_error", error=str(e), exc_info=True)
            raise
    
    def build_profile(
        self, 
        raw_analyses: Dict[str, Dict], 
        synthesis: Dict,
        metadata: AnalysisMetadata
    ) -> PersonalityProfile:
        """Build the final PersonalityProfile from raw data and synthesis"""
        
        # Build WritingStyleProfile
        ws = raw_analyses.get("writing_style", {})
        writing_style = WritingStyleProfile(
            rhythm=RhythmPattern(**ws.get("rhythm", {
                "pacing_description": "Unable to determine",
                "sentence_variation": "Unknown",
                "paragraph_style": "Unknown",
                "flow_characteristics": []
            })),
            stylistic_markers=StylisticMarkers(**ws.get("stylistic_markers", {
                "signature_phrases": [],
                "metaphor_patterns": [],
                "transition_style": "Unknown",
                "emphasis_patterns": [],
                "punctuation_habits": "Standard"
            })),
            tonal_range=TonalRange(**ws.get("tonal_range", {
                "default_tone": "Neutral",
                "tonal_shifts": {},
                "emotional_coloring": "Unknown",
                "formality_spectrum": "Unknown"
            })),
            linguistic_fingerprints=ws.get("linguistic_fingerprints", []),
            vocabulary_character=ws.get("vocabulary_character", "Unknown"),
            voice_description=ws.get("voice_description", "Unable to determine writing voice"),
            confidence=ws.get("confidence", 0.5)
        )
        
        # Build CognitiveProfile
        cog = raw_analyses.get("cognitive", {})
        cognitive = CognitiveProfile(
            reasoning_patterns=ReasoningPatterns(**cog.get("reasoning_patterns", {
                "primary_mode": "Mixed",
                "logical_style": "Unknown",
                "evidence_preference": "Unknown",
                "abstraction_level": "Unknown"
            })),
            mental_models=MentalModels(**cog.get("mental_models", {
                "identified_frameworks": [],
                "implicit_models": [],
                "analogical_sources": []
            })),
            problem_solving_style=cog.get("problem_solving_style", "Unknown"),
            idea_connection_style=cog.get("idea_connection_style", "Unknown"),
            learning_approach=cog.get("learning_approach", "Unknown"),
            complexity_preference=cog.get("complexity_preference", "Unknown"),
            thinking_description=cog.get("thinking_description", "Unable to determine thinking patterns"),
            confidence=cog.get("confidence", 0.5)
        )
        
        # Build EmotionalProfile
        emo = raw_analyses.get("emotional", {})
        emotional = EmotionalProfile(
            triggers=EmotionalTriggers(**emo.get("triggers", {
                "excites": [],
                "frustrates": [],
                "motivates": [],
                "calms": []
            })),
            passion_map=PassionMap(**emo.get("passion_map", {
                "high_passion": [],
                "moderate_interest": [],
                "emerging_curiosity": []
            })),
            expression_patterns=emo.get("expression_patterns", "Unknown"),
            emotional_vocabulary=emo.get("emotional_vocabulary", []),
            values_from_emotion=emo.get("values_from_emotion", []),
            emotional_baseline=emo.get("emotional_baseline", "Unknown"),
            emotional_description=emo.get("emotional_description", "Unable to determine emotional patterns"),
            confidence=emo.get("confidence", 0.5)
        )
        
        # Build InterestProfile
        int_data = raw_analyses.get("interests", {})
        genuine_interests = [
            Interest(**i) if isinstance(i, dict) else Interest(
                topic=str(i), depth=0.5, evidence=[], context="Unknown"
            )
            for i in int_data.get("genuine_interests", [])
        ]
        interests = InterestProfile(
            genuine_interests=genuine_interests,
            curiosities=int_data.get("curiosities", []),
            aspirations=int_data.get("aspirations", []),
            topic_affinities=int_data.get("topic_affinities", {}),
            learning_trajectories=int_data.get("learning_trajectories", []),
            interest_description=int_data.get("interest_description", "Unable to determine interests"),
            confidence=int_data.get("confidence", 0.5)
        )
        
        # Build WorldviewProfile
        wv = raw_analyses.get("worldview", {})
        worldview = WorldviewProfile(
            core_beliefs=CoreBeliefs(**wv.get("core_beliefs", {
                "explicit_beliefs": [],
                "implicit_assumptions": [],
                "values_hierarchy": []
            })),
            philosophical_leanings=wv.get("philosophical_leanings", []),
            framing_patterns=wv.get("framing_patterns", "Unknown"),
            unique_perspectives=wv.get("unique_perspectives", []),
            domain_lenses=wv.get("domain_lenses", {}),
            epistemology=wv.get("epistemology", "Unknown"),
            worldview_description=wv.get("worldview_description", "Unable to determine worldview"),
            confidence=wv.get("confidence", 0.5)
        )
        
        # Build SocialProfile
        soc = raw_analyses.get("social", {})
        social = SocialProfile(
            communication_dynamics=CommunicationDynamics(**soc.get("communication_dynamics", {
                "initiation_style": "Unknown",
                "response_patterns": "Unknown",
                "engagement_depth": "Unknown",
                "directness_level": "Unknown"
            })),
            collaboration_style=soc.get("collaboration_style", "Unknown"),
            authority_positioning=soc.get("authority_positioning", "Unknown"),
            audience_adaptation=soc.get("audience_adaptation", {}),
            relational_patterns=soc.get("relational_patterns", []),
            conflict_approach=soc.get("conflict_approach", "Unknown"),
            social_description=soc.get("social_description", "Unable to determine social patterns"),
            confidence=soc.get("confidence", 0.5)
        )
        
        # Calculate overall confidence
        confidences = [
            writing_style.confidence,
            cognitive.confidence,
            emotional.confidence,
            interests.confidence,
            worldview.confidence,
            social.confidence
        ]
        overall_confidence = sum(confidences) / len(confidences)
        
        return PersonalityProfile(
            version=2,
            writing_style=writing_style,
            cognitive=cognitive,
            emotional=emotional,
            interests=interests,
            worldview=worldview,
            social=social,
            personality_essence=synthesis.get("personality_essence", "Unable to synthesize personality essence"),
            key_characteristics=synthesis.get("key_characteristics", []),
            context_variations=synthesis.get("context_variations", {}),
            analysis_metadata=metadata,
            overall_confidence=overall_confidence
        )


class AnalysisOrchestrator:
    """Orchestrates the multi-pass personality analysis pipeline"""
    
    def __init__(
        self, 
        model: Optional[str] = None,
        batch_size: Optional[int] = None
    ):
        self.model = model or settings.ANTHROPIC_ANALYSIS_MODEL
        self.batch_size = batch_size or settings.ANALYSIS_BATCH_SIZE
        if not settings.ANTHROPIC_API_KEY or not settings.ANTHROPIC_API_KEY.strip():
            raise ValueError("ANTHROPIC_API_KEY not set. Add it to your .env file.")
        self.client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.extractor = PatternExtractor(self.client, self.model)
        self.synthesizer = ProfileSynthesizer(self.client, self.model)
    
    def analyze(
        self, 
        texts: List[str],
        progress_callback: Optional[Callable[[str, int, int], None]] = None
    ) -> PersonalityProfile:
        """
        Run complete personality analysis pipeline.
        
        Args:
            texts: List of text samples to analyze
            progress_callback: Optional callback(stage_name, current, total)
        
        Returns:
            Complete PersonalityProfile
        """
        if not texts:
            raise ValueError("Cannot analyze empty text list")
        
        start_time = time.time()
        total_chars = sum(len(t) for t in texts)
        estimated_tokens = total_chars // 4  # Rough estimate
        
        logger.info("analysis_started", 
                   text_count=len(texts), 
                   estimated_tokens=estimated_tokens,
                   model=self.model)
        
        # Batch texts if needed for very large datasets
        sample_texts = self._select_representative_samples(texts)
        
        # Pass 1: Extract patterns for each dimension
        if progress_callback:
            progress_callback("Starting pattern extraction", 0, 8)
        
        with PerformanceTimer(logger, "pass1_extraction", sample_count=len(sample_texts)):
            raw_analyses = self.extractor.extract_all_dimensions(
                sample_texts, 
                progress_callback
            )
        
        # Pass 2: Synthesize into coherent profile
        if progress_callback:
            progress_callback("Synthesizing personality profile", 7, 8)
        
        with PerformanceTimer(logger, "pass2_synthesis"):
            synthesis = self.synthesizer.synthesize(raw_analyses)
        
        # Build final profile
        duration = time.time() - start_time
        metadata = AnalysisMetadata(
            documents_analyzed=len(texts),
            total_tokens_analyzed=estimated_tokens,
            analysis_duration_seconds=duration,
            model_used=self.model
        )
        
        profile = self.synthesizer.build_profile(raw_analyses, synthesis, metadata)
        
        if progress_callback:
            progress_callback("Analysis complete", 8, 8)
        
        logger.info("analysis_complete", 
                   duration_seconds=duration,
                   overall_confidence=profile.overall_confidence)
        
        return profile
    
    def _select_representative_samples(
        self, 
        texts: List[str], 
        max_samples: int = 50,
        max_chars_per_sample: int = 3000
    ) -> List[str]:
        """
        Select representative samples from texts.
        Prioritizes diversity and quality over quantity.
        """
        if len(texts) <= max_samples:
            return [t[:max_chars_per_sample] for t in texts if t.strip()]
        
        # Simple sampling: take evenly spaced samples
        step = len(texts) // max_samples
        samples = []
        for i in range(0, len(texts), step):
            if len(samples) >= max_samples:
                break
            text = texts[i].strip()
            if text:
                samples.append(text[:max_chars_per_sample])
        
        logger.debug("samples_selected", 
                    original_count=len(texts), 
                    selected_count=len(samples))
        
        return samples
    
    def analyze_incrementally(
        self,
        texts: List[str],
        existing_profile: Optional[PersonalityProfile] = None,
        progress_callback: Optional[Callable[[str, int, int], None]] = None
    ) -> PersonalityProfile:
        """
        Analyze new texts, optionally incorporating existing profile.
        For now, this just runs fresh analysis. Future: blend with existing.
        """
        # TODO: Implement incremental analysis that blends new insights with existing profile
        return self.analyze(texts, progress_callback)


# Convenience function for simple usage
def analyze_personality(texts: List[str]) -> PersonalityProfile:
    """Analyze texts and return a PersonalityProfile"""
    orchestrator = AnalysisOrchestrator()
    return orchestrator.analyze(texts)

