# Video Phone Number Extraction - Dependency Installation Guide

## 🚨 Critical Issue: Missing System Dependencies

Your video processor works on your PC but returns 0 results on other PCs because **system dependencies** are missing. Python packages alone are not enough!

## 🔍 Quick Diagnosis

Run this command to check what's missing:

```bash
python check_dependencies.py
```

## 📋 Required System Dependencies

### 1. **Tesseract OCR Engine** (MOST CRITICAL)

- **What it is**: The actual OCR engine that reads text from images
- **Why it's needed**: `pytesseract` is just a Python wrapper
- **What happens without it**: OCR returns empty results → 0 phone numbers found

### 2. **FFmpeg** (For Video Processing)

- **What it is**: Video codec library for reading video files
- **Why it's needed**: OpenCV needs it to decode video formats
- **What happens without it**: Video files can't be opened

### 3. **OpenCV System Libraries**

- **What it is**: Computer vision system libraries
- **Why it's needed**: Video processing and image manipulation
- **What happens without it**: Video processing fails

## 🛠️ Installation Instructions

### Option 1: Automated Installation (Recommended)

```bash
# Make the script executable and run it
chmod +x install_dependencies.sh
./install_dependencies.sh
```

### Option 2: Manual Installation

#### Ubuntu/Debian:

```bash
sudo apt-get update
sudo apt-get install -y tesseract-ocr tesseract-ocr-eng ffmpeg libopencv-dev python3-opencv libavcodec-extra
pip install -r requirements.txt
```

#### CentOS/RHEL:

```bash
sudo yum install -y tesseract tesseract-langpack-eng ffmpeg ffmpeg-devel opencv opencv-devel
pip install -r requirements.txt
```

#### macOS:

```bash
brew install tesseract ffmpeg opencv
pip install -r requirements.txt
```

#### Windows:

1. **Tesseract OCR**: Download from https://github.com/UB-Mannheim/tesseract/wiki
2. **FFmpeg**: Download from https://ffmpeg.org/download.html
3. **Add to PATH**: Make sure both are in your system PATH
4. **Python packages**: `pip install -r requirements.txt`

### Option 3: Docker (Guaranteed to work)

```bash
# Build the Docker image (includes all dependencies)
docker build -t video-processor .

# Run the container
docker run -p 8000:8000 video-processor
```

## 🔧 Troubleshooting

### Problem: "Tesseract not found" error

**Solution**: Install tesseract-ocr system package

```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr

# macOS
brew install tesseract

# Windows: Download and install from official website
```

### Problem: Video files can't be opened

**Solution**: Install FFmpeg

```bash
# Ubuntu/Debian
sudo apt-get install ffmpeg

# macOS
brew install ffmpeg

# Windows: Download and install from official website
```

### Problem: OpenCV import errors

**Solution**: Install OpenCV system libraries

```bash
# Ubuntu/Debian
sudo apt-get install libopencv-dev python3-opencv

# macOS
brew install opencv

# Windows: Usually handled by pip install opencv-python
```

### Problem: pytesseract can't find tesseract

**Solution**: Set the tesseract path in your code

```python
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Windows
# or
pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'  # Linux
```

## ✅ Verification

After installation, run the dependency checker:

```bash
python check_dependencies.py
```

You should see:

```
✅ Tesseract found: 5.0.0
✅ FFmpeg found: 4.4.0
✅ OpenCV Python package found
✅ OpenCV video capture working
✅ All Python packages found
✅ pytesseract can access tesseract: 5.0.0

🎉 All dependencies are properly installed!
```

## 📦 Updated Requirements

The `requirements.txt` file has been updated with additional packages:

- `opencv-contrib-python==4.8.1.78` - Extended OpenCV functionality
- `ffmpeg-python==0.2.0` - Python FFmpeg wrapper
- `psutil==5.9.6` - System monitoring (for dependency checking)

## 🚀 Quick Start

1. **Install system dependencies** (see instructions above)
2. **Install Python packages**: `pip install -r requirements.txt`
3. **Verify installation**: `python check_dependencies.py`
4. **Run your application**: `python manage.py runserver`

## 💡 Why This Happens

- **Your PC**: Has all system dependencies installed (probably from other projects)
- **Other PCs**: Only have Python packages, missing system libraries
- **Result**: Python code runs but libraries can't access system tools → 0 results

The key insight is that some Python packages are just wrappers around system tools, and those system tools must be installed separately!
