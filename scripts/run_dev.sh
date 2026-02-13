#!/bin/bash

# TrustHire Development Server
# Quick start script for development

echo "🚀 Starting TrustHire development server..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -q -r requirements.txt

# Check for .env file
if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found. Copying from .env.example..."
    cp .env.example .env
    echo "✏️  Please edit .env and add your ANTHROPIC_API_KEY"
    exit 1
fi

# Run server
echo "✅ Starting server on http://localhost:8000"
echo "📚 API docs will be available at http://localhost:8000/api/v1/docs"
echo ""

uvicorn main:app --reload --host 0.0.0.0 --port 8000
