#!/bin/bash

# NutFlix Frontend Build Script
echo "🥜 Building NutFlix React Frontend..."

# Navigate to frontend directory
cd "$(dirname "$0")"

# Check if Node.js is installed
if ! command -v npm &> /dev/null; then
    echo "❌ Node.js/npm not found. Please install Node.js first:"
    echo "   https://nodejs.org/"
    exit 1
fi

# Install dependencies
echo "📦 Installing dependencies..."
npm install

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

# Build for production
echo "🔨 Building React app..."
npm run build

if [ $? -ne 0 ]; then
    echo "❌ Build failed"
    exit 1
fi

echo "✅ Build complete!"
echo ""
echo "🚀 Your React app is ready!"
echo "   Start Flask backend: python web_service.py"
echo "   Access dashboard: http://localhost:5050"
echo ""
echo "🔧 For development:"
echo "   Start dev server: npm run dev"
echo "   Access dev mode: http://localhost:3000"
