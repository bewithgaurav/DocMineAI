#!/bin/bash
# Quick Start Script for DocMineAI
# This script helps new users test the framework quickly

echo "🚀 DocMineAI - Quick Start"
echo "========================="

# Check if we're in the right directory
if [ ! -f "extract.py" ]; then
    echo "❌ Please run this script from the project root directory"
    exit 1
fi

# Check Python installation
echo "📋 Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+"
    exit 1
fi

# Check virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  Virtual environment not activated. Creating one..."
    python3 -m venv venv
    source venv/bin/activate
    echo "✅ Virtual environment created and activated"
fi

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

# Check model availability
echo "🤖 Checking model availability..."
python extract.py --check-models

# Test with example configuration
echo "\n🧪 Testing with business configuration..."
if [ -d "examples/sample_docs" ] && [ "$(ls -A examples/sample_docs)" ]; then
    python extract.py --config examples/configs/business_config.yaml --docs-dir examples/sample_docs --output examples/outputs/test_results.yaml
    echo "✅ Test extraction completed! Check examples/outputs/test_results.yaml"
else
    echo "⚠️  No sample documents found. Add some documents to examples/sample_docs/ and rerun"
fi

echo "\n🎉 Quick start completed!"
echo "\nNext steps:"
echo "1. Add your documents to a folder (e.g., 'docs/')"
echo "2. Run: python extract.py --docs-dir docs/"
echo "3. Customize config files in examples/configs/ for your needs"
echo "\nFor help: python extract.py --help"