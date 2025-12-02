import re
from typing import Dict
from backend.personality.profile import PersonalityProfile


class ResponseValidator:
    """Validate that responses match the personality profile's style"""
    
    def __init__(self, personality_profile: PersonalityProfile):
        self.profile = personality_profile
    
    def validate(self, response: str) -> Dict:
        """
        Validate response and return confidence metrics.
        
        Returns:
        - confidence_score: 0-1 overall confidence
        - style_match: 0-1 how well it matches style
        - issues: list of potential issues
        """
        issues = []
        style = self.profile.writing_style
        
        # Check for signature phrases usage
        signature_phrases = style.stylistic_markers.signature_phrases[:10]
        has_signature_phrase = any(
            phrase.lower() in response.lower() 
            for phrase in signature_phrases
        ) if signature_phrases else False
        
        # Check formality matches based on tonal range
        formality_spec = style.tonal_range.formality_spectrum.lower()
        formal_words = ['furthermore', 'moreover', 'consequently', 'therefore', 'thus']
        casual_words = ['gonna', 'wanna', 'yeah', 'kinda', 'sorta', 'btw']
        
        formal_count = sum(1 for word in formal_words if word in response.lower())
        casual_count = sum(1 for word in casual_words if word in response.lower())
        
        # Determine expected formality from spectrum description
        is_formal = any(x in formality_spec for x in ['formal', 'professional', 'academic'])
        is_casual = any(x in formality_spec for x in ['casual', 'informal', 'relaxed'])
        
        if is_casual and formal_count > 2:
            issues.append("Response too formal for profile's casual style")
        elif is_formal and casual_count > 2:
            issues.append("Response too casual for profile's formal style")
        
        # Check for meta-commentary (shouldn't say "Griffin would...")
        meta_phrases = [
            'griffin would', 'as griffin', 'griffin thinks', 
            'griffin believes', 'speaking as griffin', 'in griffin\'s style'
        ]
        if any(phrase in response.lower() for phrase in meta_phrases):
            issues.append("Contains meta-commentary (should BE the person, not describe them)")
        
        # Check tonal alignment
        tone = style.tonal_range.default_tone.lower()
        if 'serious' in tone or 'professional' in tone:
            humor_indicators = ['lol', 'haha', '😂', '😄', 'rofl', 'lmao']
            if sum(1 for h in humor_indicators if h in response.lower()) > 2:
                issues.append("Excessive humor doesn't match profile's serious tone")
        
        # Check sentence variation if rhythm indicates varied sentences
        sentences = re.split(r'[.!?]+', response)
        sentences = [s.strip() for s in sentences if s.strip()]
        if sentences and len(sentences) > 3:
            lengths = [len(s.split()) for s in sentences]
            variation = max(lengths) - min(lengths) if lengths else 0
            
            rhythm_desc = style.rhythm.sentence_variation.lower()
            if 'varied' in rhythm_desc or 'rhythmic' in rhythm_desc:
                if variation < 3:
                    issues.append("Sentences too uniform - profile indicates varied rhythm")
            elif 'uniform' in rhythm_desc:
                if variation > 10:
                    issues.append("Sentences too varied - profile indicates uniform rhythm")
        
        # Calculate confidence score
        confidence_score = 1.0
        confidence_score -= len(issues) * 0.15
        confidence_score = max(0.0, min(1.0, confidence_score))
        
        # Style match score
        style_match = 0.75  # Base score
        if has_signature_phrase:
            style_match += 0.15
        if len(issues) == 0:
            style_match += 0.1
        
        style_match = min(1.0, style_match)
        
        return {
            'confidence_score': confidence_score,
            'style_match': style_match,
            'issues': issues,
            'is_valid': confidence_score > 0.5
        }
