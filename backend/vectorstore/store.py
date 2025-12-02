import chromadb
from chromadb.config import Settings
from typing import List, Dict, Optional
from backend.config import settings as app_settings
from backend.logging_config import get_logger, PerformanceTimer

logger = get_logger(__name__)

class VectorStore:
    def __init__(self):
        logger.info("initializing_vector_store", persist_dir=app_settings.CHROMA_PERSIST_DIR)
        
        self.client = chromadb.PersistentClient(
            path=app_settings.CHROMA_PERSIST_DIR,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        self.collection = self.client.get_or_create_collection(
            name="griffin_documents",
            metadata={"description": "Griffin's personal documents and communications"}
        )
        
        logger.info("vector_store_initialized", collection_name="griffin_documents")
    
    def add_chunks(
        self,
        ids: List[str],
        documents: List[str],
        metadatas: List[Dict],
        embeddings: Optional[List[List[float]]] = None
    ):
        """Add chunks to vector store"""
        logger.info("adding_chunks_to_vector_store", chunk_count=len(ids), has_embeddings=embeddings is not None)
        
        try:
            with PerformanceTimer(logger, "add_chunks_to_chroma", chunk_count=len(ids)):
                if embeddings:
                    self.collection.add(
                        ids=ids,
                        documents=documents,
                        metadatas=metadatas,
                        embeddings=embeddings
                    )
                else:
                    self.collection.add(
                        ids=ids,
                        documents=documents,
                        metadatas=metadatas
                    )
            
            logger.info("chunks_added_successfully", chunk_count=len(ids))
        except Exception as e:
            logger.error("chunk_add_error", chunk_count=len(ids), error=str(e), exc_info=True)
            raise
    
    def query(
        self,
        query_texts: Optional[List[str]] = None,
        query_embeddings: Optional[List[List[float]]] = None,
        n_results: int = 5,
        where: Optional[Dict] = None,
        where_document: Optional[Dict] = None
    ):
        """Query vector store for similar documents"""
        logger.debug(
            "querying_vector_store",
            n_results=n_results,
            has_where_filter=where is not None,
            has_query_texts=query_texts is not None
        )
        
        try:
            with PerformanceTimer(logger, "vector_store_query", n_results=n_results):
                results = self.collection.query(
                    query_texts=query_texts,
                    query_embeddings=query_embeddings,
                    n_results=n_results,
                    where=where,
                    where_document=where_document
                )
            
            results_count = len(results['documents'][0]) if results.get('documents') else 0
            logger.debug("vector_store_query_completed", results_returned=results_count)
            return results
        except Exception as e:
            logger.error("vector_store_query_error", error=str(e), exc_info=True)
            raise
    
    def get(self, ids: List[str]):
        """Get specific chunks by ID"""
        logger.debug("getting_chunks_by_id", chunk_count=len(ids))
        try:
            results = self.collection.get(ids=ids)
            logger.debug("chunks_retrieved_by_id", chunk_count=len(ids))
            return results
        except Exception as e:
            logger.error("chunk_get_error", chunk_count=len(ids), error=str(e), exc_info=True)
            raise
    
    def delete(self, ids: List[str]):
        """Delete chunks from vector store"""
        logger.info("deleting_chunks", chunk_count=len(ids))
        try:
            self.collection.delete(ids=ids)
            logger.info("chunks_deleted", chunk_count=len(ids))
        except Exception as e:
            logger.error("chunk_delete_error", chunk_count=len(ids), error=str(e), exc_info=True)
            raise
    
    def count(self) -> int:
        """Get total number of chunks in collection"""
        try:
            count = self.collection.count()
            logger.debug("vector_store_count", total_chunks=count)
            return count
        except Exception as e:
            logger.error("vector_store_count_error", error=str(e), exc_info=True)
            raise

# Singleton instance
vector_store = VectorStore()

