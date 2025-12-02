from typing import Dict, Optional
from datetime import datetime
import os
from backend.ingestion.processors import TextProcessor, ContextExtractor

class MetadataExtractor:
    """Extract comprehensive metadata from documents"""
    
    @staticmethod
    def extract(
        file_path: str,
        content: str,
        parsed_metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Extract all metadata for a document.
        
        Returns comprehensive metadata dict including:
        - File info (name, size, dates)
        - Source type (email, journal, etc.)
        - Context (professional, personal)
        - Topics
        - Language
        - Any additional parsed metadata
        """
        filename = os.path.basename(file_path)
        
        metadata = {
            'filename': filename,
            'file_path': file_path,
            'file_size': os.path.getsize(file_path),
            'file_extension': os.path.splitext(filename)[1],
            'uploaded_at': datetime.now().isoformat(),
        }
        
        # Add file timestamps
        try:
            stat = os.stat(file_path)
            metadata['created_at'] = datetime.fromtimestamp(stat.st_ctime).isoformat()
            metadata['modified_at'] = datetime.fromtimestamp(stat.st_mtime).isoformat()
        except:
            pass
        
        # Infer source type and context
        metadata['source_type'] = ContextExtractor.infer_source_type(filename, content)
        metadata['context'] = ContextExtractor.infer_context(content)
        
        # Extract topics
        metadata['topics'] = ContextExtractor.extract_topics(content)
        
        # Detect language
        metadata['language'] = TextProcessor.detect_language(content)
        
        # Content stats
        metadata['char_count'] = len(content)
        metadata['word_count'] = len(content.split())
        sentences = TextProcessor.split_into_sentences(content)
        metadata['sentence_count'] = len(sentences)
        
        # Extract metadata from content
        content_metadata = TextProcessor.extract_metadata_from_content(content)
        metadata.update(content_metadata)
        
        # Merge with parsed metadata
        if parsed_metadata:
            metadata.update(parsed_metadata)
        
        return metadata
    
    @staticmethod
    def create_chunk_metadata(
        base_metadata: Dict,
        chunk_index: int,
        chunk_text: str
    ) -> Dict:
        """Create metadata for an individual chunk"""
        return {
            **base_metadata,
            'chunk_index': chunk_index,
            'chunk_char_count': len(chunk_text),
            'chunk_word_count': len(chunk_text.split()),
        }

