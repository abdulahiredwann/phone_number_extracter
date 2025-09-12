FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-eng \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Create media directories
RUN mkdir -p media/videos media/results

# Expose port
EXPOSE 8000

# Start Django development server with Daphne
CMD ["python", "-m", "daphne", "-b", "0.0.0.0", "-p", "8000", "phone.asgi:application"]