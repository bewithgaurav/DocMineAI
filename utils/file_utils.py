"""
File utilities for document processing
"""
from pathlib import Path
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

def get_supported_files(directory: Path, extensions: Dict[str, List[str]]) -> Dict[str, List[Path]]:
    """Get all supported files organized by type"""
    if not directory.exists():
        logger.error(f"Directory does not exist: {directory}")
        return {}
    
    files_by_type = {file_type: [] for file_type in extensions.keys()}
    
    for file_path in directory.iterdir():
        if file_path.is_file():
            file_ext = file_path.suffix.lower()
            
            # Check which type this file belongs to
            for file_type, type_extensions in extensions.items():
                if file_ext in type_extensions:
                    files_by_type[file_type].append(file_path)
                    break
    
    # Log summary
    total_files = sum(len(files) for files in files_by_type.values())
    logger.info(f"Found {total_files} supported files in {directory}")
    for file_type, files in files_by_type.items():
        if files:
            logger.info(f"  {file_type}: {len(files)} files")
    
    return files_by_type

def validate_file_size(file_path: Path, max_size_mb: int) -> bool:
    """Check if file size is within limits"""
    try:
        size_mb = file_path.stat().st_size / (1024 * 1024)
        if size_mb > max_size_mb:
            logger.warning(f"File {file_path.name} is {size_mb:.1f}MB, exceeds limit of {max_size_mb}MB")
            return False
        return True
    except Exception as e:
        logger.error(f"Error checking file size for {file_path}: {e}")
        return False

def ensure_output_directory(output_dir: Path) -> bool:
    """Ensure output directory exists"""
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        logger.error(f"Failed to create output directory {output_dir}: {e}")
        return False

def backup_existing_file(file_path: Path) -> bool:
    """Create a backup of existing file"""
    if not file_path.exists():
        return True
    
    try:
        backup_path = file_path.with_suffix(f'{file_path.suffix}.backup')
        counter = 1
        while backup_path.exists():
            backup_path = file_path.with_suffix(f'{file_path.suffix}.backup.{counter}')
            counter += 1
        
        file_path.rename(backup_path)
        logger.info(f"Created backup: {backup_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to create backup for {file_path}: {e}")
        return False