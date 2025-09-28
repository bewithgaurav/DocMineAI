# ⛏️ DocMineAI

AI-powered document intelligence framework for extracting structured information from any document type. Powered by **Retrieval-Augmented Generation (RAG)** and Large Language Models, DocMineAI processes PDFs, Word documents, and images to mine specific data categories with intelligent text chunking and configurable extraction schemas.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![AI Powered](https://img.shields.io/badge/AI-Powered-brightgreen.svg)](https://github.com/yourusername/docmineai)

## ✨ Features

- 🔍 **Multi-format Support**: Process PDFs, Word documents (.docx), and images (PNG, JPG)
- 🤖 **Multiple LLM Providers**: Ollama (local) and OpenAI API support
- 🎯 **Customizable Extraction**: Define any extraction categories via YAML configuration
- 📊 **Intelligent Text Processing**: Smart chunking with configurable overlap
- 🛠️ **CLI Interface**: Easy-to-use command-line tool
- 🔧 **Highly Configurable**: Customize prompts, models, chunk sizes, and extraction schemas
- 📈 **Robust Error Handling**: Graceful fallbacks and detailed logging
- 🌟 **Production Ready**: Modular architecture for easy extension

---
> **🚀 NEW USER? START HERE!**  
> Check out the **[`examples/`](examples/)** directory for:
> - Ready-to-use configurations for different document types
> - Sample documents and expected outputs  
> - One-command setup and testing scripts
> - Step-by-step customization guides
---

## 🚀 Quick Start

> **👉 New to the framework? Start with the [`examples/`](examples/) directory for ready-to-use configurations and step-by-step guides!**

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/docmineai.git
cd docmineai

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Quick Setup & Test

```bash
# Validate your installation
python examples/scripts/validate_setup.py

# One-command setup and test (if you have Ollama)
./examples/scripts/quick_start.sh
```

### 3. Set up Local LLM (Recommended)

Install [Ollama](https://ollama.ai/) and pull a model:

```bash
# Install Ollama (visit https://ollama.ai for installation)
ollama pull llama3.2
```

### 4. Basic Usage

```bash
# Extract information from documents
python extract.py --docs-dir documents/ --model ollama --output results.yaml

# Check available models
python extract.py --check-models

# Use custom configuration
python extract.py --config my_config.yaml --prompts my_prompts.yaml
```

## � Getting Started with Examples

**🌟 The fastest way to understand and use this framework is through the [`examples/`](examples/) directory!**

### 🎯 Ready-to-Use Configurations
- **Business Documents**: `examples/configs/business_config.yaml` - Contracts, financial reports
- **Academic Research**: `examples/configs/research_config.yaml` - Research papers, theses  
- **Legal Documents**: `examples/configs/legal_config.yaml` - Legal contracts, compliance

### 🚀 Quick Start Scripts
```bash
# Validate your setup
python examples/scripts/validate_setup.py

# Auto-setup and test
./examples/scripts/quick_start.sh

# Process multiple folders at once
python examples/scripts/batch_process.py --input-dirs folder1 folder2
```

### 📖 Learning Path
1. **Start here**: Check out [`examples/README.md`](examples/README.md)
2. **Test run**: `python extract.py --config examples/configs/business_config.yaml --docs-dir examples/sample_docs`
3. **See outputs**: Look at `examples/outputs/` for example extraction results
4. **Customize**: Copy a config file and modify for your needs

## �📖 Usage Guide

### Command Line Interface

```bash
python extract.py [OPTIONS]

Options:
  --docs-dir DIR          Directory containing documents to process
  --config FILE          Path to configuration file (default: config/extraction_config.yaml)
  --prompts FILE          Path to prompts file (default: prompts/custom_prompts.yaml)
  --model {ollama,openai} Model type to use (default: ollama)
  --output FILE          Output file path (default: output/extracted_data.yaml)
  --check-models         Check availability of models
  --verbose, -v          Enable verbose logging
  --help                 Show this help message
```

### Examples

**Basic extraction:**
```bash
python extract.py --docs-dir ./documents --output my_results.yaml
```

**With OpenAI API:**
```bash
export OPENAI_API_KEY="your-api-key-here"
python extract.py --model openai --docs-dir ./documents
```

**Custom configuration:**
```bash
python extract.py --config configs/research_config.yaml --prompts prompts/academic_prompts.yaml
```

**Verbose logging:**
```bash
python extract.py --docs-dir ./docs --verbose
```

## ⚙️ Configuration

### Main Configuration File (`config/extraction_config.yaml`)

```yaml
# General settings
general:
  chunk_size: 2000          # Text chunk size for processing
  overlap: 200              # Overlap between chunks
  output_file: "output/extracted_data.yaml"

# Model configuration
models:
  default: "ollama"         # Default model to use
  ollama:
    model_name: "llama3.2"
    base_url: "http://localhost:11434"
    timeout: 120
  openai:
    model_name: "gpt-4"
    api_key: "${OPENAI_API_KEY}"  # Environment variable
    timeout: 60

# Define what information to extract
extraction_schema:
  products:
    description: "Products, services, or solutions mentioned"
    fields:
      - name: "Product name"
      - description: "What it does"
      - category: "Product category"
  
  integrations:
    description: "Integration capabilities and requirements"
    fields:
      - type: "Integration type"
      - protocol: "Technical protocol"
      - description: "Integration details"
  
  # Add any custom categories
  compliance:
    description: "Compliance and regulatory information"
    fields:
      - standard: "Compliance standard"
      - requirement: "Specific requirement"

# Processing settings
processing:
  supported_extensions: [".pdf", ".docx", ".png", ".jpg", ".jpeg"]
  max_file_size_mb: 100
  min_chunk_length: 50
```

### Custom Prompts (`prompts/custom_prompts.yaml`)

```yaml
system_prompt: |
  You are an expert document analyzer specializing in extracting structured information.
  Your task is to analyze text and extract specific information categories accurately.

extraction_prompts:
  products: |
    Extract information about products, services, or solutions mentioned in the text.
    Focus on identifying:
    - Product names
    - Brief descriptions of what they do
    - Product categories or types
    
    Format your response as a YAML list with clear structure.

  integrations: |
    Extract information about technical integrations, APIs, or connectivity options.
    Look for:
    - Integration types (API, connector, etc.)
    - Technical protocols (REST, SOAP, HTTP, etc.)
    - Integration requirements or capabilities
    
    Format your response as a YAML list.
```

## 📁 Project Structure

```
docmineai/
├── extract.py              # Main CLI interface
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── .gitignore            # Git ignore rules
├── examples/ ⭐            # 👈 START HERE! Ready-to-use examples
│   ├── configs/           # Pre-built configurations
│   ├── prompts/           # Domain-specific prompts  
│   ├── scripts/           # Helper and setup scripts
│   ├── sample_docs/       # Test documents
│   └── outputs/           # Example extraction results
├── config/
│   └── extraction_config.yaml  # Main configuration
├── prompts/
│   ├── custom_prompts.yaml     # Customizable prompts
│   └── example_prompts/
│       └── sap_prompts.yaml    # Example: SAP-specific prompts
├── src/                   # Core framework modules
│   ├── config_manager.py  # Configuration management
│   ├── llm_interface.py   # LLM provider interfaces
│   └── text_processor.py  # Text processing utilities
├── processors/            # Document processors
│   ├── base_processor.py  # Base processor class
│   ├── pdf_processor.py   # PDF processing
│   ├── docx_processor.py  # Word document processing
│   └── image_processor.py # Image OCR processing
└── utils/                 # Utility modules
    ├── file_utils.py      # File handling utilities
    └── json_utils.py      # JSON processing utilities
```

## 🔧 Customization

### Adding New Extraction Categories

Edit `config/extraction_config.yaml`:

```yaml
extraction_schema:
  # Add your custom category
  financial_info:
    description: "Financial data and metrics"
    fields:
      - metric: "Financial metric name"
      - value: "Metric value"
      - period: "Time period"
```

### Custom Prompts

Edit `prompts/custom_prompts.yaml`:

```yaml
extraction_prompts:
  financial_info: |
    Extract financial information from the text including:
    - Revenue figures
    - Profit margins  
    - Financial metrics
    - Time periods
    
    Return structured YAML format.
```

### Adding New Document Processors

1. Create a new processor in `processors/`:

```python
from processors.base_processor import BaseProcessor

class MyProcessor(BaseProcessor):
    def __init__(self):
        super().__init__()
        
    def extract_text(self, file_path: str) -> str:
        # Implement your text extraction logic
        pass
        
    def extract_metadata(self, file_path: str) -> dict:
        # Extract file metadata
        pass
```

2. Register it in `extract.py`

## 🛠️ Development

### Setting Up Development Environment

```bash
# Clone and setup
git clone https://github.com/yourusername/docmineai.git
cd docmineai
python -m venv venv
source venv/bin/activate

# Install in development mode
pip install -r requirements.txt
pip install -e .
```

### Running Tests

```bash
# Test with sample documents
mkdir test_docs
# Add some test files
python extract.py --docs-dir test_docs --verbose
```

## 📋 Requirements

### System Requirements
- Python 3.8+
- 2GB+ RAM (for local LLM processing)
- Internet connection (for OpenAI API or Ollama model downloads)

### Key Dependencies
- `pdfplumber` - PDF text extraction
- `python-docx` - Word document processing  
- `easyocr` - Optical Character Recognition
- `PyYAML` - Configuration management
- `requests` - HTTP requests for APIs
- `Pillow` - Image processing

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes**
4. **Add tests** for new functionality
5. **Commit your changes**: `git commit -m 'Add amazing feature'`
6. **Push to the branch**: `git push origin feature/amazing-feature`
7. **Open a Pull Request**

### Contribution Ideas
- 🆕 New document format processors (Excel, PowerPoint, etc.)
- 🤖 Additional LLM provider integrations
- 📊 Enhanced metadata extraction
- 🔧 Performance optimizations
- 📚 Documentation improvements
- 🧪 Test coverage expansion

## ❓ Troubleshooting

### Common Issues

**Issue: `ModuleNotFoundError` for dependencies**
```bash
# Solution: Install requirements
pip install -r requirements.txt
```

**Issue: Ollama connection failed**
```bash
# Check if Ollama is running
ollama serve
ollama list
```

**Issue: Out of memory errors**
```bash
# Reduce chunk size in config
general:
  chunk_size: 1000  # Smaller chunks
```

**Issue: Poor extraction quality**
- Try different models (`llama3.2`, `gpt-4`)
- Adjust prompts for your specific use case
- Verify document quality and text clarity

### Getting Help

- 📖 Check the [documentation](https://github.com/yourusername/document-rag-extractor/wiki)
- 🐛 Report bugs via [GitHub Issues](https://github.com/yourusername/document-rag-extractor/issues)
- 💬 Join discussions in [GitHub Discussions](https://github.com/yourusername/document-rag-extractor/discussions)

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Ollama](https://ollama.ai/) - For making local LLMs accessible
- [pdfplumber](https://github.com/jsvine/pdfplumber) - Excellent PDF processing
- [EasyOCR](https://github.com/JaidedAI/EasyOCR) - Reliable OCR capabilities
- The open-source community for continuous inspiration

---

> 🚀 **Ready to extract insights from your documents?**  
> Start with the **[`examples/`](examples/)** directory and follow the step-by-step guides!

*Star ⭐ this repository if it helps you extract insights from your documents!*