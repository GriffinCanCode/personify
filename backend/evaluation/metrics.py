from typing import List, Dict
import re
from collections import Counter
from sklearn.metrics.pairwise import cosine_similarity
from backend.vectorstore.embeddings import get_embedding

class StyleMetrics:
    """Metrics for evaluating style match"""
    
    @staticmethod
    def vocabulary_overlap(text1: str, text2: str) -> float:
        """Calculate vocabulary overlap between two texts"""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        
        return intersection / union if union > 0 else 0.0
    
    @staticmethod
    def sentence_length_similarity(text1: str, text2: str) -> float:
        """Compare sentence lengths between two texts"""
        sentences1 = re.split(r'[.!?]+', text1)
        sentences2 = re.split(r'[.!?]+', text2)
        
        sentences1 = [s.strip() for s in sentences1 if s.strip()]
        sentences2 = [s.strip() for s in sentences2 if s.strip()]
        
        if not sentences1 or not sentences2:
            return 0.0
        
        avg_len1 = sum(len(s.split()) for s in sentences1) / len(sentences1)
        avg_len2 = sum(len(s.split()) for s in sentences2) / len(sentences2)
        
        # Normalized difference (0 = identical, 1 = very different)
        diff = abs(avg_len1 - avg_len2) / max(avg_len1, avg_len2)
        
        # Invert so 1 = identical
        return 1.0 - min(diff, 1.0)
    
    @staticmethod
    def phrase_similarity(text1: str, text2: str) -> float:
        """Compare common phrases between texts"""
        # Extract 2-3 word phrases
        def extract_phrases(text):
            words = text.lower().split()
            phrases = []
            for i in range(len(words) - 1):
                phrases.append(' '.join(words[i:i+2]))
                if i < len(words) - 2:
                    phrases.append(' '.join(words[i:i+3]))
            return phrases
        
        phrases1 = extract_phrases(text1)
        phrases2 = extract_phrases(text2)
        
        if not phrases1 or not phrases2:
            return 0.0
        
        phrases1_set = set(phrases1)
        phrases2_set = set(phrases2)
        
        intersection = len(phrases1_set & phrases2_set)
        union = len(phrases1_set | phrases2_set)
        
        return intersection / union if union > 0 else 0.0
    
    @staticmethod
    def semantic_similarity(text1: str, text2: str) -> float:
        """Calculate semantic similarity using embeddings"""
        try:
            emb1 = get_embedding(text1)
            emb2 = get_embedding(text2)
            
            similarity = cosine_similarity([emb1], [emb2])[0][0]
            return float(similarity)
        except:
            return 0.0
    
    @staticmethod
    def overall_style_match(generated: str, reference_texts: List[str]) -> Dict[str, float]:
        """
        Calculate overall style match between generated text and reference texts.
        
        Returns dict with individual and composite scores.
        """
        if not reference_texts:
            return {'composite_score': 0.0}
        
        # Average scores across all reference texts
        vocab_scores = []
        length_scores = []
        phrase_scores = []
        semantic_scores = []
        
        for ref in reference_texts[:5]:  # Limit to 5 references
            vocab_scores.append(StyleMetrics.vocabulary_overlap(generated, ref))
            length_scores.append(StyleMetrics.sentence_length_similarity(generated, ref))
            phrase_scores.append(StyleMetrics.phrase_similarity(generated, ref))
            semantic_scores.append(StyleMetrics.semantic_similarity(generated, ref))
        
        avg_vocab = sum(vocab_scores) / len(vocab_scores)
        avg_length = sum(length_scores) / len(length_scores)
        avg_phrase = sum(phrase_scores) / len(phrase_scores)
        avg_semantic = sum(semantic_scores) / len(semantic_scores)
        
        # Weighted composite score
        composite = (
            avg_vocab * 0.2 +
            avg_length * 0.2 +
            avg_phrase * 0.3 +
            avg_semantic * 0.3
        )
        
        return {
            'vocabulary_overlap': avg_vocab,
            'sentence_length_similarity': avg_length,
            'phrase_similarity': avg_phrase,
            'semantic_similarity': avg_semantic,
            'composite_score': composite
        }

class QualityMetrics:
    """Metrics for evaluating response quality"""
    
    @staticmethod
    def coherence_score(text: str) -> float:
        """Basic coherence check"""
        # Check for complete sentences
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if not sentences:
            return 0.0
        
        # Check each sentence has reasonable length
        valid_sentences = [s for s in sentences if 3 <= len(s.split()) <= 50]
        
        return len(valid_sentences) / len(sentences)
    
    @staticmethod
    def relevance_score(response: str, query: str) -> float:
        """Check if response is relevant to query"""
        # Extract key words from query
        query_words = set(query.lower().split())
        response_words = set(response.lower().split())
        
        # Remove common words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for'}
        query_words = query_words - stop_words
        
        if not query_words:
            return 0.5  # Neutral score
        
        # Calculate overlap
        overlap = len(query_words & response_words)
        
        return min(overlap / len(query_words), 1.0)
    
    @staticmethod
    def completeness_score(response: str) -> float:
        """Check if response is complete"""
        # Basic checks
        if len(response.strip()) < 10:
            return 0.0
        
        # Check doesn't end mid-sentence
        ends_properly = response.strip()[-1] in '.!?'
        
        # Check has reasonable length
        word_count = len(response.split())
        length_score = min(word_count / 50, 1.0)  # Ideal 50+ words
        
        return (0.5 if ends_properly else 0.2) + (length_score * 0.5)

