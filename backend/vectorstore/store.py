import chromadb
from chromadb.config import Settings
from typing import List, Dict, Optional
from backend.config import settings as app_settings

class VectorStore:
    def __init__(self):
        self.client = chromadb.PersistentClient(
            path=app_settings.CHROMA_PERSIST_DIR,
            settings=Settings(anonymized_telemetry=False)
        )
        self.collection = self.client.get_or_create_collection(
            name="griffin_documents",
            metadata={"description": "Griffin's personal documents and communications"}
        )
    
    def add_chunks(
        self,
        ids: List[str],
        documents: List[str],
        metadatas: List[Dict],
        embeddings: Optional[List[List[float]]] = None
    ):
        """Add chunks to vector store"""
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
    
    def query(
        self,
        query_texts: Optional[List[str]] = None,
        query_embeddings: Optional[List[List[float]]] = None,
        n_results: int = 5,
        where: Optional[Dict] = None,
        where_document: Optional[Dict] = None
    ):
        """Query vector store for similar documents"""
        return self.collection.query(
            query_texts=query_texts,
            query_embeddings=query_embeddings,
            n_results=n_results,
            where=where,
            where_document=where_document
        )
    
    def get(self, ids: List[str]):
        """Get specific chunks by ID"""
        return self.collection.get(ids=ids)
    
    def delete(self, ids: List[str]):
        """Delete chunks from vector store"""
        self.collection.delete(ids=ids)
    
    def count(self) -> int:
        """Get total number of chunks in collection"""
        return self.collection.count()

# Singleton instance
vector_store = VectorStore()

