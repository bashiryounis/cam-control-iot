from src.service.onvif_service import ONVIFService
from src.service.stream_service import StreamService
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class CameraService:
    """Main service that coordinates ONVIF control and video streaming."""
    
    def __init__(self):
        self.onvif_service = ONVIFService()
        self.stream_service = StreamService()
        self.cameras: Dict[str, dict] = {}
    
    async def add_camera(
        self, 
        camera_id: str, 
        ip: str, 
        port: int, 
        username: str, 
        password: str
    ) -> bool:
        """Add a new camera to the system."""
        try:
            # Connect via ONVIF
            success = await self.onvif_service.connect_camera(
                camera_id, ip, port, username, password
            )
            
            if not success:
                return False
            
            # Get stream URI
            stream_uri = self.onvif_service.get_stream_uri(camera_id)
            if not stream_uri:
                logger.warning(f"No stream URI for camera {camera_id}")
            
            # Store camera info
            self.cameras[camera_id] = {
                'ip': ip,
                'port': port,
                'username': username,
                'stream_uri': stream_uri,
                'is_streaming': False
            }
            
            logger.info(f"Successfully added camera {camera_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add camera {camera_id}: {e}")
            return False
    
    async def remove_camera(self, camera_id: str) -> bool:
        """Remove a camera from the system."""
        try:
            # Stop streaming if active
            if self.cameras.get(camera_id, {}).get('is_streaming'):
                await self.stop_streaming(camera_id)
            
            # Remove from services
            if camera_id in self.cameras:
                del self.cameras[camera_id]
            
            logger.info(f"Removed camera {camera_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to remove camera {camera_id}: {e}")
            return False
    
    async def start_streaming(self, camera_id: str) -> bool:
        """Start video streaming for a camera."""
        camera_info = self.cameras.get(camera_id)
        if not camera_info or not camera_info.get('stream_uri'):
            return False
        
        success = await self.stream_service.start_stream(
            camera_id, camera_info['stream_uri']
        )
        
        if success:
            self.cameras[camera_id]['is_streaming'] = True
        
        return success
    
    async def stop_streaming(self, camera_id: str) -> bool:
        """Stop video streaming for a camera."""
        success = await self.stream_service.stop_stream(camera_id)
        
        if success and camera_id in self.cameras:
            self.cameras[camera_id]['is_streaming'] = False
        
        return success
    
    async def move_camera(self, camera_id: str, pan: float, tilt: float, zoom: float = 0) -> bool:
        """Move camera using PTZ controls."""
        return await self.onvif_service.move_continuous(camera_id, pan, tilt, zoom)
    
    async def stop_camera_movement(self, camera_id: str) -> bool:
        """Stop camera PTZ movement."""
        return await self.onvif_service.stop_movement(camera_id)
    
    async def get_frame(self, camera_id: str) -> Optional[str]:
        """Get current frame from camera."""
        return await self.stream_service.get_frame(camera_id)
    
    def list_cameras(self) -> List[dict]:
        """Get list of all cameras."""
        return [
            {
                'camera_id': camera_id,
                'ip': info['ip'],
                'port': info['port'],
                'is_streaming': info['is_streaming']
            }
            for camera_id, info in self.cameras.items()
        ]

