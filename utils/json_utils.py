"""
JSON utilities for data processing and output
"""
import json
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def save_json(data: Dict[str, Any], output_path: Path, indent: int = 2) -> bool:
    """Save data as JSON file with proper formatting"""
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent, ensure_ascii=False, default=str)
        logger.info(f"Saved JSON data to {output_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to save JSON to {output_path}: {e}")
        return False

def load_json(file_path: Path) -> Dict[str, Any]:
    """Load JSON data from file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        logger.info(f"Loaded JSON data from {file_path}")
        return data
    except Exception as e:
        logger.error(f"Failed to load JSON from {file_path}: {e}")
        return {}

def create_extraction_summary(processed_results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Create a summary of extraction results"""
    successful = [r for r in processed_results if r.get('success', False)]
    failed = [r for r in processed_results if not r.get('success', False)]
    
    # Count by file type
    file_types = {}
    for result in processed_results:
        file_type = result.get('file_type', 'unknown')
        if file_type not in file_types:
            file_types[file_type] = {'total': 0, 'successful': 0, 'failed': 0}
        
        file_types[file_type]['total'] += 1
        if result.get('success', False):
            file_types[file_type]['successful'] += 1
        else:
            file_types[file_type]['failed'] += 1
    
    # Calculate text statistics
    total_chars = sum(len(r.get('text_content', '')) for r in successful)
    avg_chars = total_chars / len(successful) if successful else 0
    
    return {
        "processing_summary": {
            "total_files": len(processed_results),
            "successful": len(successful),
            "failed": len(failed),
            "success_rate": f"{(len(successful) / len(processed_results) * 100):.1f}%" if processed_results else "0%"
        },
        "by_file_type": file_types,
        "text_statistics": {
            "total_characters": total_chars,
            "average_characters_per_file": round(avg_chars, 1)
        },
        "failed_files": [
            {
                "file": r.get('file_name'),
                "error": r.get('error'),
                "processor": r.get('processor')
            }
            for r in failed
        ] if failed else []
    }

def structure_extracted_data(processed_results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Structure the extracted data for the final JSON output"""
    
    # Filter successful extractions
    successful_extractions = [r for r in processed_results if r.get('success', False)]
    
    # Create the main data structure
    structured_data = {
        "metadata": {
            "extraction_date": datetime.now().isoformat(),
            "total_documents": len(successful_extractions),
            "source_directory": "docs/",
            "extraction_tool": "SAP Document Processor v1.0"
        },
        "documents": [],
        "summary": create_extraction_summary(processed_results)
    }
    
    # Process each document
    for result in successful_extractions:
        document_data = {
            "file_info": {
                "name": result.get('file_name'),
                "path": result.get('file_path'),
                "type": result.get('file_type'),
                "processor": result.get('processor'),
                "processed_at": result.get('processed_at')
            },
            "content": {
                "raw_text": result.get('text_content', ''),
                "text_length": len(result.get('text_content', '')),
                "preview": result.get('text_content', '')[:200] + "..." if len(result.get('text_content', '')) > 200 else result.get('text_content', '')
            },
            "metadata": result.get('metadata', {}),
            # Placeholder for future LLM processing
            "extracted_info": {
                "products": [],
                "integrations": [],
                "relationships": [],
                "security": [],
                "extraction_status": "pending_llm_processing"
            }
        }
        
        structured_data["documents"].append(document_data)
    
    return structured_data

def merge_extraction_results(existing_data: Dict[str, Any], new_results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Merge new extraction results with existing data"""
    if not existing_data:
        return structure_extracted_data(new_results)
    
    # Update metadata
    existing_data["metadata"]["last_updated"] = datetime.now().isoformat()
    
    # Merge new documents (avoiding duplicates by filename)
    existing_files = {doc["file_info"]["name"] for doc in existing_data.get("documents", [])}
    
    new_structured = structure_extracted_data(new_results)
    for doc in new_structured["documents"]:
        if doc["file_info"]["name"] not in existing_files:
            existing_data["documents"].append(doc)
    
    # Update counts
    existing_data["metadata"]["total_documents"] = len(existing_data["documents"])
    
    # Update summary
    all_results = [{"success": True, **doc} for doc in existing_data["documents"]]
    existing_data["summary"] = create_extraction_summary(all_results)
    
    return existing_data