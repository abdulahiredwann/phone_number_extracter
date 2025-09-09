from ninja import NinjaAPI, File, Form
from ninja.files import UploadedFile
from ninja.errors import HttpError
from django.http import JsonResponse
from django.conf import settings
from django.utils import timezone
import threading
from .models import VideoProcessingTask, PhoneNumberResult
from .video_processor import VideoProcessor
from typing import List, Optional
import uuid
import os


api = NinjaAPI(title="Video Phone Number Extraction API", version="1.0.0")


def start_video_processing(task_id: str):
    """Start video processing in a background thread"""
    def process_video():
        try:
            print(f"🚀 Starting background processing for task {task_id}")
            processor = VideoProcessor(task_id)
            processor.process_video()
        except Exception as e:
            print(f"❌ Error in background processing: {str(e)}")
            # Update task status to failed
            try:
                task = VideoProcessingTask.objects.get(id=task_id)
                task.status = 'failed'
                task.error_message = str(e)
                task.completed_at = timezone.now()
                task.save()
            except VideoProcessingTask.DoesNotExist:
                pass
    
    # Start processing in background thread
    thread = threading.Thread(target=process_video)
    thread.daemon = True
    thread.start()


@api.post("/upload-video")
def upload_video(
    request,
    video: UploadedFile = File(...)
):
    """
    Upload a video file for phone number extraction (returns task ID immediately)
    """
    # Validate file type
    if not video.name.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
        raise HttpError(400, "Only video files (mp4, avi, mov, mkv) are allowed")
    
    # Use default parameters
    region = "IL"
    sample_fps = 4
    min_confidence = 55
    
    # Create task
    task = VideoProcessingTask.objects.create(
        video_file=video,
        region=region,
        sample_fps=sample_fps,
        min_confidence=min_confidence
    )
    
    print(f"\n🚀 Video uploaded successfully - Task {task.id}")
    print(f"📁 Video file: {task.video_file.name}")
    print(f"🌍 Region: {task.region}")
    print(f"🎬 Sample FPS: {task.sample_fps}")
    print(f"🎯 Min Confidence: {task.min_confidence}")
    
    # Update task status to processing
    task.status = 'processing'
    task.started_at = timezone.now()
    task.save()
    
    # Start processing in background thread
    start_video_processing(str(task.id))
    
    return {
        "task_id": str(task.id),
        "status": "processing",
        "message": "Video uploaded successfully. Processing started in background.",
        "websocket_url": f"ws://localhost:8000/ws/task/{task.id}/"
    }


@api.get("/task/{task_id}")
def get_task_status(request, task_id: str):
    """
    Get the status of a video processing task
    """
    try:
        task = VideoProcessingTask.objects.get(id=task_id)
    except VideoProcessingTask.DoesNotExist:
        raise HttpError(404, "Task not found")
    
    return {
        "task_id": str(task.id),
        "status": task.status,
        "progress": task.progress,
        "current_frame": task.current_frame,
        "total_frames": task.total_frames,
        "current_message": task.current_message,
        "created_at": task.created_at.isoformat(),
        "started_at": task.started_at.isoformat() if task.started_at else None,
        "completed_at": task.completed_at.isoformat() if task.completed_at else None,
        "error_message": task.error_message,
        "video_file": task.video_file.name if task.video_file else None
    }


@api.get("/task/{task_id}/results")
def get_task_results(request, task_id: str):
    """
    Get the extracted phone numbers for a completed task
    """
    try:
        task = VideoProcessingTask.objects.get(id=task_id)
    except VideoProcessingTask.DoesNotExist:
        raise HttpError(404, "Task not found")
    
    if task.status != 'completed':
        raise HttpError(400, f"Task is not completed yet. Current status: {task.status}")
    
    phone_numbers = PhoneNumberResult.objects.filter(task=task)
    
    results = []
    for phone in phone_numbers:
        results.append({
            "e164_number": phone.e164_number,
            "national_number": phone.national_number,
            "first_seen_seconds": phone.first_seen_seconds,
            "frame_count": phone.frame_count,
            "raw_text_examples": phone.raw_text_examples
        })
    
    return {
        "task_id": str(task.id),
        "status": task.status,
        "total_phone_numbers": len(results),
        "phone_numbers": results
    }


