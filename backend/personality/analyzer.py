import re
from typing import List, Dict
from collections import Counter
import textstat
from backend.personality.profile import (
    PersonalityProfile, CommunicationStyle, PersonalityTraits, DecisionPatterns
)

class StyleAnalyzer:
    """Analyze writing style from text samples"""
    
    @staticmethod
    def analyze_communication_style(texts: List[str]) -> CommunicationStyle:
        """Analyze communication style from text samples"""
        all_text = ' '.join(texts)
        
        # Sentence analysis
        sentences = re.split(r'[.!?]+', all_text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        words = all_text.split()
        
        avg_sentence_length = sum(len(s.split()) for s in sentences) / max(len(sentences), 1)
        avg_word_length = sum(len(w) for w in words) / max(len(words), 1)
        
        # Formality (based on vocabulary complexity)
        formality = min(textstat.flesch_reading_ease(all_text) / 100, 1.0)
        formality = 1.0 - formality  # Invert: higher score = more formal
        
        # Directness (shorter sentences = more direct)
        directness = max(0.0, min(1.0, 1.0 - (avg_sentence_length / 30)))
        
        # Verbosity (longer texts = more verbose)
        verbosity = min(avg_sentence_length / 25, 1.0)
        
        # Humor detection (basic: exclamation marks, specific words)
        humor_indicators = ['!', 'lol', 'haha', 'funny', '😂', '😄']
        humor_count = sum(all_text.lower().count(ind) for ind in humor_indicators)
        humor = min(humor_count / (len(texts) * 2), 1.0)
        
        # Common phrases (2-3 word sequences)
        phrases = StyleAnalyzer._extract_common_phrases(texts)
        
        # Vocabulary level
        vocab_level = StyleAnalyzer._assess_vocabulary(all_text)
        
        # Sentence structure description
        sentence_structure = StyleAnalyzer._describe_sentence_structure(avg_sentence_length, sentences)
        
        return CommunicationStyle(
            formality=formality,
            directness=directness,
            verbosity=verbosity,
            humor=humor,
            common_phrases=phrases,
            sentence_structure=sentence_structure,
            vocabulary_level=vocab_level,
            avg_sentence_length=avg_sentence_length,
            avg_word_length=avg_word_length
        )
    
    @staticmethod
    def _extract_common_phrases(texts: List[str], top_n: int = 20) -> List[str]:
        """Extract commonly used phrases"""
        # Extract 2-3 word phrases
        all_phrases = []
        
        for text in texts:
            words = text.lower().split()
            for i in range(len(words) - 1):
                # 2-word phrases
                phrase = ' '.join(words[i:i+2])
                if len(phrase) > 5:  # Filter very short phrases
                    all_phrases.append(phrase)
                
                # 3-word phrases
                if i < len(words) - 2:
                    phrase = ' '.join(words[i:i+3])
                    if len(phrase) > 8:
                        all_phrases.append(phrase)
        
        # Count and filter
        phrase_counts = Counter(all_phrases)
        
        # Filter out common generic phrases
        stop_phrases = {'a lot of', 'in the', 'to the', 'of the', 'for the'}
        
        filtered = [(p, c) for p, c in phrase_counts.items() 
                   if c > 1 and p not in stop_phrases]
        
        top_phrases = sorted(filtered, key=lambda x: x[1], reverse=True)[:top_n]
        
        return [phrase for phrase, _ in top_phrases]
    
    @staticmethod
    def _assess_vocabulary(text: str) -> str:
        """Assess vocabulary sophistication"""
        score = textstat.flesch_reading_ease(text)
        
        if score > 80:
            return "Simple and accessible"
        elif score > 60:
            return "Clear and conversational"
        elif score > 50:
            return "Professional and precise"
        else:
            return "Complex and sophisticated"
    
    @staticmethod
    def _describe_sentence_structure(avg_length: float, sentences: List[str]) -> str:
        """Describe sentence structure patterns"""
        if avg_length < 12:
            return "Short, punchy sentences"
        elif avg_length < 20:
            return "Medium-length, balanced sentences"
        else:
            return "Long, complex sentences"

class PersonalityAnalyzer:
    """Analyze personality traits from writing"""
    
    @staticmethod
    def analyze_traits(texts: List[str], communication_style: CommunicationStyle) -> PersonalityTraits:
        """Estimate personality traits from writing patterns"""
        all_text = ' '.join(texts).lower()
        
        # Openness (creativity, abstract thinking)
        openness_words = ['creative', 'imagine', 'innovative', 'unique', 'artistic', 'abstract']
        openness_score = sum(all_text.count(w) for w in openness_words) / max(len(texts), 1)
        openness = min(openness_score * 0.1 + 0.5, 1.0)
        
        # Conscientiousness (organization, planning)
        conscientiousness_words = ['plan', 'organize', 'schedule', 'prepare', 'detail', 'systematic']
        conscientiousness_score = sum(all_text.count(w) for w in conscientiousness_words) / max(len(texts), 1)
        conscientiousness = min(conscientiousness_score * 0.1 + 0.5, 1.0)
        
        # Extraversion (social energy)
        extraversion_words = ['excited', 'people', 'social', 'fun', 'party', 'friends']
        extraversion_score = sum(all_text.count(w) for w in extraversion_words) / max(len(texts), 1)
        extraversion = min(extraversion_score * 0.1 + 0.5, 1.0)
        
        # Agreeableness (cooperation, empathy)
        agreeableness_words = ['help', 'kind', 'care', 'understand', 'support', 'appreciate']
        agreeableness_score = sum(all_text.count(w) for w in agreeableness_words) / max(len(texts), 1)
        agreeableness = min(agreeableness_score * 0.1 + 0.5, 1.0)
        
        # Emotional Stability
        instability_words = ['worried', 'anxious', 'stressed', 'upset', 'frustrated', 'angry']
        instability_score = sum(all_text.count(w) for w in instability_words) / max(len(texts), 1)
        emotional_stability = max(0.5 - instability_score * 0.1, 0.0)
        
        return PersonalityTraits(
            openness=openness,
            conscientiousness=conscientiousness,
            extraversion=extraversion,
            agreeableness=agreeableness,
            emotional_stability=emotional_stability
        )
    
    @staticmethod
    def extract_values(texts: List[str]) -> List[str]:
        """Extract apparent values from writing"""
        all_text = ' '.join(texts).lower()
        
        value_keywords = {
            'Authenticity': ['authentic', 'genuine', 'honest', 'real', 'true'],
            'Efficiency': ['efficient', 'optimize', 'streamline', 'productive', 'fast'],
            'Creativity': ['creative', 'innovative', 'original', 'artistic', 'imagination'],
            'Growth': ['learn', 'grow', 'improve', 'develop', 'progress'],
            'Quality': ['quality', 'excellence', 'best', 'perfect', 'outstanding'],
            'Connection': ['connect', 'relationship', 'together', 'community', 'collaborate'],
            'Independence': ['independent', 'autonomous', 'self', 'freedom', 'own'],
            'Knowledge': ['knowledge', 'understand', 'learn', 'wisdom', 'insight'],
        }
        
        value_scores = {}
        for value, keywords in value_keywords.items():
            score = sum(all_text.count(kw) for kw in keywords)
            value_scores[value] = score
        
        sorted_values = sorted(value_scores.items(), key=lambda x: x[1], reverse=True)
        return [value for value, score in sorted_values if score > 0][:7]
    
    @staticmethod
    def extract_knowledge_domains(texts: List[str]) -> Dict[str, List[str]]:
        """Extract topics that appear to be knowledge domains"""
        # This is a simplified version - could use topic modeling for better results
        all_text = ' '.join(texts).lower()
        
        # Common domain keywords
        domains = {
            'Technology': ['software', 'code', 'programming', 'computer', 'tech', 'ai', 'algorithm'],
            'Business': ['business', 'market', 'strategy', 'revenue', 'customer', 'sales'],
            'Psychology': ['psychology', 'behavior', 'emotion', 'mental', 'cognitive'],
            'Writing': ['writing', 'story', 'narrative', 'essay', 'article', 'prose'],
            'Design': ['design', 'visual', 'aesthetic', 'ui', 'ux', 'interface'],
            'Science': ['research', 'study', 'experiment', 'data', 'analysis', 'theory'],
        }
        
        domain_scores = {}
        for domain, keywords in domains.items():
            score = sum(all_text.count(kw) for kw in keywords)
            if score > 5:  # Threshold for expertise
                domain_scores[domain] = 'expert'
            elif score > 2:
                domain_scores[domain] = 'competent'
        
        # Group by level
        expert = [d for d, l in domain_scores.items() if l == 'expert']
        competent = [d for d, l in domain_scores.items() if l == 'competent']
        
        return {
            'expert': expert,
            'competent': competent,
            'learning': []
        }
    
    @staticmethod
    def analyze_decision_patterns(texts: List[str]) -> DecisionPatterns:
        """Analyze decision-making patterns"""
        all_text = ' '.join(texts).lower()
        
        # Analytical vs Intuitive
        analytical_words = ['analyze', 'data', 'evidence', 'research', 'logic', 'reason']
        intuitive_words = ['feel', 'sense', 'gut', 'instinct', 'intuition']
        
        analytical_score = sum(all_text.count(w) for w in analytical_words)
        intuitive_score = sum(all_text.count(w) for w in intuitive_words)
        
        total = analytical_score + intuitive_score + 1
        analytical_ratio = analytical_score / total
        
        # Risk tolerance
        risk_words = ['risk', 'bold', 'try', 'experiment', 'venture']
        safe_words = ['safe', 'careful', 'cautious', 'conservative', 'secure']
        
        risk_score = sum(all_text.count(w) for w in risk_words)
        safe_score = sum(all_text.count(w) for w in safe_words)
        
        risk_total = risk_score + safe_score + 1
        risk_tolerance = risk_score / risk_total
        
        # Time preference (simple heuristic)
        time_pref = "varies"
        if 'quick' in all_text or 'fast' in all_text:
            time_pref = "quick"
        elif 'careful' in all_text or 'thorough' in all_text:
            time_pref = "deliberate"
        
        return DecisionPatterns(
            analytical_vs_intuitive=analytical_ratio,
            risk_tolerance=risk_tolerance,
            time_preference=time_pref
        )

class ProfileBuilder:
    """Build complete personality profile from data"""
    
    @staticmethod
    def build_profile(texts: List[str]) -> PersonalityProfile:
        """Build complete personality profile from text samples"""
        if not texts:
            raise ValueError("Cannot build profile from empty texts")
        
        # Analyze communication style
        communication_style = StyleAnalyzer.analyze_communication_style(texts)
        
        # Analyze personality traits
        personality_traits = PersonalityAnalyzer.analyze_traits(texts, communication_style)
        
        # Extract values
        values = PersonalityAnalyzer.extract_values(texts)
        
        # Extract knowledge domains
        knowledge_domains = PersonalityAnalyzer.extract_knowledge_domains(texts)
        
        # Analyze decision patterns
        decision_patterns = PersonalityAnalyzer.analyze_decision_patterns(texts)
        
        # Context adaptations (placeholder for now)
        context_adaptations = {
            'professional': {},
            'personal': {},
            'creative': {}
        }
        
        return PersonalityProfile(
            version=1,
            communication_style=communication_style,
            personality_traits=personality_traits,
            values_hierarchy=values,
            knowledge_domains=knowledge_domains,
            decision_patterns=decision_patterns,
            context_adaptations=context_adaptations
        )

