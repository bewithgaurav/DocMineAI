"""
Base processor class and common utilities
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from pathlib import Path
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class BaseProcessor(ABC):
    """Abstract base class for all document processors"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger(self.__class__.__name__)
        
    @abstractmethod
    def can_process(self, file_path: Path) -> bool:
        """Check if this processor can handle the given file type"""
        pass
        
    @abstractmethod
    def extract_text(self, file_path: Path) -> str:
        """Extract raw text from the document"""
        pass
        
    @abstractmethod
    def extract_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Extract metadata from the document"""
        pass
        
    def process(self, file_path: Path) -> Dict[str, Any]:
        """Main processing method that combines text extraction and metadata"""
        self.logger.info(f"Processing {file_path.name}")
        
        try:
            # Extract raw content
            text = self.extract_text(file_path)
            metadata = self.extract_metadata(file_path)
            
            # Combine into standard format
            result = {
                "file_path": str(file_path),
                "file_name": file_path.name,
                "file_type": file_path.suffix.lower(),
                "text_content": text,
                "metadata": metadata,
                "processed_at": datetime.now().isoformat(),
                "processor": self.__class__.__name__,
                "success": True,
                "error": None
            }
            
            self.logger.info(f"Successfully processed {file_path.name} - {len(text)} characters extracted")
            return result
            
        except Exception as e:
            self.logger.error(f"Error processing {file_path.name}: {str(e)}")
            return {
                "file_path": str(file_path),
                "file_name": file_path.name,
                "file_type": file_path.suffix.lower(),
                "text_content": "",
                "metadata": {},
                "processed_at": datetime.now().isoformat(),
                "processor": self.__class__.__name__,
                "success": False,
                "error": str(e)
            }
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize extracted text"""
        if not text:
            return ""
            
        # Remove excessive whitespace
        text = ' '.join(text.split())
        
        # Remove common OCR artifacts
        text = text.replace('\f', ' ')  # Form feed
        text = text.replace('\r', ' ')  # Carriage return
        
        # Normalize line breaks
        text = text.replace('\n\n\n', '\n\n')
        
        return text.strip()
    
    def get_file_info(self, file_path: Path) -> Dict[str, Any]:
        """Get basic file information"""
        stat = file_path.stat()
        return {
            "size_bytes": stat.st_size,
            "size_mb": round(stat.st_size / (1024 * 1024), 2),
            "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
        }