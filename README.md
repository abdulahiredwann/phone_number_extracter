# 📞 Video Phone Number Extraction

A powerful web application that extracts phone numbers from video files using advanced OCR technology. Upload a video, and the system will automatically detect and extract all phone numbers found in the video frames.

## ✨ Features

- 🎥 **Video Processing**: Supports MP4, AVI, MOV, MKV formats
- 🔍 **Advanced OCR**: Uses Tesseract OCR with image preprocessing
- 📱 **Phone Number Detection**: Specifically optimized for Israeli phone numbers
- 🌐 **Web Interface**: Clean React frontend with real-time progress
- ⚡ **Real-time Updates**: WebSocket-based progress tracking
- 🐳 **Docker Ready**: Fully containerized for easy deployment
- 💾 **SQLite Database**: Persistent storage for processing results

## 🚀 Quick Start with Docker

### Prerequisites

- Docker and Docker Compose installed
- Git (to clone the repository)

### 1. Clone the Repository

### 2. Build and Start the Application

```bash
# Build and start all services
docker compose up --build -d

# Check if services are running
docker compose ps
```

### 3. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/api/docs

### 4. Upload and Process Videos

1. Open your browser and go to http://localhost:3000
2. Click "Upload Video" and select your video file
3. Watch the real-time progress as the system processes your video
4. View the extracted phone numbers when processing is complete

## 🏗️ Project Structure

```
video-phone-extraction/
├── frontend/                 # React frontend application
│   ├── src/
│   │   ├── Pages/
│   │   │   ├── Upload.tsx    # Video upload page
│   │   │   ├── SeeProgress.tsx # Progress tracking page
│   │   │   └── SeeResult.tsx  # Results display page
│   │   └── hooks/
│   │       └── useWebSocket.ts # WebSocket connection
│   └── Dockerfile
├── phone/                    # Django backend application
│   ├── api/
│   │   ├── models.py         # Database models
│   │   ├── views.py          # API endpoints
│   │   ├── video_processor.py # Video processing logic
│   │   └── consumers.py      # WebSocket consumers
│   ├── phone/
│   │   ├── settings.py       # Django settings
│   │   └── asgi.py          # ASGI configuration
│   └── manage.py
├── media/                    # Media storage (created automatically)
│   ├── videos/              # Uploaded video files
│   └── results/             # Processing results
├── requirements.txt          # Python dependencies
├── docker-compose.yml       # Docker services configuration
├── Dockerfile              # Backend Docker configuration
└── README.md
```

## 🗄️ Database

The application uses **SQLite** for data storage:

- **Location**: `phone/db.sqlite3`
- **Persistent**: Data survives container restarts
- **Tables**:
  - `VideoProcessingTask`: Stores video processing jobs
  - `PhoneNumberResult`: Stores extracted phone numbers

### Database Management

```bash
# Access database (if needed)
docker compose exec backend python manage.py dbshell

# Run migrations
docker compose exec backend python manage.py migrate

# Create superuser (for admin access)
docker compose exec backend python manage.py createsuperuser
```

## 🔧 Configuration

### Environment Variables

The application can be configured using environment variables in `docker-compose.yml`:

```yaml
environment:
  - DEBUG=True
  - ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0,frontend
  - DJANGO_SETTINGS_MODULE=phone.settings
```

### Video Processing Settings

Default settings in the code:

- **Region**: Israel (IL)
- **Sample FPS**: 4 frames per second
- **Min Confidence**: 55 (OCR confidence threshold)
- **Image Resize**: Minimum 400px width for better OCR

## 📊 API Endpoints

### Video Processing

- `POST /api/upload-video` - Upload video for processing
- `GET /api/task/{task_id}` - Get task status
- `GET /api/task/{task_id}/results` - Get extracted phone numbers
- `POST /api/extract-phone-numbers` - Quick processing without saving

### Task Management

- `GET /api/tasks` - List all tasks
- `DELETE /api/task/{task_id}` - Delete task and files

### Health Check

- `GET /api/health` - API health status

## 🛠️ Development

### Running Locally (Without Docker)

#### Backend Setup

```bash
# Navigate to phone directory
cd phone

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r ../requirements.txt

# Install system dependencies
sudo apt-get install tesseract-ocr tesseract-ocr-eng ffmpeg

# Run migrations
python manage.py migrate

# Start server
python manage.py runserver
```

#### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### Dependency Check

```bash
# Check if all dependencies are installed
python check_dependencies.py

# Or in Docker
docker compose exec backend python /app/check_dependencies.py
```

## 🐳 Docker Commands

### Basic Commands

```bash
# Start all services
docker compose up -d

# Stop all services
docker compose down

# View logs
docker compose logs -f

# View specific service logs
docker compose logs -f backend
docker compose logs -f frontend

# Restart a service
docker compose restart backend
```

### Development Commands

```bash
# Rebuild and start
docker compose up --build -d

# Build without cache
docker compose build --no-cache

# Execute commands in container
docker compose exec backend bash
docker compose exec frontend bash

# Run specific commands
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py createsuperuser
```

## 📈 Performance

### Video Processing

- **Supported Formats**: MP4, AVI, MOV, MKV
- **Processing Speed**: ~4 FPS sampling (configurable)
- **Memory Usage**: Optimized for container environments
- **Storage**: Videos stored in `media/videos/` directory

### Optimization Tips

- Use smaller video files for faster processing
- Higher resolution videos may take longer but give better results
- The system automatically resizes small frames for better OCR

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with Docker
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

If you encounter any issues:

1. Check the troubleshooting section above
2. View the logs: `docker compose logs`
3. Run dependency check: `python check_dependencies.py`
4. Create an issue in the repository

## 🎯 Usage Example

1. **Start the application**:

   ```bash
   docker compose up --build -d
   ```

2. **Open your browser** and go to http://localhost:3000

3. **Upload a video** containing phone numbers

4. **Watch the progress** as the system processes your video

5. **View results** with all extracted phone numbers, timestamps, and confidence scores

The system will automatically:

- ✅ Extract frames from your video
- ✅ Process images with advanced OCR
- ✅ Detect Israeli phone numbers
- ✅ Provide real-time progress updates
- ✅ Store results in the database
- ✅ Display results in a user-friendly interface

**Ready to extract phone numbers from your videos!** 🚀
