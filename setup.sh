#!/bin/bash
# Deckorator Setup Script
# Downloads and sets up the deck planning system

set -e  # Exit on error

echo "🏗️  DECKORATOR SETUP"
echo "==================="
echo "Setting up AI-powered deck planning system..."
echo

# Check Python installation
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
    echo "✅ Python 3 found: $PYTHON_VERSION"
else
    echo "❌ Python 3 not found!"
    echo "   Please install Python 3.6+ from https://python.org"
    exit 1
fi

# Create project directory
PROJECT_DIR="deckorator-project"
if [ -d "$PROJECT_DIR" ]; then
    echo "📁 Directory '$PROJECT_DIR' already exists"
    read -p "   Overwrite? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "   Cancelled."
        exit 1
    fi
    rm -rf "$PROJECT_DIR"
fi

mkdir -p "$PROJECT_DIR"
cd "$PROJECT_DIR"
echo "📁 Created project directory: $PROJECT_DIR"

# Download main scripts
echo "📥 Downloading deck planner..."
curl -s -L "https://raw.githubusercontent.com/pem725/deckorator/main/deck_planner.py" -o deck_planner.py

echo "📥 Downloading LLM submission helper..."
curl -s -L "https://raw.githubusercontent.com/pem725/deckorator/main/llm_submit.py" -o llm_submit.py

echo "📥 Downloading supplier database..."
curl -s -L "https://raw.githubusercontent.com/pem725/deckorator/main/suppliers_database.json" -o suppliers_database.json

# Make scripts executable
chmod +x deck_planner.py llm_submit.py

echo "✅ Download complete!"
echo
echo "🚀 READY TO START!"
echo "=================="
echo "1. cd $PROJECT_DIR"
echo "2. python3 deck_planner.py"
echo "3. Follow the prompts to generate your custom deck plan"
echo "4. Take photos of your deck area and create sketches"
echo "5. Submit to Claude, ChatGPT, or your favorite AI assistant"
echo
echo "📚 Documentation: https://pem725.github.io/deckorator"
echo "🛠️  Support: https://github.com/pem725/deckorator/issues"
echo
echo "🏗️  Happy deck building!"