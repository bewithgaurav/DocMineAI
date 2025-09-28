"""
Configuration management for Document RAG Extractor
"""
import yaml
from pathlib import Path
from typing import Dict, Any, Optional

class ConfigManager:
    """Manages configuration loading and validation"""
    
    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or Path("config/extraction_config.yaml")
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # Validate required sections
        self._validate_config(config)
        return config
    
    def _validate_config(self, config: Dict[str, Any]):
        """Validate configuration structure"""
        required_sections = ['general', 'models', 'extraction_schema', 'processing']
        
        for section in required_sections:
            if section not in config:
                raise ValueError(f"Missing required configuration section: {section}")
    
    def get_model_config(self, model_type: Optional[str] = None) -> Dict[str, Any]:
        """Get model configuration"""
        model_type = model_type or self.config['models']['default']
        
        if model_type not in self.config['models']:
            raise ValueError(f"Model type '{model_type}' not configured")
        
        return self.config['models'][model_type]
    
    def get_extraction_schema(self) -> Dict[str, Any]:
        """Get extraction schema definition"""
        return self.config['extraction_schema']
    
    def get_processing_config(self) -> Dict[str, Any]:
        """Get file processing configuration"""
        return self.config['processing']
    
    def get_general_config(self) -> Dict[str, Any]:
        """Get general configuration"""
        return self.config['general']

class PromptsManager:
    """Manages extraction prompts"""
    
    def __init__(self, prompts_path: Optional[Path] = None):
        self.prompts_path = prompts_path or Path("prompts/custom_prompts.yaml")
        self.prompts = self.load_prompts()
    
    def load_prompts(self) -> Dict[str, Any]:
        """Load prompts from YAML file"""
        if not self.prompts_path.exists():
            raise FileNotFoundError(f"Prompts file not found: {self.prompts_path}")
        
        with open(self.prompts_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def get_persona(self) -> str:
        """Get the AI persona for extractions"""
        return self.prompts.get('persona', '')
    
    def get_prompt_template(self, extraction_type: str) -> str:
        """Get prompt template for specific extraction type"""
        prompts = self.prompts.get('prompts', {})
        
        if extraction_type not in prompts:
            # Fallback to custom prompt
            return prompts.get('custom', {}).get('prompt_template', '')
        
        return prompts[extraction_type].get('prompt_template', '')
    
    def format_prompt(self, extraction_type: str, text_chunk: str) -> str:
        """Format a prompt with persona and text chunk"""
        template = self.get_prompt_template(extraction_type)
        persona = self.get_persona()
        
        return template.format(
            persona=persona,
            text_chunk=text_chunk
        )