from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from typing import List
import os
import shutil
from datetime import datetime

from backend.database.connection import get_db
from backend.database.models import Document, Chunk
from backend.config import settings
from backend.ingestion.parsers import compute_content_hash
from backend.ingestion.background_processor import process_document_async, get_document_status
from backend.vectorstore.store import vector_store
from backend.logging_config import get_logger, PerformanceTimer

logger = get_logger(__name__)
router = APIRouter(prefix="/upload", tags=["upload"])

@router.get("/status/{document_id}")
async def get_processing_status(
    document_id: int,
    db: Session = Depends(get_db)
):
    """
    Get real-time processing status for an uploaded document.
    Returns progress percentage, current stage, and completion status.
    """
    logger.debug("checking_processing_status", document_id=document_id)
    
    try:
        # Get status from background processor
        status = get_document_status(document_id)
        
        if not status:
            # Check if document exists
            document = db.query(Document).filter(Document.id == document_id).first()
            if not document:
                logger.warning("document_not_found_for_status", document_id=document_id)
                raise HTTPException(status_code=404, detail="Document not found")
            
            # If no active processing status, check if completed
            if document.processed_at:
                chunk_count = db.query(Chunk).filter(Chunk.document_id == document_id).count()
                logger.debug(
                    "document_processing_completed",
                    document_id=document_id,
                    chunk_count=chunk_count
                )
                return {
                    'document_id': document_id,
                    'status': 'completed',
                    'stage': 'done',
                    'progress': 100,
                    'chunks_created': chunk_count
                }
            else:
                logger.debug("document_status_pending", document_id=document_id)
                return {
                    'document_id': document_id,
                    'status': 'pending',
                    'stage': 'unknown',
                    'progress': 0
                }
        
        logger.debug("document_status_retrieved", document_id=document_id, status=status.get('status'))
        return {
            'document_id': document_id,
            **status
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error("status_check_error", document_id=document_id, error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/files")
async def upload_files(
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload files for processing (INSTANT RESPONSE).
    Files are saved immediately and processed asynchronously in background.
    Use /upload/status/{document_id} to check processing progress.
    """
    logger.info("file_upload_started", file_count=len(files))
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    
    results = []
    
    for file in files:
        try:
            with PerformanceTimer(logger, "file_upload", filename=file.filename):
                # Read file content for proper content hash
                content = file.file.read()
                file_size = len(content)
                
                logger.debug(
                    "uploading_file",
                    filename=file.filename,
                    file_size=file_size,
                    content_type=file.content_type
                )
                
                # Compute actual content hash for deduplication
                content_hash = compute_content_hash(content.decode('utf-8', errors='ignore'))
                
                # Check for existing document with same content hash
                existing_doc = db.query(Document).filter(Document.content_hash == content_hash).first()
                
                if existing_doc:
                    logger.info(
                        "duplicate_document_found",
                        filename=file.filename,
                        existing_id=existing_doc.id
                    )
                    results.append({
                        'filename': file.filename,
                        'status': 'exists',
                        'document_id': existing_doc.id,
                        'message': 'Document already uploaded. Use existing document.'
                    })
                    continue
                
                # Save file immediately
                file_path = os.path.join(settings.UPLOAD_DIR, file.filename)
                with open(file_path, 'wb') as f:
                    f.write(content)
                
                # Create document record with "queued" status
                document = Document(
                    filename=file.filename,
                    source_type='pending',
                    file_path=file_path,
                    content_hash=content_hash,
                    meta_data={
                        'file_size': file_size,
                        'upload_time': datetime.utcnow().isoformat(),
                        'status': 'queued'
                    }
                )
                
                db.add(document)
                db.commit()
                db.refresh(document)
                
                logger.info(
                    "file_saved_and_queued",
                    filename=file.filename,
                    document_id=document.id,
                    file_size=file_size
                )
                
                # Queue for background processing (NON-BLOCKING)
                await process_document_async(document.id)
                
                results.append({
                    'filename': file.filename,
                    'status': 'queued',
                    'document_id': document.id,
                    'message': 'File uploaded. Processing in background.'
                })
        except IntegrityError:
            db.rollback()
            # Handle race condition - document was inserted by another request
            existing = db.query(Document).filter(Document.filename == file.filename).first()
            if existing:
                logger.info("duplicate_document_race_condition", filename=file.filename, existing_id=existing.id)
                results.append({
                    'filename': file.filename,
                    'status': 'exists',
                    'document_id': existing.id,
                    'message': 'Document already exists.'
                })
            else:
                logger.error("integrity_error_no_existing_doc", filename=file.filename)
                results.append({
                    'filename': file.filename,
                    'status': 'error',
                    'message': 'Upload failed: duplicate content detected'
                })
        except Exception as e:
            db.rollback()
            logger.error("file_upload_failed", filename=file.filename, error=str(e), exc_info=True)
            results.append({
                'filename': file.filename,
                'status': 'error',
                'message': f'Upload failed: {str(e)}'
            })
    
    logger.info("file_upload_batch_completed", total_files=len(files), successful=len([r for r in results if r['status'] in ('queued', 'exists')]))
    return {'results': results}

@router.get("/documents")
async def get_documents(
    db: Session = Depends(get_db)
):
    """Get all uploaded documents with real-time processing status"""
    logger.debug("fetching_all_documents")
    
    try:
        documents = db.query(Document).order_by(
            Document.created_at.desc()
        ).all()
        
        logger.info("documents_fetched", count=len(documents))
        
        result_docs = []
        for doc in documents:
            # Get real-time processing status
            status = get_document_status(doc.id)
            
            # Get chunk count without loading all chunks
            chunk_count = db.query(Chunk).filter(Chunk.document_id == doc.id).count()
            
            # Safely extract metadata
            metadata = doc.meta_data if hasattr(doc, 'meta_data') else (doc.metadata if hasattr(doc, 'metadata') else {})
            
            result_docs.append({
                'id': doc.id,
                'filename': doc.filename,
                'source_type': doc.source_type,
                'created_at': doc.created_at.isoformat() if doc.created_at else None,
                'processed_at': doc.processed_at.isoformat() if doc.processed_at else None,
                'chunk_count': chunk_count,
                'metadata': metadata if isinstance(metadata, dict) else {},
                'processing_status': status.get('status') if status else (
                    'completed' if doc.processed_at else 'pending'
                ),
                'processing_progress': status.get('progress', 100) if status else (
                    100 if doc.processed_at else 0
                )
            })
        
        return result_docs
    except Exception as e:
        logger.error("documents_fetch_error", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
async def get_stats(
    db: Session = Depends(get_db)
):
    """Get upload statistics"""
    logger.debug("fetching_upload_stats")
    
    try:
        with PerformanceTimer(logger, "stats_calculation"):
            total_documents = db.query(Document).count()
            processed_documents = db.query(Document).filter(
                Document.processed_at.isnot(None)
            ).count()
            total_chunks = db.query(Chunk).count()
            
            # Source type breakdown
            source_types = db.query(
                Document.source_type,
                func.count(Document.id)
            ).group_by(Document.source_type).all()
            
            vector_store_size = vector_store.count()
            
            logger.info(
                "upload_stats_calculated",
                total_documents=total_documents,
                processed_documents=processed_documents,
                total_chunks=total_chunks,
                vector_store_size=vector_store_size
            )
            
            return {
                'total_documents': total_documents,
                'processed_documents': processed_documents,
                'total_chunks': total_chunks,
                'source_types': {st: count for st, count in source_types},
                'vector_store_size': vector_store_size
            }
    except Exception as e:
        logger.error("stats_fetch_error", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

