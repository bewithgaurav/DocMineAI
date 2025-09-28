"""
Text processing utilities for Document RAG Extractor
"""
import re
from typing import List, Dict, Any
from pathlib import Path

class TextProcessor:
    """Handles text chunking and processing"""
    
    def __init__(self, chunk_size: int = 2000, overlap: int = 200):
        self.chunk_size = chunk_size
        self.overlap = overlap
    
    def chunk_text(self, text: str) -> List[str]:
        """Split text into overlapping chunks"""
        if len(text) <= self.chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + self.chunk_size
            
            # If we're not at the end, try to break at a sentence boundary
            if end < len(text):
                # Look for sentence endings in the last 200 characters of the chunk
                chunk_text = text[start:end]
                last_period = chunk_text.rfind('.')
                last_newline = chunk_text.rfind('\n')
                
                # Use the latest sentence or paragraph boundary
                break_point = max(last_period, last_newline)
                if break_point > self.chunk_size - 200:  # Don't break too early
                    end = start + break_point + 1
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            # Move start position with overlap
            start = end - self.overlap if end < len(text) else len(text)
        
        return chunks
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove common OCR artifacts
        text = text.replace('\f', ' ')  # Form feed
        text = text.replace('\r', ' ')  # Carriage return
        
        # Normalize quotes and dashes
        text = text.replace('"', '"').replace('"', '"')
        text = text.replace(''', "'").replace(''', "'")
        text = text.replace('–', '-').replace('—', '-')
        
        return text.strip()
    
    def extract_keywords(self, text: str, keywords: List[str]) -> bool:
        """Check if text contains relevant keywords"""
        text_lower = text.lower()
        return any(keyword.lower() in text_lower for keyword in keywords)
    
    def filter_chunks_by_keywords(self, chunks: List[str], keywords: List[str]) -> List[str]:
        """Filter chunks that contain relevant keywords"""
        if not keywords:
            return chunks
        
        return [chunk for chunk in chunks if self.extract_keywords(chunk, keywords)]

class YAMLProcessor:
    """Handles YAML parsing and merging"""
    
    @staticmethod
    def parse_yaml_from_text(text: str) -> Dict[str, Any]:
        """Extract YAML content from LLM response"""
        import yaml
        
        # Try to find YAML block in response
        yaml_match = re.search(r'```ya?ml\s*\n(.*?)\n```', text, re.DOTALL | re.IGNORECASE)
        if yaml_match:
            yaml_text = yaml_match.group(1)
        else:
            # Try to find YAML without code blocks
            yaml_text = text.strip()
        
        try:
            return yaml.safe_load(yaml_text) or {}
        except yaml.YAMLError as e:
            # If YAML parsing fails, try to extract structured data
            return YAMLProcessor._extract_structured_data(text)
    
    @staticmethod
    def _extract_structured_data(text: str) -> Dict[str, Any]:
        """Fallback method to extract structured data when YAML parsing fails"""
        # This is a simple fallback - in a production system you might want more sophisticated parsing
        result = {}
        
        # Look for patterns like "products:", "integrations:", etc.
        sections = re.split(r'\n(?=\w+:)', text)
        
        for section in sections:
            if ':' in section:
                lines = section.strip().split('\n')
                if lines:
                    header = lines[0].replace(':', '').strip()
                    content = []
                    
                    for line in lines[1:]:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            content.append(line)
                    
                    if content:
                        result[header] = content
        
        return result
    
    @staticmethod
    def merge_yaml_results(results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Merge multiple YAML results into one"""
        merged = {}
        
        for result in results:
            if not isinstance(result, dict):
                continue
                
            for key, value in result.items():
                if key not in merged:
                    merged[key] = []
                
                if isinstance(value, list):
                    merged[key].extend(value)
                elif value:  # Skip empty values
                    merged[key].append(value)
        
        return merged