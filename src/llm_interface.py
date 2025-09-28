"""
LLM interfaces for Document RAG Extractor
Supports both local Ollama and OpenAI API models
"""
import os
import json
import requests
from typing import Dict, Any, Optional
import logging
from abc import ABC, abstractmethod

# Try to import OpenAI - make it optional
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    openai = None

logger = logging.getLogger(__name__)

class LLMInterface(ABC):
    """Abstract base class for LLM interfaces"""
    
    @abstractmethod
    def generate(self, prompt: str) -> str:
        """Generate response from the model"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the model is available"""
        pass

class OllamaInterface(LLMInterface):
    """Interface for local Ollama models"""
    
    def __init__(self, model_name: str = "llama3.2", base_url: str = "http://localhost:11434", timeout: int = 120):
        self.model_name = model_name
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        
    def generate(self, prompt: str) -> str:
        """Generate response using Ollama API"""
        try:
            url = f"{self.base_url}/api/generate"
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1,
                    "top_p": 0.9
                }
            }
            
            logger.debug(f"Sending request to Ollama: {url}")
            response = requests.post(url, json=payload, timeout=self.timeout)
            response.raise_for_status()
            
            result = response.json()
            return result.get('response', '')
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Ollama API error: {e}")
            raise Exception(f"Failed to get response from Ollama: {e}")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Ollama response: {e}")
            raise Exception(f"Invalid JSON response from Ollama: {e}")
    
    def is_available(self) -> bool:
        """Check if Ollama is available"""
        try:
            url = f"{self.base_url}/api/tags"
            response = requests.get(url, timeout=5)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False

class OpenAIInterface(LLMInterface):
    """Interface for OpenAI API models"""
    
    def __init__(self, model_name: str = "gpt-3.5-turbo", api_key: Optional[str] = None, 
                 max_tokens: int = 2000, temperature: float = 0.1):
        
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI package not installed. Install with: pip install openai")
        
        self.model_name = model_name
        self.max_tokens = max_tokens
        self.temperature = temperature
        
        # Set API key
        api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OpenAI API key not provided. Set OPENAI_API_KEY environment variable.")
        
        # Initialize client for newer OpenAI library versions
        try:
            self.client = openai.OpenAI(api_key=api_key)
        except AttributeError:
            # Fallback for older versions
            openai.api_key = api_key
            self.client = None
    
    def generate(self, prompt: str) -> str:
        """Generate response using OpenAI API"""
        try:
            if self.client:  # New API
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=self.max_tokens,
                    temperature=self.temperature
                )
                return response.choices[0].message.content.strip()
            
            else:  # Old API
                response = openai.ChatCompletion.create(
                    model=self.model_name,
                    messages=[
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=self.max_tokens,
                    temperature=self.temperature
                )
                return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise Exception(f"Failed to get response from OpenAI: {e}")
    
    def is_available(self) -> bool:
        """Check if OpenAI API is available"""
        if not OPENAI_AVAILABLE:
            return False
            
        try:
            # Simple test with minimal tokens
            if self.client:
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[{"role": "user", "content": "test"}],
                    max_tokens=1
                )
            else:
                response = openai.ChatCompletion.create(
                    model=self.model_name,
                    messages=[{"role": "user", "content": "test"}],
                    max_tokens=1
                )
            return True
        except Exception:
            return False

class LLMFactory:
    """Factory for creating LLM interfaces"""
    
    @staticmethod
    def create_llm(model_config: Dict[str, Any], model_type: str) -> LLMInterface:
        """Create appropriate LLM interface based on configuration"""
        
        if model_type == "ollama":
            return OllamaInterface(
                model_name=model_config.get("model_name", "llama3.2"),
                base_url=model_config.get("base_url", "http://localhost:11434"),
                timeout=model_config.get("timeout", 120)
            )
        
        elif model_type == "openai":
            return OpenAIInterface(
                model_name=model_config.get("model_name", "gpt-3.5-turbo"),
                max_tokens=model_config.get("max_tokens", 2000),
                temperature=model_config.get("temperature", 0.1)
            )
        
        else:
            raise ValueError(f"Unsupported model type: {model_type}")
    
    @staticmethod
    def get_available_models() -> Dict[str, bool]:
        """Check availability of different model types"""
        results = {}
        
        # Check Ollama
        try:
            ollama = OllamaInterface()
            results["ollama"] = ollama.is_available()
        except Exception:
            results["ollama"] = False
        
        # Check OpenAI
        try:
            if os.getenv('OPENAI_API_KEY') and OPENAI_AVAILABLE:
                openai_interface = OpenAIInterface()
                results["openai"] = openai_interface.is_available()
            else:
                results["openai"] = False
        except Exception:
            results["openai"] = False
        
        return results