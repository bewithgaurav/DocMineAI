# 📚 DocMineAI Examples Directory

This directory contains practical examples and templates to help you get started with the DocMineAI framework - your AI-powered document intelligence solution.

## 📁 Contents

### 🔧 Configuration Examples
- **`configs/`** - Ready-to-use configuration files for different use cases
  - `research_config.yaml` - Academic/research document processing
  - `business_config.yaml` - Business document analysis
  - `legal_config.yaml` - Legal document processing
  - `technical_config.yaml` - Technical documentation extraction

### 📝 Prompt Templates
- **`prompts/`** - Custom prompt templates for various domains
  - `academic_prompts.yaml` - Research paper analysis
  - `business_prompts.yaml` - Business document extraction
  - `legal_prompts.yaml` - Legal document analysis
  - `medical_prompts.yaml` - Medical document processing

### 📄 Sample Documents
- **`sample_docs/`** - Sample documents for testing
  - `sample.pdf` - Sample PDF document
  - `sample.docx` - Sample Word document
  - `sample.png` - Sample image with text

### 📊 Output Examples
- **`outputs/`** - Example extraction results
  - `sample_extraction.yaml` - Example output format
  - `business_analysis.yaml` - Business document results
  - `research_results.yaml` - Academic extraction results

### 🚀 Quick Start Scripts
- **`scripts/`** - Helper scripts and automation
  - `quick_start.sh` - One-command setup and test
  - `batch_process.py` - Process multiple document folders
  - `validate_setup.py` - Check installation and dependencies

## 🎯 Use Cases

### 1. Academic Research
Extract key information from research papers, theses, and academic documents.

### 2. Business Intelligence  
Analyze contracts, reports, and business documents for insights.

### 3. Legal Document Review
Process legal documents for compliance, terms, and key clauses.

### 4. Technical Documentation
Extract APIs, integrations, and technical specifications from manuals.

### 5. Medical Records
Process medical documents for patient information and treatment details.

## 🛠️ How to Use Examples

1. **Copy a configuration**: `cp examples/configs/business_config.yaml my_config.yaml`
2. **Customize prompts**: Edit the extraction prompts for your specific needs
3. **Test with samples**: Use the sample documents to verify your setup
4. **Run extraction**: `python extract.py --config my_config.yaml --docs-dir examples/sample_docs`

## 📖 Learning Path

1. Start with `configs/business_config.yaml` for general use
2. Try the sample documents to understand output format
3. Customize prompts based on your document types
4. Create your own configuration for your specific domain
