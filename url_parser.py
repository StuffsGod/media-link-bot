"""
URL parser module for extracting file information from text.
Handles URL detection, file name extraction, and size parsing.
"""

import re
from typing import List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class URLParser:
    """Parser for extracting URLs and file metadata from text."""
    
    # HTTP/HTTPS URL pattern
    URL_PATTERN = re.compile(
        r'https?://(?:www\.)?[-a-zA-Z0-9@:%._+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_+.~#?&/=]*)',
        re.IGNORECASE
    )
    
    # File size pattern (e.g., "1.5 GB", "500 MB", "1.2 GB")
    SIZE_PATTERN = re.compile(
        r'(\d+(?:\.\d+)?)\s*([KMG]B)',
        re.IGNORECASE
    )
    
    # Common file extensions
    MEDIA_EXTENSIONS = {
        'mkv', 'mp4', 'avi', 'mov', 'flv', 'wmv', 'webm',  # Video
        'mp3', 'flac', 'aac', 'wav', 'ogg', 'm4a',  # Audio
        'zip', 'rar', '7z', 'tar', 'gz',  # Archive
        'pdf', 'doc', 'docx', 'txt'  # Document
    }
    
    @staticmethod
    def extract_urls(text: str) -> List[str]:
        """
        Extract all HTTP/HTTPS URLs from text.
        
        Args:
            text: Text to parse
            
        Returns:
            List of unique URLs (sorted by first appearance)
        """
        if not text:
            return []
        
        try:
            urls = URLParser.URL_PATTERN.findall(text)
            # Remove duplicates while preserving order
            seen = set()
            unique_urls = []
            for url in urls:
                url_clean = url.rstrip('.,;:!?)\'\"')  # Remove trailing punctuation
                if url_clean not in seen and url_clean.startswith('http'):
                    seen.add(url_clean)
                    unique_urls.append(url_clean)
            
            return unique_urls
            
        except Exception as e:
            logger.error(f"Error extracting URLs: {e}")
            return []
    
    @staticmethod
    def extract_file_size(text: str) -> Optional[str]:
        """
        Extract file size from text.
        
        Args:
            text: Text to parse
            
        Returns:
            File size string (e.g., "1.5 GB") or None
        """
        if not text:
            return None
        
        try:
            match = URLParser.SIZE_PATTERN.search(text)
            if match:
                return f"{match.group(1)} {match.group(2).upper()}"
            return None
            
        except Exception as e:
            logger.error(f"Error extracting file size: {e}")
            return None
    
    @staticmethod
    def extract_file_name(text: str) -> Optional[str]:
        """
        Extract likely file name from text.
        Looks for patterns like "filename [size]" at the start of a line.
        
        Args:
            text: Text to parse
            
        Returns:
            File name or None
        """
        if not text:
            return None
        
        try:
            lines = text.split('\n')
            
            for line in lines:
                line = line.strip()
                if not line or line.startswith('http'):
                    continue
                
                # Remove size notation if present
                file_name = re.sub(r'\s*\[\d+(?:\.\d+)?\s*[KMG]B\]\s*$', '', line)
                
                # Check if it looks like a filename
                if file_name and len(file_name) > 2:
                    # Remove common non-filename prefixes
                    file_name = re.sub(r'^(download|get|file|link|url)[\s:]', '', file_name, flags=re.IGNORECASE)
                    file_name = file_name.strip()
                    
                    if file_name and len(file_name) > 2:
                        return file_name
            
            # Fallback: use first non-empty, non-URL line
            for line in lines:
                line = line.strip()
                if line and not line.startswith('http'):
                    return line
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting file name: {e}")
            return None
    
    @staticmethod
    def parse_message(text: str, caption: Optional[str] = None) -> Tuple[str, Optional[str], List[str]]:
        """
        Parse complete message to extract file info and URLs.
        
        Args:
            text: Message text
            caption: Optional caption (usually forwarded message caption)
            
        Returns:
            Tuple of (file_name, file_size, urls)
        """
        try:
            combined_text = f"{text}\n{caption}" if caption else text
            
            # Extract URLs
            urls = URLParser.extract_urls(combined_text)
            
            # Extract file size
            file_size = URLParser.extract_file_size(combined_text)
            
            # Extract file name - prioritize caption over text
            file_name = URLParser.extract_file_name(caption) if caption else None
            if not file_name:
                file_name = URLParser.extract_file_name(text)
            
            # Fallback file name
            if not file_name:
                file_name = "Media File"
            
            # Sanitize file name
            file_name = URLParser.sanitize_filename(file_name)
            
            return file_name, file_size, urls
            
        except Exception as e:
            logger.error(f"Error parsing message: {e}")
            return "Media File", None, []
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Sanitize filename to make it safe for storage.
        
        Args:
            filename: Original filename
            
        Returns:
            Sanitized filename
        """
        if not filename:
            return "Media File"
        
        # Remove/replace invalid characters
        filename = re.sub(r'[<>:"/\\|?*]', '', filename)
        # Remove excessive whitespace
        filename = re.sub(r'\s+', ' ', filename).strip()
        # Limit length
        filename = filename[:200]
        
        if not filename:
            return "Media File"
        
        return filename
    
    @staticmethod
    def is_valid_url(url: str) -> bool:
        """
        Validate if a URL is properly formatted.
        
        Args:
            url: URL to validate
            
        Returns:
            True if valid
        """
        if not url:
            return False
        
        try:
            return bool(re.match(
                r'^https?://(?:www\.)?[-a-zA-Z0-9@:%._+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b',
                url,
                re.IGNORECASE
            ))
        except:
            return False
    
    @staticmethod
    def format_urls_for_display(urls: List[str], max_display: int = 3) -> Tuple[str, List[Tuple[str, str]]]:
        """
        Format URLs for display in message and as buttons.
        
        Args:
            urls: List of URLs
            max_display: Maximum URLs to show as individual buttons
            
        Returns:
            Tuple of (text_representation, button_list)
            button_list contains tuples of (label, url)
        """
        if not urls:
            return "No links available", []
        
        try:
            # Text representation (all URLs listed)
            text_parts = []
            for i, url in enumerate(urls, 1):
                text_parts.append(f"{i}. {url}")
            
            text_repr = "\n".join(text_parts)
            
            # Buttons (limited to max_display)
            buttons = []
            for i, url in enumerate(urls[:max_display], 1):
                # Shorten label for button
                label = f"Link {i}" if len(urls) > 1 else "Download"
                buttons.append((label, url))
            
            # If more URLs exist, add "More Links" button
            if len(urls) > max_display:
                buttons.append(("📄 More Links", "show_all"))
            
            return text_repr, buttons
            
        except Exception as e:
            logger.error(f"Error formatting URLs: {e}")
            return "\n".join(urls), []
