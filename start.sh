#!/bin/bash
echo "Starting Nyaya Sahayaka..."

echo "1. Starting Backend (Legal Agent AI)..."
cd legal-agent-ai
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
cd ..

echo "2. Starting Frontend (Legal Agent Web)..."
cd legal-agent-web
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "✅ Both services are starting up!"
echo "   - Backend: http://localhost:8000"
echo "   - Frontend: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop both servers."

# Wait for Ctrl+C
trap "echo 'Stopping servers...'; kill $BACKEND_PID $FRONTEND_PID; exit" SIGINT SIGTERM
wait $BACKEND_PID $FRONTEND_PID
