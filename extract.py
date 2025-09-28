#!/usr/bin/env python3
"""
DocMineAI - Main CLI Interface

AI-powered document intelligence framework for extracting structured
information from documents using RAG and LLMs.
"""

import argparse
import logging
import sys
from pathlib import Path
from datetime import datetime
import yaml

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from config_manager import ConfigManager, PromptsManager
from llm_interface import LLMFactory
from text_processor import TextProcessor, YAMLProcessor

# Import existing document processors
from processors.pdf_processor import PDFProcessor
from processors.docx_processor import DocxProcessor
from processors.image_processor import ImageProcessor
from utils.file_utils import get_supported_files, validate_file_size

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DocumentRAGExtractor:
    """Main extractor class"""
    
    def __init__(self, config_path: str = None, prompts_path: str = None, model_type: str = None):
        # Load configuration
        self.config_manager = ConfigManager(Path(config_path) if config_path else None)
        self.prompts_manager = PromptsManager(Path(prompts_path) if prompts_path else None)
        
        # Get configuration
        self.general_config = self.config_manager.get_general_config()
        self.processing_config = self.config_manager.get_processing_config()
        
        # Initialize text processor
        self.text_processor = TextProcessor(
            chunk_size=self.general_config.get('chunk_size', 2000),
            overlap=self.general_config.get('overlap', 200)
        )
        
        # Initialize LLM
        model_type = model_type or self.config_manager.config['models']['default']
        model_config = self.config_manager.get_model_config(model_type)
        self.llm = LLMFactory.create_llm(model_config, model_type)
        self.model_type = model_type
        
        # Initialize document processors
        self.processors = self._initialize_processors()
        
        logger.info(f"DocMineAI initialized with {model_type} model")
    
    def _initialize_processors(self):
        """Initialize document processors"""
        processors = {}
        
        try:
            processors['pdf'] = PDFProcessor()
            logger.info("PDF processor initialized")
        except ImportError as e:
            logger.warning(f"PDF processor not available: {e}")
        
        try:
            processors['docx'] = DocxProcessor()
            logger.info("DOCX processor initialized")
        except ImportError as e:
            logger.warning(f"DOCX processor not available: {e}")
        
        try:
            processors['image'] = ImageProcessor()
            logger.info("Image processor initialized")
        except ImportError as e:
            logger.warning(f"Image processor not available: {e}")
        
        return processors
    
    def process_documents(self, docs_dir: str = "docs") -> dict:
        """Process all documents in the specified directory"""
        docs_path = Path(docs_dir)
        
        if not docs_path.exists():
            raise FileNotFoundError(f"Documents directory not found: {docs_path}")
        
        # Get supported files
        supported_extensions = {
            'pdf': ['.pdf'],
            'docx': ['.docx', '.doc'],
            'image': ['.png', '.jpg', '.jpeg', '.bmp', '.tiff'],
            'txt': ['.txt']
        }
        
        files_by_type = get_supported_files(docs_path, supported_extensions)
        
        # Process documents to extract text
        extracted_texts = []
        
        for file_type, files in files_by_type.items():
            if not files:
                continue
            
            logger.info(f"Processing {len(files)} {file_type} files...")
            
            for file_path in files:
                logger.info(f"Processing {file_path.name}...")
                
                if not validate_file_size(file_path, self.processing_config.get('max_file_size_mb', 100)):
                    continue
                
                try:
                    if file_type == 'txt':
                        # Handle text files directly
                        with open(file_path, 'r', encoding='utf-8') as f:
                            text = f.read()
                        
                        extracted_texts.append({
                            'file_name': file_path.name,
                            'file_type': file_type,
                            'text': self.text_processor.clean_text(text)
                        })
                    
                    else:
                        # Use appropriate processor
                        processor = self.processors.get(file_type)
                        if processor:
                            result = processor.process(file_path)
                            if result.get('success'):
                                extracted_texts.append({
                                    'file_name': file_path.name,
                                    'file_type': file_type,
                                    'text': result.get('text_content', '')
                                })
                
                except Exception as e:
                    logger.error(f"Error processing {file_path.name}: {e}")
        
        logger.info(f"Successfully extracted text from {len(extracted_texts)} documents")
        
        # Now extract structured information using LLM
        return self.extract_information(extracted_texts)
    
    def extract_information(self, extracted_texts: list) -> dict:
        """Extract structured information from texts using LLM"""
        extraction_schema = self.config_manager.get_extraction_schema()
        extraction_types = list(extraction_schema.keys())
        
        logger.info(f"Extracting information for: {extraction_types}")
        
        results = {
            'extraction_metadata': {
                'timestamp': datetime.now().isoformat(),
                'model_used': self.model_type,
                'total_documents': len(extracted_texts),
                'extraction_types': extraction_types
            }
        }
        
        # Initialize result structure
        for extraction_type in extraction_types:
            results[extraction_type] = []
        
        for doc_info in extracted_texts:
            logger.info(f"Processing {doc_info['file_name']} for information extraction...")
            
            text = doc_info['text']
            chunks = self.text_processor.chunk_text(text)
            
            logger.info(f"  Split into {len(chunks)} chunks")
            
            for extraction_type in extraction_types:
                logger.info(f"  Extracting {extraction_type}...")
                
                type_results = []
                
                for i, chunk in enumerate(chunks):
                    # Skip small chunks
                    if len(chunk) < self.processing_config.get('min_chunk_length', 50):
                        continue
                    
                    try:
                        # Format prompt
                        prompt = self.prompts_manager.format_prompt(extraction_type, chunk)
                        
                        # Get LLM response
                        logger.debug(f"    Processing chunk {i+1}/{len(chunks)}")
                        response = self.llm.generate(prompt)
                        
                        # Parse YAML response
                        parsed_data = YAMLProcessor.parse_yaml_from_text(response)
                        
                        # Add to results if data found
                        if parsed_data and extraction_type in parsed_data:
                            type_results.append(parsed_data[extraction_type])
                    
                    except Exception as e:
                        logger.error(f"Error processing chunk {i+1} for {extraction_type}: {e}")
                        continue
                
                # Merge results for this extraction type
                if type_results:
                    merged_results = YAMLProcessor.merge_yaml_results([{extraction_type: r} for r in type_results])
                    if extraction_type in merged_results:
                        results[extraction_type].extend(merged_results[extraction_type])
        
        return results
    
    def save_results(self, results: dict, output_file: str = None) -> str:
        """Save results to YAML file"""
        output_path = Path(output_file or self.general_config.get('output_file', 'output/extracted_data.yaml'))
        
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            yaml.dump(results, f, default_flow_style=False, allow_unicode=True, indent=2)
        
        logger.info(f"Results saved to {output_path}")
        return str(output_path)

