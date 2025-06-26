import cv2
import asyncio
import base64
from typing import Dict ,Optional, AsyncGenerator
import logging

logger = logging.getLogger(__name__)

class StreamService:
    """Handles video streaming operations using OpenCV."""
    
    def __init__(self):
        self.active_streams: Dict[str, cv2.VideoCapture] = {}
        self.stream_tasks: Dict[str, asyncio.Task] = {}
    
    async def start_stream(self, camera_id: str, rtsp_url: str) -> bool:
        """Start video streaming for a camera."""
        try:
            if camera_id in self.active_streams:
                await self.stop_stream(camera_id)
            
            # Create video capture
            cap = cv2.VideoCapture(rtsp_url)
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Reduce latency
            
            if not cap.isOpened():
                logger.error(f"Failed to open stream for camera {camera_id}")
                return False
            
            self.active_streams[camera_id] = cap
            logger.info(f"Started stream for camera {camera_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error starting stream for camera {camera_id}: {e}")
            return False
    
    async def stop_stream(self, camera_id: str) -> bool:
        """Stop video streaming for a camera."""
        try:
            if camera_id in self.active_streams:
                cap = self.active_streams[camera_id]
                cap.release()
                del self.active_streams[camera_id]
            
            if camera_id in self.stream_tasks:
                self.stream_tasks[camera_id].cancel()
                del self.stream_tasks[camera_id]
            
            logger.info(f"Stopped stream for camera {camera_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error stopping stream for camera {camera_id}: {e}")
            return False
    
    async def get_frame(self, camera_id: str) -> Optional[str]:
        """Get a single frame as base64 encoded JPEG."""
        try:
            cap = self.active_streams.get(camera_id)
            if not cap:
                return None
            
            ret, frame = cap.read()
            if not ret:
                return None
            
            # Resize frame for web streaming
            frame = cv2.resize(frame, (640, 480))
            
            # Encode as JPEG
            _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
            
            # Convert to base64
            frame_base64 = base64.b64encode(buffer).decode('utf-8')
            return frame_base64
            
        except Exception as e:
            logger.error(f"Error getting frame for camera {camera_id}: {e}")
            return None
    
    async def stream_generator(self, camera_id: str) -> AsyncGenerator[str, None]:
        """Generate continuous frames for WebSocket streaming."""
        while camera_id in self.active_streams:
            frame = await self.get_frame(camera_id)
            if frame:
                yield frame
            await asyncio.sleep(0.033)  # ~30 FPS