@api.get("/tasks")
def list_tasks(request, status: Optional[str] = None, limit: int = 10):
    """
    List all video processing tasks with optional status filter
    """
    tasks = VideoProcessingTask.objects.all()
    
    if status:
        tasks = tasks.filter(status=status)
    
    tasks = tasks[:limit]
    
    results = []
    for task in tasks:
        results.append({
            "task_id": str(task.id),
            "status": task.status,
            "created_at": task.created_at.isoformat(),
            "completed_at": task.completed_at.isoformat() if task.completed_at else None,
            "video_file": task.video_file.name if task.video_file else None
        })
    
    return {
        "tasks": results,
        "total": len(results)
    }


@api.delete("/task/{task_id}")
def delete_task(request, task_id: str):
    """
    Delete a video processing task and its associated files
    """
    try:
        task = VideoProcessingTask.objects.get(id=task_id)
    except VideoProcessingTask.DoesNotExist:
        raise HttpError(404, "Task not found")
    
    # Delete video file if it exists
    if task.video_file and os.path.exists(task.video_file.path):
        os.remove(task.video_file.path)
    
    # Delete task (this will also delete associated phone numbers due to CASCADE)
    task.delete()
    
    return {"message": "Task deleted successfully"}


@api.post("/extract-phone-numbers")
def extract_phone_numbers(
    request,
    video: UploadedFile = File(...)
):
    """
    Extract phone numbers from video without saving to database (quick processing)
    """
    # Validate file type
    if not video.name.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
        raise HttpError(400, "Only video files (mp4, avi, mov, mkv) are allowed")
    
    # Use default parameters
    region = "IL"
    sample_fps = 4
    min_confidence = 55
    
    try:
        print(f"\n🚀 Starting quick video processing")
        print(f"📁 Video file: {video.name}")
        print(f"🌍 Region: {region}")
        print(f"🎬 Sample FPS: {sample_fps}")
        print(f"🎯 Min Confidence: {min_confidence}")
        
        # Save video temporarily
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_file:
            for chunk in video.chunks():
                tmp_file.write(chunk)
            temp_video_path = tmp_file.name
        
        print(f"💾 Video saved temporarily to: {temp_video_path}")
        
        # Process video directly
        import cv2
        import pytesseract
        import phonenumbers
        import pandas as pd
        from phonenumbers import PhoneNumberMatcher, PhoneNumberFormat
        from collections import defaultdict
        
        # Open video
        cap = cv2.VideoCapture(temp_video_path)
        if not cap.isOpened():
            raise RuntimeError(f"Cannot open video: {temp_video_path}")
        
        video_fps = cap.get(cv2.CAP_PROP_FPS) or 25
        frame_interval = max(int(round(video_fps / sample_fps)), 1)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        print(f"🎥 Video info: {video_fps} FPS, {total_frames} total frames")
        print(f"📊 Processing every {frame_interval} frames ({sample_fps} FPS sampling)")
        
        # Results storage
        found = defaultdict(lambda: {"first_time": None, "frames": set(), "raw_hits": set()})
        
        def preprocess_image(img):
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            gray = clahe.apply(gray)
            th = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                       cv2.THRESH_BINARY, 31, 9)
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1,1))
            th = cv2.morphologyEx(th, cv2.MORPH_OPEN, kernel, iterations=1)
            return th
        
        def extract_text_from_image(img):
            config = "--oem 3 --psm 6"
            try:
                data = pytesseract.image_to_data(
                    img, 
                    lang="eng", 
                    config=config, 
                    output_type=pytesseract.Output.DATAFRAME
                )
                if data is None or data.empty:
                    return []
                
                data = data[pd.to_numeric(data["conf"], errors="coerce").fillna(-1) >= min_confidence]
                lines = []
                
                if not data.empty:
                    for (block, par, line), grp in data.groupby(["block_num", "par_num", "line_num"]):
                        txt = " ".join(str(t) for t in grp["text"] if isinstance(t, str))
                        txt = txt.strip()
                        if txt:
                            lines.append(txt)
                return lines
            except Exception as e:
                print(f"OCR Error: {e}")
                return []
        
        def extract_phone_numbers(text, region):
            hits = []
            try:
                for match in PhoneNumberMatcher(text, region):
                    num = match.number
                    if phonenumbers.is_possible_number(num) and phonenumbers.is_valid_number(num):
                        e164 = phonenumbers.format_number(num, PhoneNumberFormat.E164)
                        natl = phonenumbers.format_number(num, PhoneNumberFormat.NATIONAL)
                        hits.append((e164, natl, match.raw_string))
            except Exception as e:
                print(f"Phone number extraction error: {e}")
            return hits
        
        # Process video
        frame_idx = -1
        processed_frames = 0
        print(f"🔄 Starting frame processing...")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            frame_idx += 1
            
            if frame_idx % frame_interval != 0:
                continue
            
            processed_frames += 1
            timestamp_sec = frame_idx / video_fps
            
            # Progress logging every 10 processed frames
            if processed_frames % 10 == 0:
                progress = (frame_idx / total_frames) * 100
                print(f"📈 Progress: {progress:.1f}% - Processing frame {frame_idx}/{total_frames} (Time: {timestamp_sec:.1f}s)")
            
            processed_img = preprocess_image(frame)
            text_lines = extract_text_from_image(processed_img)
            
            if text_lines:
                print(f"📝 Frame {frame_idx}: Found {len(text_lines)} text lines")
                for line in text_lines[:3]:  # Show first 3 lines
                    print(f"   Text: {line[:50]}{'...' if len(line) > 50 else ''}")
            
            joined_text = "\n".join(text_lines)
            texts_to_scan = set(text_lines)
            texts_to_scan.add(joined_text)
            
            frame_phone_count = 0
            for text in texts_to_scan:
                for e164, natl, raw in extract_phone_numbers(text, region):
                    if found[e164]["first_time"] is None:
                        found[e164]["first_time"] = timestamp_sec
                        print(f"📞 NEW PHONE FOUND: {e164} ({natl}) at {timestamp_sec:.1f}s")
                    found[e164]["frames"].add(frame_idx)
                    found[e164]["raw_hits"].add(raw)
                    frame_phone_count += 1
            
            if frame_phone_count > 0:
                print(f"   Found {frame_phone_count} phone numbers in this frame")
        
        cap.release()
        
        print(f"✅ Video processing completed!")
        print(f"📊 Processed {processed_frames} frames out of {total_frames} total frames")
        print(f"📞 Found {len(found)} unique phone numbers")
        
        # Clean up temp file
        import os
        os.unlink(temp_video_path)
        print(f"🗑️ Cleaned up temporary file")
        
        # Format results
        results = []
        for e164, info in found.items():
            results.append({
                "e164_number": e164,
                "national_number": phonenumbers.format_number(
                    phonenumbers.parse(e164, None), 
                    PhoneNumberFormat.NATIONAL
                ),
                "first_seen_seconds": round(info["first_time"], 3) if info["first_time"] is not None else 0,
                "frame_count": len(info["frames"]),
                "raw_text_examples": "; ".join(sorted(info["raw_hits"]))[:500]
            })
        
        # Print summary
        print(f"\n📋 FINAL RESULTS:")
        for i, phone in enumerate(results, 1):
            print(f"   {i}. {phone['e164_number']} ({phone['national_number']})")
            print(f"      First seen: {phone['first_seen_seconds']}s")
            print(f"      Appeared in: {phone['frame_count']} frames")
            print(f"      Examples: {phone['raw_text_examples'][:100]}{'...' if len(phone['raw_text_examples']) > 100 else ''}")
            print()
        
        return {
            "status": "completed",
            "message": "Video processed successfully",
            "total_phone_numbers": len(results),
            "phone_numbers": results
        }
        
    except Exception as e:
        print(f"❌ Error in quick processing: {str(e)}")
        print(f"🔍 Error type: {type(e).__name__}")
        import traceback
        print(f"📍 Traceback: {traceback.format_exc()}")
        raise HttpError(500, f"Video processing failed: {str(e)}")


@api.get("/health")
def health_check(request):
    """
    Health check endpoint
    """
    return {"status": "healthy", "message": "API is running"}
