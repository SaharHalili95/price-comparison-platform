#!/bin/bash

# Smart Price Comparison Platform - Frontend Startup Script

echo "🚀 Starting Smart Price Comparison Platform - Frontend"
echo "================================================"

# Navigate to frontend directory
cd "$(dirname "$0")/frontend"

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
else
    echo "✅ Dependencies already installed"
fi

# Start the development server
echo ""
echo "✅ Frontend setup complete!"
echo "🌐 Starting Vite development server..."
echo "   Frontend: http://localhost:5173"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

npm run dev
