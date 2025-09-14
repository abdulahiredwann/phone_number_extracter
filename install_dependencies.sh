#!/bin/bash
# Installation script for Video Phone Number Extraction dependencies

echo "🚀 Installing Video Phone Number Extraction Dependencies"
echo "========================================================"

# Detect operating system
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]] || [[ "$OSTYPE" == "win32" ]]; then
    OS="windows"
else
    echo "❌ Unsupported operating system: $OSTYPE"
    exit 1
fi

echo "🖥️  Detected OS: $OS"

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Install system dependencies based on OS
if [[ "$OS" == "linux" ]]; then
    echo "📦 Installing Linux dependencies..."
    
    # Update package list
    if command_exists apt-get; then
        echo "🔄 Updating package list..."
        sudo apt-get update
        
        echo "📥 Installing Tesseract OCR..."
        sudo apt-get install -y tesseract-ocr tesseract-ocr-eng
        
        echo "📥 Installing FFmpeg..."
        sudo apt-get install -y ffmpeg
        
        echo "📥 Installing OpenCV system dependencies..."
        sudo apt-get install -y libopencv-dev python3-opencv
        
        echo "📥 Installing additional codec support..."
        sudo apt-get install -y libavcodec-extra
        
    elif command_exists yum; then
        echo "🔄 Installing with yum..."
        
        echo "📥 Installing Tesseract OCR..."
        sudo yum install -y tesseract tesseract-langpack-eng
        
        echo "📥 Installing FFmpeg..."
        sudo yum install -y ffmpeg ffmpeg-devel
        
        echo "📥 Installing OpenCV system dependencies..."
        sudo yum install -y opencv opencv-devel
        
    else
        echo "❌ Unsupported package manager. Please install manually:"
        echo "   - tesseract-ocr"
        echo "   - ffmpeg"
        echo "   - opencv system libraries"
    fi

elif [[ "$OS" == "macos" ]]; then
    echo "📦 Installing macOS dependencies..."
    
    if command_exists brew; then
        echo "🔄 Installing with Homebrew..."
        
        echo "📥 Installing Tesseract OCR..."
        brew install tesseract
        
        echo "📥 Installing FFmpeg..."
        brew install ffmpeg
        
        echo "📥 Installing OpenCV..."
        brew install opencv
        
    else
        echo "❌ Homebrew not found. Please install Homebrew first:"
        echo "   /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
        exit 1
    fi

elif [[ "$OS" == "windows" ]]; then
    echo "📦 Windows dependencies installation..."
    echo "⚠️  For Windows, please install manually:"
    echo ""
    echo "1. Tesseract OCR:"
    echo "   - Download from: https://github.com/UB-Mannheim/tesseract/wiki"
    echo "   - Or use: choco install tesseract"
    echo ""
    echo "2. FFmpeg:"
    echo "   - Download from: https://ffmpeg.org/download.html"
    echo "   - Or use: choco install ffmpeg"
    echo ""
    echo "3. Make sure both are in your PATH"
    echo ""
    echo "Then run: pip install -r requirements.txt"
    exit 0
fi

# Install Python dependencies
echo ""
echo "🐍 Installing Python dependencies..."

if command_exists python3; then
    echo "📥 Installing from requirements.txt..."
    pip3 install -r requirements.txt
elif command_exists python; then
    echo "📥 Installing from requirements.txt..."
    pip install -r requirements.txt
else
    echo "❌ Python not found. Please install Python 3.7+ first."
    exit 1
fi

# Verify installation
echo ""
echo "🔍 Verifying installation..."
python3 check_dependencies.py

echo ""
echo "✅ Installation complete!"
echo "   If any dependencies are still missing, please install them manually."
