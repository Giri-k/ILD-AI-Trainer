#!/bin/bash
# ILD Diagnostic Trainer - Start Script
# Starts both backend (FastAPI) and frontend (React) servers

set -e

echo "================================================"
echo "  ILD Diagnostic Trainer - Starting Application  "
echo "================================================"

# Check for .env file
if [ ! -f backend/.env ]; then
    echo ""
    echo "ERROR: backend/.env file not found!"
    echo "Run: cp backend/.env.example backend/.env"
    echo "Then add your OpenAI API key."
    exit 1
fi

# Check for OpenAI key
if grep -q "sk-your-openai-api-key-here" backend/.env 2>/dev/null; then
    echo ""
    echo "WARNING: Please set your real OpenAI API key in backend/.env"
    echo ""
fi

# Start backend
echo ""
echo "[1/2] Starting Backend (FastAPI) on port 8000..."
cd backend
if [ ! -d "venv" ]; then
    echo "  Creating virtual environment..."
    python3 -m venv venv
fi
source venv/bin/activate
pip install -q -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd ..

# Start frontend
echo "[2/2] Starting Frontend (React) on port 3000..."
cd frontend
if [ ! -d "node_modules" ]; then
    echo "  Installing npm dependencies..."
    npm install --silent
fi
npm start &
FRONTEND_PID=$!
cd ..

echo ""
echo "================================================"
echo "  Application Running!"
echo "  Frontend:  http://localhost:3000"
echo "  Backend:   http://localhost:8000"
echo "  API Docs:  http://localhost:8000/docs"
echo "================================================"
echo ""
echo "Press Ctrl+C to stop both servers"

# Cleanup on exit
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM
wait
