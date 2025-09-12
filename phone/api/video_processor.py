import cv2
import pytesseract
import phonenumbers
import pandas as pd
from phonenumbers import PhoneNumberMatcher, PhoneNumberFormat
from collections import defaultdict
from pathlib import Path
import os
import threading
import time
import asyncio
from django.utils import timezone
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import VideoProcessingTask, PhoneNumberResult
# 

class VideoProcessor:
    """Service class for processing videos and extracting phone numbers"""
    
    def __init__(self, task_id):
        self.task_id = task_id
        self.task = VideoProcessingTask.objects.get(id=task_id)
        self.channel_layer = get_channel_layer()
    

    # Process image for better OCR results
    def preprocess_image(self, img):
        """Preprocess image for better OCR results"""
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # Contrast enhancement
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        gray = clahe.apply(gray)
        # Adaptive thresholding
        th = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   cv2.THRESH_BINARY, 31, 9)
        # Morphological opening to remove noise
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1,1))
        th = cv2.morphologyEx(th, cv2.MORPH_OPEN, kernel, iterations=1)
        # Pass the processed image to the OCR
        return th
    
    def extract_text_from_image(self, img):
        """Extract text from image using OCR - matches the working v.py script exactly"""
        config = "--oem 3 --psm 6"
        data = pytesseract.image_to_data(
            img, 
            lang="eng", 
            config=config, 
            output_type=pytesseract.Output.DATAFRAME
        )
        if data is None or data.empty:
            return []
        
        # Filter by confidence - same as working script
        data = data[pd.to_numeric(data["conf"], errors="coerce").fillna(-1) >= self.task.min_confidence]
        lines = []
        
        if not data.empty:
            for (block, par, line), grp in data.groupby(["block_num", "par_num", "line_num"]):
                txt = " ".join(str(t) for t in grp["text"] if isinstance(t, str))
                txt = txt.strip()
                if txt:
                    lines.append(txt)
        
        return lines
    
    def extract_phone_numbers(self, text, region):
        """Extract phone numbers from text using libphonenumber with improved parsing"""
        hits = []
        
        # First, try direct parsing
        for match in PhoneNumberMatcher(text, region):
            num = match.number
            if phonenumbers.is_possible_number(num) and phonenumbers.is_valid_number(num):
                e164 = phonenumbers.format_number(num, PhoneNumberFormat.E164)
                natl = phonenumbers.format_number(num, PhoneNumberFormat.NATIONAL)
                # Add the raw string to the hits
                hits.append((e164, natl, match.raw_string))
        
        # If no hits, try to fix common OCR issues
        if not hits:
            print(f"🔍 No direct hits for text: '{text}' - trying OCR fixes...")
            
            # Strategy 1: Add country code if missing
            if region == "IL" and not text.startswith("+972"):
                import re
                
                # Try multiple patterns to catch different OCR formats
                patterns = [
                    r'(\d{2})-?B?(\d{2})-?(\d{4})',  # 54-B52-8105
                    r'(\d{2})-(\d{3})-(\d{4})',      # 52-268-8331
                    r'(\d{2})B(\d{2})(\d{4})',       # 54B528105
                    r'(\d{2})(\d{2})(\d{4})',        # 54528105
                ]
                
                for pattern in patterns:
                    matches = re.findall(pattern, text)
                    print(f"🔍 Pattern {pattern} found {len(matches)} matches: {matches}")
                    
                    for match in matches:
                        if len(match) == 3:
                            part1, part2, part3 = match
                            print(f"🔍 Processing match: {part1}, {part2}, {part3}")
                            
                            # Fix OCR errors (B → 8)
                            part2 = part2.replace('B', '8')
                            
                            # Try different combinations
                            candidates = [
                                f"+972{part1}{part2}{part3}",
                                f"+972 {part1}-{part2}-{part3}",
                                f"+972{part1}-{part2}-{part3}",
                                f"+972{part1}{part2}-{part3}",
                                f"+972{part1}-{part2}{part3}",
                                f"0{part1}-{part2}-{part3}",  # Israeli national format
                                f"0{part1}{part2}{part3}"     # Israeli national format no dashes
                            ]
                            
                            validation_failed = True
                            for candidate in candidates:
                                try:
                                    print(f"🔍 Trying candidate: {candidate}")
                                    parsed = phonenumbers.parse(candidate, region)
                                    if phonenumbers.is_possible_number(parsed) and phonenumbers.is_valid_number(parsed):
                                        e164 = phonenumbers.format_number(parsed, PhoneNumberFormat.E164)
                                        natl = phonenumbers.format_number(parsed, PhoneNumberFormat.NATIONAL)
                                        print(f"✅ Valid phone number found: {e164} ({natl})")
                                        hits.append((e164, natl, text))
                                        validation_failed = False
                                        break
                                except Exception as e:
                                    print(f"❌ Failed to parse {candidate}: {e}")
                                    continue
                            
                            # If validation failed but we have a pattern match, use fallback
                            if validation_failed and part1.startswith('5'):
                                e164 = f"+972{part1}{part2}{part3}"
                                natl = f"0{part1}-{part2}-{part3}"
                                print(f"✅ Fallback: Accepting {e164} ({natl}) as Israeli mobile (validation failed but pattern looks valid)")
                                hits.append((e164, natl, text))
                                break
                            
                            if hits:  # If we found a valid number, break out of pattern loop
                                break
                    
                    if hits:  # If we found hits, break out of patterns loop
                        break
            
            # Strategy 2: Fallback - accept numbers that look like Israeli mobile numbers
            if not hits and region == "IL":
                print(f"🔍 No hits with strict validation, trying fallback for: '{text}'")
                import re
                
                # Look for patterns that look like Israeli mobile numbers
                patterns = [
                    r'(\d{2})-?B?(\d{2})-?(\d{4})',  # 54-B52-8105
                    r'(\d{2})-(\d{3})-(\d{4})',      # 52-268-8331
                ]
                
                for pattern in patterns:
                    matches = re.findall(pattern, text)
                    if matches:
                        for match in matches:
                            if len(match) == 3:
                                part1, part2, part3 = match
                                # Fix OCR errors
                                part2 = part2.replace('B', '8')
                                
                                # Create Israeli mobile number
                                if part1.startswith('5'):  # Israeli mobile prefix
                                    e164 = f"+972{part1}{part2}{part3}"
                                    natl = f"0{part1}-{part2}-{part3}"
                                    
                                    # Basic validation - check if it looks like a valid Israeli mobile
                                    if len(part1 + part2 + part3) == 9 and part1.startswith('5'):
                                        print(f"✅ Fallback: Accepting {e164} ({natl}) as Israeli mobile")
                                        hits.append((e164, natl, text))
                                        break
                        if hits:
                            break
        
        return hits
    
    def clean_phone_text(self, text):
        """Clean text for better phone number extraction"""
        # Remove common OCR artifacts
        text = text.replace(')', '').replace('(', '').replace(',', '').replace('.', '')
        text = text.replace(' ', '').replace('-', '')
        return text
    
    def send_progress_update(self, progress, current_frame, total_frames, message):
        """Send progress update via WebSocket"""
        if self.channel_layer:
            async_to_sync(self.channel_layer.group_send)(
                f'video_task_{self.task_id}',
                {
                    'type': 'progress_update',
                    'task_id': str(self.task_id),
                    'progress': progress,
                    'current_frame': current_frame,
                    'total_frames': total_frames,
                    'message': message,
                    'status': 'processing'
                }
            )
    
    def send_task_completed(self, phone_numbers_count):
        """Send task completed notification via WebSocket"""
        if self.channel_layer:
            async_to_sync(self.channel_layer.group_send)(
                f'video_task_{self.task_id}',
                {
                    'type': 'task_completed',
                    'task_id': str(self.task_id),
                    'status': 'completed',
                    'message': f'Processing completed! Found {phone_numbers_count} phone numbers.',
                    'phone_numbers_count': phone_numbers_count
                }
            )
    
    def send_task_failed(self, error_message):
        """Send task failed notification via WebSocket"""
        if self.channel_layer:
            async_to_sync(self.channel_layer.group_send)(
                f'video_task_{self.task_id}',
                {
                    'type': 'task_failed',
                    'task_id': str(self.task_id),
                    'status': 'failed',
                    'error_message': error_message
                }
            )
    
    def update_task_progress(self, progress, current_frame, total_frames, message):
        """Update task progress in database and send WebSocket update"""
        self.task.progress = progress
        self.task.current_frame = current_frame
        self.task.total_frames = total_frames
        self.task.current_message = message
        self.task.save()
        
        # Send WebSocket update
        self.send_progress_update(progress, current_frame, total_frames, message)
    
    def process_video(self):
        """Main video processing function"""
        # 
        try:
            print("Abdu")
            print(f"\n🚀 Starting video processing for task {self.task.id}")
            print(f"📁 Video file: {self.task.video_file.name}")
            print(f"🌍 Region: {self.task.region}")
            print(f"🎬 Sample FPS: {self.task.sample_fps}")
            print(f"🎯 Min Confidence: {self.task.min_confidence}")
            
            # Update task status
            self.task.status = 'processing'
            self.task.started_at = timezone.now()
            self.task.save()
            
            video_path = self.task.video_file.path
            
            # Open video
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                raise RuntimeError(f"Cannot open video: {video_path}")
            
            video_fps = cap.get(cv2.CAP_PROP_FPS) or 25
            frame_interval = max(int(round(video_fps / self.task.sample_fps)), 1)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            print(f"🎥 Video info: {video_fps} FPS, {total_frames} total frames")
            print(f"📊 Processing every {frame_interval} frames ({self.task.sample_fps} FPS sampling)")
            
            # Update task with total frames
            self.update_task_progress(0, 0, total_frames, "Starting video processing...")
            
            # Results storage
            found = defaultdict(lambda: {"first_time": None, "frames": set(), "raw_hits": set()})
            
            frame_idx = -1
            processed_frames = 0
            print(f"🔄 Starting frame processing...")
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                frame_idx += 1
                
                # Sample frames
                if frame_idx % frame_interval != 0:
                    continue
                
                processed_frames += 1
                timestamp_sec = frame_idx / video_fps
                
                # Process frame
                processed_img = self.preprocess_image(frame)
                text_lines = self.extract_text_from_image(processed_img)
                
                # Update progress every 5 processed frames or on first frame
                if processed_frames % 5 == 0 or processed_frames == 1:
                    progress = int((frame_idx / total_frames) * 100)
                    message = f"Processing frame {frame_idx}/{total_frames} (Time: {timestamp_sec:.1f}s)"
                    self.update_task_progress(progress, frame_idx, total_frames, message)
                    print(f"📈 Progress: {progress}% - {message}")
                
                if text_lines:
                    print(f"📝 Frame {frame_idx}: Found {len(text_lines)} text lines")
                    for line in text_lines[:2]:  # Show first 2 lines
                        print(f"   Text: {line[:50]}{'...' if len(line) > 50 else ''}")
                
                # Try both individual lines and joined text
                joined_text = "\n".join(text_lines)
                texts_to_scan = set(text_lines)
                texts_to_scan.add(joined_text)
                
                # Extract phone numbers
                frame_phone_count = 0
                for text in texts_to_scan:
                    hits = self.extract_phone_numbers(text, self.task.region)
                    for e164, natl, raw in hits:
                        if e164 not in found:
                            found[e164] = {
                                "first_time": timestamp_sec,
                                "frames": set(),
                                "raw_hits": set()
                            }
                            print(f"🆕 New phone number found: {e164} ({natl}) at {timestamp_sec:.1f}s")
                        
                        found[e164]["frames"].add(frame_idx)
                        found[e164]["raw_hits"].add(raw)
                        frame_phone_count += 1
                
                if frame_phone_count > 0:
                    print(f"   Found {frame_phone_count} phone numbers in this frame")
            
            cap.release()
            
            print(f"✅ Video processing completed!")
            print(f"📊 Processed {processed_frames} frames out of {total_frames} total frames")
            print(f"📞 Found {len(found)} unique phone numbers")
            
            # Save results to database
            self.save_results(found)
            print(f"💾 Results saved to database")
            
            # Update task status
            self.task.status = 'completed'
            self.task.progress = 100
            self.task.completed_at = timezone.now()
            self.task.save()
            
            # Send completion notification
            self.send_task_completed(len(found))
            
            print(f"🎉 Task {self.task.id} completed successfully!")
            
        except Exception as e:
            print(f"❌ Error processing video: {str(e)}")
            print(f"🔍 Error type: {type(e).__name__}")
            import traceback
            print(f"📍 Traceback: {traceback.format_exc()}")
            
            # Update task status with error
            self.task.status = 'failed'
            self.task.error_message = str(e)
            self.task.completed_at = timezone.now()
            self.task.save()
            
            # Send error notification
            self.send_task_failed(str(e))
    
    def save_results(self, found_numbers):
        """Save extracted phone numbers to database"""
        for e164, info in found_numbers.items():
            PhoneNumberResult.objects.create(
                task=self.task,
                e164_number=e164,
                national_number=phonenumbers.format_number(
                    phonenumbers.parse(e164, None), 
                    PhoneNumberFormat.NATIONAL
                ),
                first_seen_seconds=round(info["first_time"], 3) if info["first_time"] is not None else 0,
                frame_count=len(info["frames"]),
                raw_text_examples="; ".join(sorted(info["raw_hits"]))[:500]
            )


def process_video_async(task_id):
    """Function to process video asynchronously"""
    processor = VideoProcessor(task_id)
    processor.process_video()


def start_video_processing(task_id):
    """Start video processing in a separate thread"""
    thread = threading.Thread(target=process_video_async, args=(task_id,))
    thread.daemon = True
    thread.start()
    return thread
