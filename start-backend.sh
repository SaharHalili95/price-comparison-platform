#!/bin/bash

# Smart Price Comparison Platform - Backend Startup Script

echo "🚀 Starting Smart Price Comparison Platform - Backend"
echo "================================================"

# Navigate to backend directory
cd "$(dirname "$0")/backend"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from .env.example..."
    cp .env.example .env
fi

# Install dependencies
echo "📦 Installing dependencies..."
pip install -q -r requirements.txt

# Start the server
echo ""
echo "✅ Backend setup complete!"
echo "🌐 Starting FastAPI server..."
echo "   API: http://localhost:8001"
echo "   Docs: http://localhost:8001/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

uvicorn app.main:app --reload --port 8001