def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(description="DocMineAI - Extract structured information from documents using AI")
    
    parser.add_argument('--docs-dir', default='docs', help='Directory containing documents to process')
    parser.add_argument('--config', help='Path to configuration file')
    parser.add_argument('--prompts', help='Path to prompts file')
    parser.add_argument('--model', choices=['ollama', 'openai'], help='Model type to use')
    parser.add_argument('--output', help='Output file path')
    parser.add_argument('--check-models', action='store_true', help='Check availability of models')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Check model availability
    if args.check_models:
        print("Checking model availability...")
        available_models = LLMFactory.get_available_models()
        
        for model_type, is_available in available_models.items():
            status = "✅ Available" if is_available else "❌ Not available"
            print(f"  {model_type}: {status}")
        
        return
    
    try:
        # Initialize extractor
        extractor = DocumentRAGExtractor(
            config_path=args.config,
            prompts_path=args.prompts,
            model_type=args.model
        )
        
        # Process documents
        print("🚀 Starting document extraction...")
        results = extractor.process_documents(args.docs_dir)
        
        # Save results
        output_file = extractor.save_results(results, args.output)
        
        # Print summary
        print("\n" + "="*60)
        print("EXTRACTION SUMMARY")
        print("="*60)
        print(f"Model used: {results['extraction_metadata']['model_used']}")
        print(f"Documents processed: {results['extraction_metadata']['total_documents']}")
        print(f"Extraction types: {', '.join(results['extraction_metadata']['extraction_types'])}")
        
        for extraction_type in results['extraction_metadata']['extraction_types']:
            count = len(results.get(extraction_type, []))
            print(f"  {extraction_type}: {count} items")
        
        print(f"\n✅ Results saved to: {output_file}")
        print("="*60)
        
    except Exception as e:
        logger.error(f"Extraction failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()