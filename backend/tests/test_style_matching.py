import pytest
from backend.evaluation.metrics import StyleMetrics, QualityMetrics

def test_vocabulary_overlap():
    text1 = "The quick brown fox jumps over the lazy dog"
    text2 = "The quick red fox runs over the sleepy dog"
    
    score = StyleMetrics.vocabulary_overlap(text1, text2)
    assert 0.0 <= score <= 1.0
    assert score > 0.5  # Should have good overlap

def test_sentence_length_similarity():
    text1 = "This is a short sentence. This is another one."
    text2 = "Here is a brief sentence. And here is one more."
    
    score = StyleMetrics.sentence_length_similarity(text1, text2)
    assert 0.0 <= score <= 1.0
    assert score > 0.7  # Similar lengths

def test_phrase_similarity():
    text1 = "I think that this is a good idea for the project"
    text2 = "I think this is a great concept for the work"
    
    score = StyleMetrics.phrase_similarity(text1, text2)
    assert 0.0 <= score <= 1.0
    assert score > 0.0  # Should have some phrase overlap

def test_coherence_score():
    coherent_text = "This is a complete sentence. Here is another one. And a third."
    score = QualityMetrics.coherence_score(coherent_text)
    assert score > 0.8
    
    incoherent_text = "word word word"
    score = QualityMetrics.coherence_score(incoherent_text)
    assert score < 0.5

def test_relevance_score():
    query = "What is machine learning?"
    relevant = "Machine learning is a type of artificial intelligence"
    irrelevant = "The weather is nice today"
    
    rel_score = QualityMetrics.relevance_score(relevant, query)
    irrel_score = QualityMetrics.relevance_score(irrelevant, query)
    
    assert rel_score > irrel_score

def test_completeness_score():
    complete = "This is a complete response with proper ending."
    incomplete = "This is an incomplete"
    
    complete_score = QualityMetrics.completeness_score(complete)
    incomplete_score = QualityMetrics.completeness_score(incomplete)
    
    assert complete_score > incomplete_score

