#!/bin/bash
# Create Object Virtual Environment Activation Script
# This script activates the Python virtual environment for the create_object project

echo "🚀 Activating Create Object Virtual Environment..."
echo "=================================================="

# Navigate to project directory
PROJECT_DIR="/Users/mike/Dropbox/Code/repos/create_object"
cd "$PROJECT_DIR" || { echo "❌ Failed to navigate to project directory"; exit 1; }

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "⚠️  Virtual environment not found!"
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created!"
    echo ""
    echo "📦 Installing dependencies..."
    source venv/bin/activate
    pip install -r requirements.txt
    echo "✅ Dependencies installed!"
else
    # Activate virtual environment
    source venv/bin/activate
    echo "✅ Virtual environment activated!"
fi

echo "📍 Python location: $(which python)"
echo "📍 Python version: $(python --version)"
echo "📍 Working directory: $(pwd)"
echo ""
echo "🔧 Available commands:"
echo "   pytest                          # Run all tests"
echo "   pytest -v                       # Run tests with verbose output"
echo "   pytest --cov=.                  # Run tests with coverage"
echo "   python scripts/save_chat.py     # Save chat history"
echo "   pip install <package>           # Install new package"
echo "   pip freeze > requirements.txt   # Update dependencies"
echo ""
echo "💡 To deactivate: type 'deactivate'"
echo "=================================================="
