import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import VideoProcessingTask


class VideoProcessingConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.task_id = self.scope['url_route']['kwargs']['task_id']
        self.task_group_name = f'video_task_{self.task_id}'
        
        # Join task group
        await self.channel_layer.group_add(
            self.task_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send initial status
        task = await self.get_task()
        if task:
            await self.send(text_data=json.dumps({
                'type': 'task_status',
                'task_id': str(task.id),
                'status': task.status,
                'progress': task.progress,
                'current_frame': task.current_frame,
                'total_frames': task.total_frames,
                'message': task.current_message
            }))
    
    async def disconnect(self, close_code):
        # Leave task group
        await self.channel_layer.group_discard(
            self.task_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type')
        
        if message_type == 'get_status':
            task = await self.get_task()
            if task:
                await self.send(text_data=json.dumps({
                    'type': 'task_status',
                    'task_id': str(task.id),
                    'status': task.status,
                    'progress': task.progress,
                    'current_frame': task.current_frame,
                    'total_frames': task.total_frames,
                    'message': task.current_message
                }))
    
    # Receive message from task group
    async def progress_update(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'progress_update',
            'task_id': event['task_id'],
            'progress': event['progress'],
            'current_frame': event['current_frame'],
            'total_frames': event['total_frames'],
            'message': event['message'],
            'status': event['status']
        }))
    
    # Receive message from task group
    async def task_completed(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'task_completed',
            'task_id': event['task_id'],
            'status': event['status'],
            'progress': 100,
            'message': event['message'],
            'phone_numbers_count': event.get('phone_numbers_count', 0)
        }))
    
    # Receive message from task group
    async def task_failed(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'task_failed',
            'task_id': event['task_id'],
            'status': event['status'],
            'error_message': event['error_message']
        }))
    
    @database_sync_to_async
    def get_task(self):
        try:
            return VideoProcessingTask.objects.get(id=self.task_id)
        except VideoProcessingTask.DoesNotExist:
            return None
