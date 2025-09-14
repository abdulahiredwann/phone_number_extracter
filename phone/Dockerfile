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

# Copy and install Python deps (your requirements.txt is perfect)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Media dirs
RUN mkdir -p media/videos media/results

# Permissions (optional: ensures Django can write)
RUN chmod -R 755 media

EXPOSE 8000

CMD ["python", "-m", "daphne", "-b", "0.0.0.0", "-p", "8000", "phone.asgi:application"]