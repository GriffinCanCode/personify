from typing import List, Dict, Optional
from backend.vectorstore.store import vector_store
from backend.vectorstore.embeddings import get_embedding
from backend.config import settings
from backend.logging_config import get_logger, PerformanceTimer

logger = get_logger(__name__)

class RetrieverStrategy:
    """Manages different retrieval strategies for RAG"""
    
    def __init__(self, k: int = None):
        self.k = k or settings.RETRIEVAL_K
        logger.debug("retriever_strategy_initialized", default_k=self.k)
    
    def retrieve(
        self,
        query: str,
        context_filter: Optional[Dict] = None,
        k: Optional[int] = None
    ) -> List[Dict]:
        """
        Retrieve most relevant chunks for a query.
        
        Returns list of dicts with:
        - content: The chunk text
        - metadata: Associated metadata
        - distance: Similarity score
        """
        k = k or self.k
        
        logger.debug("retrieve_started", query_length=len(query), k=k, has_filter=context_filter is not None)
        
        try:
            with PerformanceTimer(logger, "retrieve_chunks", k=k):
                results = vector_store.query(
                    query_texts=[query],
                    n_results=k,
                    where=context_filter
                )
            
            retrieved = []
            for i in range(len(results['documents'][0])):
                retrieved.append({
                    'content': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'distance': results['distances'][0][i] if 'distances' in results else None,
                    'id': results['ids'][0][i]
                })
            
            logger.info("retrieve_completed", retrieved_count=len(retrieved), k=k)
            return retrieved
        except Exception as e:
            logger.error("retrieve_error", query_length=len(query), k=k, error=str(e), exc_info=True)
            raise
    
    def retrieve_with_diversity(
        self,
        query: str,
        k: int = None,
        diversity_threshold: float = 0.8
    ) -> List[Dict]:
        """
        Retrieve diverse examples to avoid redundancy.
        Uses MMR (Maximal Marginal Relevance) approach.
        """
        k = k or self.k
        
        logger.debug("retrieve_with_diversity_started", query_length=len(query), k=k)
        
        try:
            with PerformanceTimer(logger, "retrieve_with_diversity", k=k):
                # Get more results than needed
                results = self.retrieve(query, k=k * 2)
                
                if not results:
                    logger.info("no_results_for_diversity_retrieval")
                    return []
                
                # Select first result
                selected = [results[0]]
                remaining = results[1:]
                
                while len(selected) < k and remaining:
                    # Find most diverse result from remaining
                    best_idx = 0
                    best_score = -float('inf')
                    
                    for idx, candidate in enumerate(remaining):
                        # Calculate diversity score (simplified)
                        min_similarity = min(
                            self._similarity(candidate['content'], sel['content'])
                            for sel in selected
                        )
                        
                        # Balance relevance and diversity
                        score = candidate.get('distance', 0) - (1 - min_similarity)
                        
                        if score > best_score:
                            best_score = score
                            best_idx = idx
                    
                    selected.append(remaining.pop(best_idx))
            
            logger.info("retrieve_with_diversity_completed", selected_count=len(selected[:k]), k=k)
            return selected[:k]
        except Exception as e:
            logger.error("retrieve_with_diversity_error", k=k, error=str(e), exc_info=True)
            raise
    
    def retrieve_by_context(
        self,
        query: str,
        source_type: Optional[str] = None,
        date_range: Optional[Dict] = None,
        k: int = None
    ) -> List[Dict]:
        """Retrieve with metadata filtering"""
        k = k or self.k
        
        where_filter = {}
        if source_type:
            where_filter['source_type'] = source_type
        
        # Note: ChromaDB has limited date filtering, may need custom logic
        
        return self.retrieve(query, context_filter=where_filter if where_filter else None, k=k)
    
    def _similarity(self, text1: str, text2: str) -> float:
        """Calculate simple similarity between texts (word overlap)"""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        
        return intersection / union if union > 0 else 0.0

# Singleton instance
retriever = RetrieverStrategy()

