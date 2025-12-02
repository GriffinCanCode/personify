"""
Background processing for document ingestion.
Dramatically improves upload speed by processing files asynchronously.
"""
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Optional
from datetime import datetime

from sqlalchemy.orm import Session
from backend.database.connection import SessionLocal
from backend.database.models import Document, Chunk
from backend.ingestion.parsers import ParserFactory, compute_content_hash
from backend.ingestion.processors import TextProcessor
from backend.ingestion.metadata_extractor import MetadataExtractor
from backend.vectorstore.embeddings import semantic_chunk_text, get_embeddings
from backend.vectorstore.store import vector_store
from backend.logging_config import get_logger, PerformanceTimer

logger = get_logger(__name__)

# Thread pool for background processing
_executor = ThreadPoolExecutor(max_workers=4)

# Track processing status
_processing_status: Dict[int, Dict] = {}


def get_document_status(document_id: int) -> Optional[Dict]:
    """Get processing status for a document"""
    return _processing_status.get(document_id)


def _process_document_sync(document_id: int) -> None:
    """Synchronous document processing (runs in background thread)"""
    logger.info("document_processing_started", document_id=document_id)
    db = SessionLocal()
    
    try:
        # Update status
        _processing_status[document_id] = {
            'status': 'processing',
            'stage': 'parsing',
            'progress': 10,
            'started_at': datetime.utcnow().isoformat()
        }
        
        # Get document
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            logger.error("document_not_found_for_processing", document_id=document_id)
            raise Exception(f"Document {document_id} not found")
        
        logger.debug("document_retrieved_for_processing", document_id=document_id, filename=document.filename)
        
        # Parse file
        with PerformanceTimer(logger, "parse_document", document_id=document_id):
            parsed = ParserFactory.parse(document.file_path)
        
        if not parsed or 'error' in parsed:
            error_msg = parsed.get('error', 'Unknown parsing error') if parsed else 'Unsupported file type'
            logger.error("document_parsing_failed", document_id=document_id, error=error_msg)
            raise Exception(error_msg)
        
        content = parsed['content']
        logger.info("document_parsed", document_id=document_id, content_length=len(content))
        
        # Update status
        _processing_status[document_id]['stage'] = 'cleaning'
        _processing_status[document_id]['progress'] = 20
        
        # Clean content
        with PerformanceTimer(logger, "clean_content", document_id=document_id):
            content = TextProcessor.clean(content)
        logger.debug("content_cleaned", document_id=document_id)
        
        # Update status
        _processing_status[document_id]['stage'] = 'chunking'
        _processing_status[document_id]['progress'] = 30
        
        # Chunk the content
        with PerformanceTimer(logger, "chunk_content", document_id=document_id):
            chunks_text = semantic_chunk_text(content)
        
        if not chunks_text:
            logger.error("no_chunks_generated", document_id=document_id)
            raise Exception("No chunks generated from content")
        
        logger.info("content_chunked", document_id=document_id, chunk_count=len(chunks_text))
        
        # Update status
        _processing_status[document_id]['stage'] = 'embedding'
        _processing_status[document_id]['progress'] = 40
        _processing_status[document_id]['total_chunks'] = len(chunks_text)
        
        # Create embeddings (most time-consuming step)
        with PerformanceTimer(logger, "generate_embeddings", document_id=document_id, chunk_count=len(chunks_text)):
            embeddings = get_embeddings(chunks_text)
        logger.info("embeddings_generated", document_id=document_id, embedding_count=len(embeddings))
        
        # Update status
        _processing_status[document_id]['stage'] = 'storing'
        _processing_status[document_id]['progress'] = 80
        
        # Store chunks in database and vector store
        chunk_ids = []
        chunk_metadatas = []
        
        # Extract base metadata
        metadata = MetadataExtractor.extract(
            file_path=document.file_path,
            content=content,
            parsed_metadata=parsed.get('metadata', {})
        )
        
        for idx, (chunk_text, embedding) in enumerate(zip(chunks_text, embeddings)):
            chunk_metadata = MetadataExtractor.create_chunk_metadata(
                base_metadata=metadata,
                chunk_index=idx,
                chunk_text=chunk_text
            )
            
            chunk_id = f"doc_{document.id}_chunk_{idx}"
            chunk_ids.append(chunk_id)
            chunk_metadatas.append(chunk_metadata)
            
            # Save to database
            chunk_record = Chunk(
                document_id=document.id,
                content=chunk_text,
                chunk_index=idx,
                embedding=embedding,
                meta_data=chunk_metadata
            )
            db.add(chunk_record)
        
        # Store in vector database
        with PerformanceTimer(logger, "store_in_vector_db", document_id=document_id, chunk_count=len(chunk_ids)):
            vector_store.add_chunks(
                ids=chunk_ids,
                embeddings=embeddings,
                documents=chunks_text,
                metadatas=chunk_metadatas
            )
        
        logger.info("chunks_stored_in_vector_db", document_id=document_id, chunk_count=len(chunk_ids))
        
        # Update document status
        document.processed_at = datetime.utcnow()
        document.meta_data = metadata
        db.commit()
        
        # Update processing status
        _processing_status[document_id] = {
            'status': 'completed',
            'stage': 'done',
            'progress': 100,
            'chunks_created': len(chunks_text),
            'completed_at': datetime.utcnow().isoformat()
        }
        
        logger.info(
            "document_processing_completed",
            document_id=document_id,
            filename=document.filename,
            chunk_count=len(chunks_text)
        )
        
    except Exception as e:
        logger.error(
            "document_processing_failed",
            document_id=document_id,
            error=str(e),
            exc_info=True
        )
        
        # Update status to failed
        _processing_status[document_id] = {
            'status': 'failed',
            'error': str(e),
            'failed_at': datetime.utcnow().isoformat()
        }
        
        # Mark document as failed
        try:
            document = db.query(Document).filter(Document.id == document_id).first()
            if document:
                document.meta_data = document.meta_data or {}
                document.meta_data['processing_error'] = str(e)
                db.commit()
                logger.debug("document_marked_as_failed", document_id=document_id)
        except Exception as commit_error:
            logger.error(
                "failed_to_update_document_status",
                document_id=document_id,
                error=str(commit_error),
                exc_info=True
            )
        
        db.rollback()
        
    finally:
        db.close()


async def process_document_async(document_id: int) -> None:
    """Queue document for background processing"""
    loop = asyncio.get_event_loop()
    
    # Initialize status
    _processing_status[document_id] = {
        'status': 'queued',
        'stage': 'pending',
        'progress': 0,
        'queued_at': datetime.utcnow().isoformat()
    }
    
    logger.info("document_queued_for_processing", document_id=document_id)
    
    # Run in thread pool to avoid blocking
    loop.run_in_executor(_executor, _process_document_sync, document_id)


def clear_completed_status(document_id: int) -> None:
    """Clear status for completed document"""
    if document_id in _processing_status:
        status = _processing_status[document_id]
        if status.get('status') in ['completed', 'failed']:
            del _processing_status[document_id]

