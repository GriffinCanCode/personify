import re
from typing import Dict
from backend.personality.profile import PersonalityProfile

class ResponseValidator:
    """Validate that responses match Griffin's style"""
    
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
        
        # Check sentence length matches
        sentences = re.split(r'[.!?]+', response)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if sentences:
            avg_sent_len = sum(len(s.split()) for s in sentences) / len(sentences)
            target_len = self.profile.communication_style.avg_sentence_length
            
            # Allow 50% deviation
            if abs(avg_sent_len - target_len) > target_len * 0.5:
                issues.append(f"Sentence length mismatch: {avg_sent_len:.1f} vs {target_len:.1f}")
        
        # Check for common phrases
        has_common_phrase = any(
            phrase in response.lower() 
            for phrase in self.profile.communication_style.common_phrases[:5]
        )
        
        # Check formality matches
        formal_words = ['furthermore', 'moreover', 'consequently', 'therefore']
        casual_words = ['gonna', 'wanna', 'yeah', 'kinda', 'sorta']
        
        formal_count = sum(1 for word in formal_words if word in response.lower())
        casual_count = sum(1 for word in casual_words if word in response.lower())
        
        target_formality = self.profile.communication_style.formality
        
        if target_formality < 0.4 and formal_count > 2:
            issues.append("Too formal for Griffin's style")
        elif target_formality > 0.7 and casual_count > 2:
            issues.append("Too casual for Griffin's style")
        
        # Check for meta-commentary (shouldn't say "Griffin would...")
        meta_phrases = [
            'griffin would', 'as griffin', 'griffin thinks', 
            'griffin believes', 'speaking as griffin'
        ]
        if any(phrase in response.lower() for phrase in meta_phrases):
            issues.append("Contains meta-commentary (should BE Griffin, not describe him)")
        
        # Calculate confidence score
        confidence_score = 1.0
        confidence_score -= len(issues) * 0.15  # Deduct for each issue
        confidence_score = max(0.0, min(1.0, confidence_score))
        
        # Style match score (simplified)
        style_match = 0.8  # Base score
        if has_common_phrase:
            style_match += 0.1
        if len(issues) == 0:
            style_match += 0.1
        
        style_match = min(1.0, style_match)
        
        return {
            'confidence_score': confidence_score,
            'style_match': style_match,
            'issues': issues,
            'is_valid': confidence_score > 0.5
        }

