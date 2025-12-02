import re
from typing import Dict, List
from datetime import datetime

class TextProcessor:
    """Process and clean extracted text"""
    
    @staticmethod
    def clean(text: str) -> str:
        """Clean and normalize text"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove excessive newlines (more than 2)
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # Strip leading/trailing whitespace
        text = text.strip()
        
        return text
    
    @staticmethod
    def remove_email_headers(text: str) -> str:
        """Remove email headers and signatures"""
        # Remove common email headers
        text = re.sub(r'^(From|To|Subject|Date|Cc|Bcc):.*$', '', text, flags=re.MULTILINE)
        
        # Remove common signatures
        signature_patterns = [
            r'\n--\s*\n.*',  # -- signature
            r'\nBest regards,.*',
            r'\nSincerely,.*',
            r'\nSent from my.*',
        ]
        
        for pattern in signature_patterns:
            text = re.sub(pattern, '', text, flags=re.DOTALL | re.IGNORECASE)
        
        return text
    
    @staticmethod
    def extract_metadata_from_content(text: str) -> Dict:
        """Extract metadata from content (dates, entities, etc.)"""
        metadata = {}
        
        # Extract dates
        date_pattern = r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b'
        dates = re.findall(date_pattern, text)
        if dates:
            metadata['mentioned_dates'] = dates[:5]  # Limit to first 5
        
        # Extract URLs
        url_pattern = r'https?://[^\s]+'
        urls = re.findall(url_pattern, text)
        if urls:
            metadata['urls'] = urls[:5]
        
        # Extract @ mentions
        mention_pattern = r'@\w+'
        mentions = re.findall(mention_pattern, text)
        if mentions:
            metadata['mentions'] = list(set(mentions))[:10]
        
        return metadata
    
    @staticmethod
    def detect_language(text: str) -> str:
        """Simple language detection (basic heuristic)"""
        # This is very basic - could use langdetect library for better results
        # For now, assume English
        return "en"
    
    @staticmethod
    def split_into_sentences(text: str) -> List[str]:
        """Split text into sentences"""
        # Basic sentence splitting
        sentences = re.split(r'[.!?]+\s+', text)
        return [s.strip() for s in sentences if s.strip()]

class ContextExtractor:
    """Extract contextual information from documents"""
    
    @staticmethod
    def infer_source_type(filename: str, content: str) -> str:
        """Infer source type from filename and content"""
        filename_lower = filename.lower()
        content_lower = content.lower()
        
        # Email indicators
        if any(word in filename_lower for word in ['email', 'mail', 'inbox', 'sent']):
            return 'email'
        if any(word in content_lower[:200] for word in ['from:', 'to:', 'subject:']):
            return 'email'
        
        # Journal indicators
        if any(word in filename_lower for word in ['journal', 'diary', 'log', 'daily']):
            return 'journal'
        
        # Note indicators
        if any(word in filename_lower for word in ['note', 'notes']):
            return 'note'
        
        # Social media
        if any(word in filename_lower for word in ['tweet', 'twitter', 'post', 'social']):
            return 'social'
        
        # Creative writing
        if any(word in filename_lower for word in ['essay', 'article', 'blog', 'story']):
            return 'creative'
        
        # Voice/transcript
        if any(word in filename_lower for word in ['transcript', 'recording', 'audio', 'voice']):
            return 'voice'
        
        return 'unknown'
    
    @staticmethod
    def infer_context(content: str) -> str:
        """Infer context (professional, personal, etc.)"""
        content_lower = content.lower()
        
        # Professional indicators
        professional_words = [
            'meeting', 'project', 'deadline', 'team', 'client',
            'proposal', 'budget', 'report', 'quarterly', 'business'
        ]
        
        # Personal indicators
        personal_words = [
            'friend', 'family', 'weekend', 'feel', 'felt', 
            'love', 'hate', 'worried', 'excited', 'hope'
        ]
        
        prof_count = sum(1 for word in professional_words if word in content_lower)
        pers_count = sum(1 for word in personal_words if word in content_lower)
        
        if prof_count > pers_count * 1.5:
            return 'professional'
        elif pers_count > prof_count * 1.5:
            return 'personal'
        else:
            return 'mixed'
    
    @staticmethod
    def extract_topics(content: str, max_topics: int = 5) -> List[str]:
        """Extract main topics from content (basic keyword extraction)"""
        # Remove common words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'is', 'was', 'are', 'were', 'been', 'be', 'have', 'has',
            'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may',
            'might', 'must', 'can', 'this', 'that', 'these', 'those', 'i', 'you',
            'he', 'she', 'it', 'we', 'they', 'my', 'your', 'his', 'her', 'its',
            'our', 'their', 'me', 'him', 'her', 'us', 'them'
        }
        
        # Extract words
        words = re.findall(r'\b[a-z]{4,}\b', content.lower())
        
        # Count frequency
        word_freq = {}
        for word in words:
            if word not in stop_words:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Get top words
        top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, _ in top_words[:max_topics]]

