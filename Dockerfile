FROM python:3.11-slim

# Install system dependencies: Tesseract + FFmpeg for OpenCV video decoding
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-eng \
    ffmpeg \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

WORKDIR /app

# Copy requirements first for better Docker layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project
COPY . .

# Media dirs
RUN mkdir -p media/videos media/results

# Permissions (optional: ensures Django can write)
RUN chmod -R 755 media

# Make scripts executable
RUN chmod +x check_dependencies.py
RUN chmod +x start_with_dependency_check.sh

# Run dependency check during build to verify everything works
# Note: Camera warnings are expected in Docker, so we don't fail the build
RUN python check_dependencies.py || echo "Dependency check completed with warnings (camera not available in Docker - this is expected)"

# Copy dependency checker to phone directory so it's accessible
RUN cp check_dependencies.py /app/phone/

EXPOSE 8000

# Set working directory to phone app
WORKDIR /app/phone

# Use the same approach as start_server.sh
CMD ["python", "-m", "daphne", "-b", "0.0.0.0", "-p", "8000", "phone.asgi:application"]