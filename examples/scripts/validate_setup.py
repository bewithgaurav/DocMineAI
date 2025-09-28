#!/usr/bin/env python3
"""
Setup Validation Script for DocMineAI

This script validates that the installation is working correctly
and all dependencies are properly installed.
"""

import sys
import os
import subprocess
import importlib.util
from pathlib import Path

def check_python_version():
    """Check if Python version is 3.8+"""
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - OK")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} - Need Python 3.8+")
        return False

def check_module(module_name, package_name=None):
    """Check if a Python module can be imported"""
    try:
        importlib.import_module(module_name)
        print(f"✅ {package_name or module_name} - Available")
        return True
    except ImportError:
        print(f"❌ {package_name or module_name} - Not available")
        return False

def check_file_exists(filepath):
    """Check if a file exists"""
    if os.path.exists(filepath):
        print(f"✅ {filepath} - Found")
        return True
    else:
        print(f"❌ {filepath} - Not found")
        return False

def check_ollama():
    """Check if Ollama is available"""
    try:
        result = subprocess.run(
            ["ollama", "list"], 
            capture_output=True, 
            text=True, 
            timeout=10
        )
        if result.returncode == 0:
            print("✅ Ollama - Available")
            models = result.stdout.strip()
            if "llama" in models.lower():
                print("✅ Llama model - Found")
            else:
                print("⚠️  Llama model - Not found (run: ollama pull llama3.2)")
            return True
        else:
            print("❌ Ollama - Not responding")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("❌ Ollama - Not installed or not in PATH")
        return False

def main():
    print("🔍 DocMineAI - Setup Validation")
    print("=" * 50)
    
    checks_passed = 0
    total_checks = 0
    
    # Check Python version
    total_checks += 1
    if check_python_version():
        checks_passed += 1
    
    # Check core dependencies
    dependencies = [
        ("pdfplumber", "PDF processing"),
        ("docx", "python-docx (Word processing)"),
        ("easyocr", "EasyOCR (Image OCR)"),
        ("PIL", "Pillow (Image processing)"),
        ("yaml", "PyYAML (Configuration)"),
        ("requests", "HTTP requests"),
    ]
    
    for module, description in dependencies:
        total_checks += 1
        if check_module(module, description):
            checks_passed += 1
    
    # Check optional dependencies
    print("\\n📦 Optional Dependencies:")
    optional_deps = [
        ("openai", "OpenAI API client"),
    ]
    
    for module, description in optional_deps:
        check_module(module, description)
    
    # Check framework files
    print("\\n📁 Framework Files:")
    framework_files = [
        "extract.py",
        "config/extraction_config.yaml",
        "prompts/custom_prompts.yaml",
        "src/config_manager.py",
        "src/llm_interface.py",
        "processors/pdf_processor.py",
    ]
    
    for filepath in framework_files:
        total_checks += 1
        if check_file_exists(filepath):
            checks_passed += 1
    
    # Check Ollama
    print("\\n🤖 LLM Models:")
    total_checks += 1
    if check_ollama():
        checks_passed += 1
    
    # Check OpenAI API key
    openai_key = os.environ.get('OPENAI_API_KEY')
    if openai_key:
        print("✅ OPENAI_API_KEY - Set")
    else:
        print("⚠️  OPENAI_API_KEY - Not set (optional)")
    
    # Summary
    print("\\n" + "=" * 50)
    print(f"📊 VALIDATION SUMMARY")
    print("=" * 50)
    print(f"Checks passed: {checks_passed}/{total_checks}")
    
    if checks_passed == total_checks:
        print("🎉 All checks passed! Framework is ready to use.")
        print("\\nNext steps:")
        print("1. Add documents to docs/ folder")
        print("2. Run: python extract.py")
        return 0
    elif checks_passed >= total_checks * 0.8:
        print("⚠️  Most checks passed. Framework should work with minor issues.")
        print("\\nRecommended actions:")
        print("- Install missing dependencies: pip install -r requirements.txt")
        print("- Install Ollama: https://ollama.ai")
        return 1
    else:
        print("❌ Several checks failed. Please fix issues before using.")
        print("\\nRequired actions:")
        print("- Install dependencies: pip install -r requirements.txt")
        print("- Install Ollama: https://ollama.ai")
        print("- Verify Python 3.8+ is installed")
        return 2

if __name__ == "__main__":
    sys.exit(main())