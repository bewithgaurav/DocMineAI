"""
Image processor with OCR capabilities using EasyOCR
"""
from pathlib import Path
from typing import Dict, Any, List, Tuple
import logging
import ssl
import urllib.request

try:
    import easyocr
    from PIL import Image
    EASYOCR_AVAILABLE = True
except ImportError:
    easyocr = None
    Image = None
    EASYOCR_AVAILABLE = False
    logging.warning("easyocr or Pillow not installed. Run: pip install easyocr Pillow")

from .base_processor import BaseProcessor

class ImageProcessor(BaseProcessor):
    """Processor for images with OCR text extraction"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        
        if not EASYOCR_AVAILABLE:
            raise ImportError("easyocr and Pillow are required for image processing. Install with: pip install easyocr Pillow")
        
        # Initialize OCR reader (this may take time on first run)
        self.ocr_languages = config.get('ocr_languages', ['en']) if config else ['en']
        self.confidence_threshold = config.get('confidence_threshold', 0.7) if config else 0.7
        
        try:
            # Fix SSL certificate verification issue on macOS
            self._fix_ssl_context()
            
            self.reader = easyocr.Reader(self.ocr_languages)
            self.logger.info(f"EasyOCR initialized with languages: {self.ocr_languages}")
        except Exception as e:
            self.logger.error(f"Failed to initialize EasyOCR: {e}")
            self.logger.info("Trying fallback initialization...")
            try:
                # Try with minimal configuration
                self.reader = easyocr.Reader(['en'], verbose=False)
                self.logger.info("EasyOCR initialized with fallback settings")
            except Exception as e2:
                self.logger.error(f"Fallback initialization also failed: {e2}")
                raise
    
    def _fix_ssl_context(self):
        """Fix SSL certificate verification issues on macOS"""
        try:
            # Create unverified SSL context for downloading models
            ssl._create_default_https_context = ssl._create_unverified_context
            self.logger.info("SSL context configured for model downloads")
        except Exception as e:
            self.logger.warning(f"Could not configure SSL context: {e}")
    
    def can_process(self, file_path: Path) -> bool:
        """Check if file is a supported image format"""
        return file_path.suffix.lower() in ['.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.gif']
    
    def extract_text(self, file_path: Path) -> str:
        """Extract text from image using OCR"""
        try:
            # Perform OCR
            results = self.reader.readtext(str(file_path))
            
            # Filter by confidence and extract text
            text_parts = []
            for (bbox, text, confidence) in results:
                if confidence >= self.confidence_threshold:
                    text_parts.append(text)
                    self.logger.debug(f"OCR: '{text}' (confidence: {confidence:.2f})")
            
            # Join text parts with spaces
            full_text = " ".join(text_parts)
            return self.clean_text(full_text)
            
        except Exception as e:
            self.logger.error(f"Error extracting text from image {file_path}: {e}")
            return ""
    
    def extract_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Extract metadata from image file"""
        metadata = self.get_file_info(file_path)
        
        try:
            # Get image properties
            with Image.open(file_path) as img:
                metadata.update({
                    "width": img.width,
                    "height": img.height,
                    "format": img.format,
                    "mode": img.mode,
                    "has_transparency": img.mode in ('RGBA', 'LA') or 'transparency' in img.info,
                })
                
                # Get EXIF data if available
                if hasattr(img, '_getexif') and img._getexif():
                    exif_data = img._getexif()
                    metadata["exif"] = {k: str(v) for k, v in exif_data.items() if v is not None}
            
            # OCR-specific metadata
            ocr_results = self.reader.readtext(str(file_path), detail=1)
            
            total_detections = len(ocr_results)
            high_confidence_detections = sum(1 for _, _, conf in ocr_results if conf >= self.confidence_threshold)
            avg_confidence = sum(conf for _, _, conf in ocr_results) / total_detections if total_detections > 0 else 0
            
            metadata.update({
                "ocr_detections": total_detections,
                "high_confidence_detections": high_confidence_detections,
                "average_confidence": round(avg_confidence, 3),
                "ocr_languages": self.ocr_languages,
                "confidence_threshold": self.confidence_threshold,
            })
            
        except Exception as e:
            self.logger.error(f"Error extracting image metadata from {file_path}: {e}")
            metadata["image_error"] = str(e)
        
        return metadata
    
    def extract_detailed_ocr_results(self, file_path: Path) -> List[Dict[str, Any]]:
        """Extract detailed OCR results with bounding boxes and confidence scores"""
        try:
            results = self.reader.readtext(str(file_path), detail=1)
            
            detailed_results = []
            for bbox, text, confidence in results:
                # Convert bbox coordinates to a more readable format
                x1, y1 = int(bbox[0][0]), int(bbox[0][1])
                x2, y2 = int(bbox[2][0]), int(bbox[2][1])
                
                detailed_results.append({
                    "text": text,
                    "confidence": round(confidence, 3),
                    "bbox": {
                        "x1": x1, "y1": y1, "x2": x2, "y2": y2,
                        "width": x2 - x1, "height": y2 - y1
                    },
                    "meets_threshold": confidence >= self.confidence_threshold
                })
            
            return detailed_results
            
        except Exception as e:
            self.logger.error(f"Error extracting detailed OCR results from {file_path}: {e}")
            return []
    
    def get_text_regions(self, file_path: Path, min_confidence: float = None) -> List[str]:
        """Extract text regions as separate strings"""
        if min_confidence is None:
            min_confidence = self.confidence_threshold
            
        try:
            results = self.reader.readtext(str(file_path))
            text_regions = []
            
            for bbox, text, confidence in results:
                if confidence >= min_confidence:
                    text_regions.append(text.strip())
            
            return text_regions
            
        except Exception as e:
            self.logger.error(f"Error extracting text regions from {file_path}: {e}")
            return []
    
    def estimate_reading_order(self, file_path: Path) -> str:
        """Attempt to order OCR results in reading order (top-to-bottom, left-to-right)"""
        try:
            results = self.reader.readtext(str(file_path), detail=1)
            
            # Filter by confidence and sort by position
            good_results = [(bbox, text, conf) for bbox, text, conf in results 
                           if conf >= self.confidence_threshold]
            
            # Sort by y-coordinate (top to bottom), then x-coordinate (left to right)
            def sort_key(item):
                bbox, text, conf = item
                y_center = (bbox[0][1] + bbox[2][1]) / 2  # Average y-coordinate
                x_center = (bbox[0][0] + bbox[2][0]) / 2  # Average x-coordinate
                return (y_center, x_center)
            
            sorted_results = sorted(good_results, key=sort_key)
            
            # Extract text in reading order
            ordered_text = [text for _, text, _ in sorted_results]
            return self.clean_text(" ".join(ordered_text))
            
        except Exception as e:
            self.logger.error(f"Error estimating reading order from {file_path}: {e}")
            return self.extract_text(file_path)  # Fallback to regular extraction