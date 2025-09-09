from django.db import models
from django.utils import timezone
import uuid


class VideoProcessingTask(models.Model):
    """Model to track video processing tasks"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    video_file = models.FileField(upload_to='videos/')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True, null=True)
    
    # Processing parameters
    region = models.CharField(max_length=5, default='IL', help_text='Country code for phone number parsing')
    sample_fps = models.IntegerField(default=4, help_text='Frames per second to analyze')
    min_confidence = models.IntegerField(default=55, help_text='Minimum OCR confidence (0-100)')
    
    # Progress tracking
    progress = models.IntegerField(default=0, help_text='Processing progress percentage (0-100)')
    current_frame = models.IntegerField(default=0, help_text='Current frame being processed')
    total_frames = models.IntegerField(default=0, help_text='Total frames to process')
    current_message = models.TextField(blank=True, help_text='Current processing message')
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Task {self.id} - {self.status}"


class PhoneNumberResult(models.Model):
    """Model to store extracted phone numbers"""
    
    task = models.ForeignKey(VideoProcessingTask, on_delete=models.CASCADE, related_name='phone_numbers')
    e164_number = models.CharField(max_length=20, help_text='Phone number in E164 format')
    national_number = models.CharField(max_length=30, help_text='Phone number in national format')
    first_seen_seconds = models.FloatField(help_text='Time in video when first seen')
    frame_count = models.IntegerField(help_text='Number of frames where this number appeared')
    raw_text_examples = models.TextField(help_text='Examples of raw text where number was found')
    
    class Meta:
        ordering = ['first_seen_seconds', 'e164_number']
        unique_together = ['task', 'e164_number']
    
    def __str__(self):
        return f"{self.e164_number} (Task: {self.task.id})"
