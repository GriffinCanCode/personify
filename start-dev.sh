#!/bin/bash

# Kill any processes on ports 8000 and 3000
./kill-ports.sh
echo ""

echo "Starting Personify Development Environment"
echo "==========================================="

# Check if backend .env exists
if [ ! -f backend/.env ]; then
    echo "❌ backend/.env file not found!"
    echo "Run: cd backend && ./setup-env.sh"
    exit 1
fi

# Start PostgreSQL with Docker (if not running)
if ! docker ps | grep -q personify-postgres; then
    echo "Starting PostgreSQL..."
    docker-compose up -d postgres
    sleep 3
fi

# Start backend in background
echo "Starting backend..."
source backend/venv/bin/activate
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
export CHROMA_TELEMETRY_IMPL="chromadb.telemetry.noop.Noop"
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Start frontend in background
echo "Starting frontend..."
cd frontend || exit
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "==========================================="
echo "✓ Development environment started!"
echo ""
echo "Frontend: http://localhost:3000"
echo "Backend: http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"
echo "==========================================="

# Wait for Ctrl+C
trap "kill $BACKEND_PID $FRONTEND_PID; docker-compose down; exit" INT
wait

