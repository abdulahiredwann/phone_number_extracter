#!/usr/bin/env python3
"""
System Dependency Checker for Video Phone Number Extraction
This script checks if all required system dependencies are installed.
"""

import subprocess
import sys
import os
import platform

def run_command(command, shell=True):
    """Run a command and return success status"""
    try:
        result = subprocess.run(command, shell=shell, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def check_tesseract():
    """Check if Tesseract OCR is installed"""
    print("🔍 Checking Tesseract OCR...")
    
    # Try different tesseract commands
    commands = ['tesseract --version', 'tesseract-ocr --version', 'tesseract.exe --version']
    
    for cmd in commands:
        success, stdout, stderr = run_command(cmd)
        if success:
            print(f"✅ Tesseract found: {stdout.split()[1] if stdout else 'Unknown version'}")
            return True
    
    print("❌ Tesseract OCR not found!")
    print("   Install instructions:")
    if platform.system() == "Windows":
        print("   - Download from: https://github.com/UB-Mannheim/tesseract/wiki")
        print("   - Or use: choco install tesseract")
    elif platform.system() == "Darwin":  # macOS
        print("   - brew install tesseract")
    else:  # Linux
        print("   - sudo apt-get install tesseract-ocr")
        print("   - sudo yum install tesseract")
    
    return False

def check_ffmpeg():
    """Check if FFmpeg is installed"""
    print("\n🔍 Checking FFmpeg...")
    
    success, stdout, stderr = run_command('ffmpeg -version')
    if success:
        version_line = stdout.split('\n')[0]
        print(f"✅ FFmpeg found: {version_line}")
        return True
    
    print("❌ FFmpeg not found!")
    print("   Install instructions:")
    if platform.system() == "Windows":
        print("   - Download from: https://ffmpeg.org/download.html")
        print("   - Or use: choco install ffmpeg")
    elif platform.system() == "Darwin":  # macOS
        print("   - brew install ffmpeg")
    else:  # Linux
        print("   - sudo apt-get install ffmpeg")
        print("   - sudo yum install ffmpeg")
    
    return False

def check_opencv_dependencies():
    """Check OpenCV system dependencies"""
    print("\n🔍 Checking OpenCV system dependencies...")
    
    try:
        import cv2
        print("✅ OpenCV Python package found")
        
        # Test video capture
        cap = cv2.VideoCapture(0)  # Try to open default camera
        if cap.isOpened():
            print("✅ OpenCV video capture working")
            cap.release()
            return True
        else:
            print("⚠️  OpenCV video capture not working (may need codec support)")
            return False
    except ImportError as e:
        print(f"❌ OpenCV Python package not found: {e}")
        return False
    except Exception as e:
        print(f"⚠️  OpenCV issue: {e}")
        return False

def check_python_packages():
    """Check required Python packages"""
    print("\n🔍 Checking Python packages...")
    
    required_packages = [
        'cv2', 'pytesseract', 'phonenumbers', 'pandas', 
        'PIL', 'numpy', 'django', 'channels'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'cv2':
                import cv2
            elif package == 'PIL':
                from PIL import Image
            else:
                __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package}")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n❌ Missing packages: {', '.join(missing_packages)}")
        print("   Install with: pip install -r requirements.txt")
        return False
    
    return True

def check_tesseract_path():
    """Check if pytesseract can find tesseract executable"""
    print("\n🔍 Checking pytesseract configuration...")
    
    try:
        import pytesseract
        
        # Try to get tesseract version
        version = pytesseract.get_tesseract_version()
        print(f"✅ pytesseract can access tesseract: {version}")
        return True
    except Exception as e:
        print(f"❌ pytesseract cannot access tesseract: {e}")
        print("   This usually means tesseract is not in PATH or pytesseract.pytesseract.tesseract_cmd needs to be set")
        return False

def main():
    """Main dependency checker"""
    print("🚀 Video Phone Number Extraction - Dependency Checker")
    print("=" * 60)
    
    checks = [
        ("Tesseract OCR", check_tesseract),
        ("FFmpeg", check_ffmpeg),
        ("OpenCV Dependencies", check_opencv_dependencies),
        ("Python Packages", check_python_packages),
        ("pytesseract Configuration", check_tesseract_path),
    ]
    
    results = []
    
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ Error checking {name}: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 60)
    print("📋 SUMMARY:")
    
    all_passed = True
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {name}: {status}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n🎉 All dependencies are properly installed!")
        print("   Your video processor should work correctly.")
    else:
        print("\n⚠️  Some dependencies are missing or misconfigured.")
        print("   Please install the missing dependencies above.")
        print("   The video processor will likely return 0 results without these.")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
