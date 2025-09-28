"""
PDF document processor using pdfplumber for enhanced text extraction
"""
from pathlib import Path
from typing import Dict, Any, List
import logging

try:
    import pdfplumber
except ImportError:
    pdfplumber = None
    logging.warning("pdfplumber not installed. Run: pip install pdfplumber")

from .base_processor import BaseProcessor

class PDFProcessor(BaseProcessor):
    """Processor for PDF documents with rich text extraction"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        
        if pdfplumber is None:
            raise ImportError("pdfplumber is required for PDF processing. Install with: pip install pdfplumber")
    
    def can_process(self, file_path: Path) -> bool:
        """Check if file is a PDF"""
        return file_path.suffix.lower() == '.pdf'
    
    def extract_text(self, file_path: Path) -> str:
        """Extract text from PDF with layout preservation"""
        try:
            text_content = []
            
            with pdfplumber.open(file_path) as pdf:
                self.logger.info(f"Processing PDF with {len(pdf.pages)} pages")
                
                for page_num, page in enumerate(pdf.pages, 1):
                    # Extract text with layout information
                    page_text = page.extract_text()
                    
                    if page_text:
                        # Add page separator
                        text_content.append(f"--- Page {page_num} ---")
                        text_content.append(page_text)
                        
                        # Try to extract tables if they exist
                        tables = page.extract_tables()
                        for i, table in enumerate(tables):
                            text_content.append(f"--- Table {i+1} on Page {page_num} ---")
                            # Convert table to text format
                            for row in table:
                                if row:
                                    text_content.append(" | ".join(str(cell) if cell else "" for cell in row))
            
            full_text = "\n".join(text_content)
            return self.clean_text(full_text)
            
        except Exception as e:
            self.logger.error(f"Error extracting text from PDF {file_path}: {e}")
            return ""
    
    def extract_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Extract metadata from PDF"""
        metadata = self.get_file_info(file_path)
        
        try:
            with pdfplumber.open(file_path) as pdf:
                # PDF-specific metadata
                pdf_metadata = pdf.metadata or {}
                
                metadata.update({
                    "pages": len(pdf.pages),
                    "title": pdf_metadata.get('Title', ''),
                    "author": pdf_metadata.get('Author', ''),
                    "subject": pdf_metadata.get('Subject', ''),
                    "creator": pdf_metadata.get('Creator', ''),
                    "producer": pdf_metadata.get('Producer', ''),
                    "creation_date": str(pdf_metadata.get('CreationDate', '')),
                    "modification_date": str(pdf_metadata.get('ModDate', '')),
                })
                
                # Skip table extraction for faster processing
                # (Table extraction can be slow on complex PDFs)
                total_tables = 0
                # for page in pdf.pages:
                #     tables = page.extract_tables()
                #     total_tables += len(tables)
                
                metadata["total_tables"] = total_tables
                
        except Exception as e:
            self.logger.error(f"Error extracting PDF metadata from {file_path}: {e}")
            metadata["pdf_error"] = str(e)
        
        return metadata
    
    def extract_tables(self, file_path: Path) -> List[List[List[str]]]:
        """Extract tables from PDF as structured data"""
        tables = []
        
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_tables = page.extract_tables()
                    tables.extend(page_tables)
        except Exception as e:
            self.logger.error(f"Error extracting tables from PDF {file_path}: {e}")
        
        return tables
    
    def get_page_text(self, file_path: Path, page_number: int) -> str:
        """Extract text from a specific page"""
        try:
            with pdfplumber.open(file_path) as pdf:
                if 0 <= page_number < len(pdf.pages):
                    page = pdf.pages[page_number]
                    return self.clean_text(page.extract_text() or "")
                else:
                    self.logger.warning(f"Page {page_number} does not exist in {file_path}")
                    return ""
        except Exception as e:
            self.logger.error(f"Error extracting page {page_number} from PDF {file_path}: {e}")
            return ""