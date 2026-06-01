#!/bin/bash
# Context-Collapse Startup Script

echo "🚀 Context-Collapse - Smart Tech News Synthesizer"
echo "================================================"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Check if Node is available
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is required but not installed."
    exit 1
fi

# Backend setup
echo ""
echo "📦 Setting up backend..."
cd backend

if [ ! -d "venv" ]; then
    echo "  Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate
pip install -q -r requirements.txt

echo "  ✅ Backend dependencies installed"

# Frontend setup
echo ""
echo "📦 Setting up frontend..."
cd ../frontend

if [ ! -d "node_modules" ]; then
    echo "  Installing npm packages..."
    npm install
fi

echo "  ✅ Frontend dependencies installed"

echo ""
echo "🎯 Starting services..."
echo ""

# Start backend in background
cd ../backend
echo "  🔥 Flask API starting on http://localhost:5001"
python app.py &
BACKEND_PID=$!

# Start frontend
cd ../frontend
echo "  ⚡ React dev server starting on http://localhost:5173"
echo ""
npm run dev &
FRONTEND_PID=$!

echo "✨ Both services are running!"
echo "   Frontend: http://localhost:5173"
echo "   Backend:  http://localhost:5001"
echo ""
echo "Press Ctrl+C to stop both services"

# Wait for interrupt
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait
