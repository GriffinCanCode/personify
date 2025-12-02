from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from typing import List
import os
import shutil
from datetime import datetime

from backend.database.connection import get_db
from backend.database.models import Document, Chunk
from backend.config import settings
from backend.ingestion.parsers import ParserFactory, compute_content_hash
from backend.ingestion.processors import TextProcessor
from backend.ingestion.metadata_extractor import MetadataExtractor
from backend.vectorstore.embeddings import semantic_chunk_text, get_embeddings
from backend.vectorstore.store import vector_store

router = APIRouter(prefix="/upload", tags=["upload"])

@router.post("/files")
async def upload_files(
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    """Upload and process multiple files"""
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    
    results = []
    
    for file in files:
        try:
            # Save file
            file_path = os.path.join(settings.UPLOAD_DIR, file.filename)
            with open(file_path, 'wb') as f:
                shutil.copyfileobj(file.file, f)
            
            # Parse file
            parsed = ParserFactory.parse(file_path)
            if not parsed:
                results.append({
                    'filename': file.filename,
                    'status': 'error',
                    'message': 'Unsupported file type'
                })
                continue
            
            if 'error' in parsed:
                results.append({
                    'filename': file.filename,
                    'status': 'error',
                    'message': parsed['error']
                })
                continue
            
            content = parsed['content']
            
            # Clean content
            content = TextProcessor.clean(content)
            
            # Check for duplicates
            content_hash = compute_content_hash(content)
            existing = db.query(Document).filter(
                Document.content_hash == content_hash
            ).first()
            
            if existing:
                results.append({
                    'filename': file.filename,
                    'status': 'duplicate',
                    'message': 'File already processed'
                })
                continue
            
            # Extract metadata
            metadata = MetadataExtractor.extract(
                file_path=file_path,
                content=content,
                parsed_metadata=parsed.get('metadata', {})
            )
            
            # Create document record
            document = Document(
                filename=file.filename,
                source_type=metadata.get('source_type', 'unknown'),
                file_path=file_path,
                content_hash=content_hash,
                metadata=metadata
            )
            
            db.add(document)
            db.flush()
            
            # Chunk the content
            chunks_text = semantic_chunk_text(content)
            
            # Create embeddings
            embeddings = get_embeddings(chunks_text)
            
            # Store chunks
            chunk_ids = []
            chunk_metadatas = []
            
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
                    embedding_id=chunk_id,
                    metadata=chunk_metadata
                )
                db.add(chunk_record)
            
            # Store in vector database
            vector_store.add_chunks(
                ids=chunk_ids,
                documents=chunks_text,
                metadatas=chunk_metadatas,
                embeddings=embeddings
            )
            
            # Mark as processed
            document.processed_at = datetime.now()
            
            db.commit()
            
            results.append({
                'filename': file.filename,
                'status': 'success',
                'chunks_created': len(chunks_text),
                'document_id': document.id
            })
            
        except Exception as e:
            db.rollback()
            results.append({
                'filename': file.filename,
                'status': 'error',
                'message': str(e)
            })
    
    return {'results': results}

@router.get("/documents")
async def get_documents(
    db: Session = Depends(get_db)
):
    """Get all uploaded documents"""
    documents = db.query(Document).order_by(
        Document.created_at.desc()
    ).all()
    
    return [
        {
            'id': doc.id,
            'filename': doc.filename,
            'source_type': doc.source_type,
            'created_at': doc.created_at.isoformat(),
            'processed_at': doc.processed_at.isoformat() if doc.processed_at else None,
            'chunk_count': len(doc.chunks),
            'metadata': doc.metadata
        }
        for doc in documents
    ]

@router.get("/stats")
async def get_stats(
    db: Session = Depends(get_db)
):
    """Get upload statistics"""
    total_documents = db.query(Document).count()
    processed_documents = db.query(Document).filter(
        Document.processed_at.isnot(None)
    ).count()
    total_chunks = db.query(Chunk).count()
    
    # Source type breakdown
    source_types = db.query(
        Document.source_type,
        db.func.count(Document.id)
    ).group_by(Document.source_type).all()
    
    return {
        'total_documents': total_documents,
        'processed_documents': processed_documents,
        'total_chunks': total_chunks,
        'source_types': {st: count for st, count in source_types},
        'vector_store_size': vector_store.count()
    }

