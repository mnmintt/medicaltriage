#!/bin/bash
# TriageAI — Start Script
# Mirrors FinSight's simple start pattern

set -e

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║     TriageAI — Groq Swarm Edition      ║"
echo "║  Architecture: Mirrored from FinSight    ║"
echo "╚══════════════════════════════════════════╝"
echo ""

# Check for API key
if [ -z "$GROQ_API_KEY" ]; then
  if [ -f backend/.env ]; then
    echo "[INFO] Loading GROQ_API_KEY from backend/.env"
    export $(grep GROQ_API_KEY backend/.env | xargs)
  else
    echo "[ERROR] GROQ_API_KEY not set."
    echo "  Option 1: export GROQ_API_KEY=gsk_..."
    echo "  Option 2: create backend/.env with GROQ_API_KEY=gsk_..."
    exit 1
  fi
fi

echo "[OK] GROQ_API_KEY detected"

# Install backend deps
echo ""
echo "[BACKEND] Installing Python dependencies..."
cd backend
pip install -r requirements.txt -q
cd ..

# Install frontend deps
echo "[FRONTEND] Installing Node dependencies..."
cd frontend
npm install --silent
cd ..

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "[STARTING] Flask backend on http://localhost:8080"
echo "[STARTING] Vite frontend on http://localhost:5173"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Start backend in background
cd backend
FLASK_ENV=development python server.py &
BACKEND_PID=$!
cd ..

sleep 2

# Start frontend
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "✅ Both services running!"
echo "   Frontend: http://localhost:5173"
echo "   Backend:  http://localhost:8080"
echo "   Health:   http://localhost:8080/api/health"
echo "   Demo:     http://localhost:8080/api/demo"
echo ""
echo "Press Ctrl+C to stop both services."
echo ""

# Wait and clean up on exit
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; echo 'Stopped.'" EXIT
wait
