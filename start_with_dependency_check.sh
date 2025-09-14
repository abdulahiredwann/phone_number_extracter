#!/bin/bash
# Startup script that runs dependency check before starting the application

echo "🚀 Starting Video Phone Number Extraction Service"
echo "=================================================="

# Run dependency check (we're already in /app/phone from Dockerfile)
echo "🔍 Running dependency check..."
python /app/check_dependencies.py
check_result=$?

# Check if it's just camera warnings (expected in Docker) or real errors
if [ $check_result -eq 0 ]; then
    echo "✅ All dependencies verified successfully!"
elif [ $check_result -eq 1 ]; then
    # Check if it's just camera-related warnings
    if python /app/check_dependencies.py 2>&1 | grep -q "camera not available"; then
        echo "✅ Dependencies verified (camera warnings are expected in Docker)"
    else
        echo "❌ Dependency check failed! Please check the errors above."
        echo "🛑 Exiting..."
        exit 1
    fi
else
    echo "❌ Dependency check failed! Please check the errors above."
    echo "🛑 Exiting..."
    exit 1
fi

echo "🚀 Starting Django application..."

# Run database migrations
echo "📊 Running database migrations..."
python manage.py migrate

# Start the application
echo "🌐 Starting server on port 8000..."
python -m daphne -b 0.0.0.0 -p 8000 phone.asgi:application
