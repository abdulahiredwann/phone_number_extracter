#!/bin/bash

# Video Processing Server Startup Script
echo "🚀 Starting Video Processing Server..."

# Navigate to project directory
cd phone

# Activate virtual environment
source ../venv/bin/activate

# Kill any existing daphne processes
echo "🔄 Stopping any existing servers..."
pkill -f daphne 2>/dev/null || true

# Wait a moment for processes to stop
sleep 2

# Start the server
echo "🚀 Starting Daphne ASGI server..."
python -m daphne -b 0.0.0.0 -p 8000 phone.asgi:application
