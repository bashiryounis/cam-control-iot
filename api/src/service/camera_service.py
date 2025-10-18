import asyncio
import logging
from typing import Dict, List, Optional
from src.service.onvif_service import ONVIFService
from src.service.stream_service import StreamService
from urllib.parse import quote

logger = logging.getLogger(__name__)

class CameraService:
    """Main service that coordinates ONVIF control and video streaming."""

    def __init__(self):
        self.onvif_service = ONVIFService()
        self.stream_service = StreamService()
        self.cameras: Dict[str, dict] = {}

    async def add_camera(self, camera_id: str, ip: str, port: int, username: str, password: str) -> Optional[dict]:
        info = await self.onvif_service.connect_camera(camera_id, ip, port, username, password)
        if not info:
            return None  # failed

        self.cameras[camera_id] = {
            'ip': ip,
            'port': port,
            'username': username,
            'password': password,
            'is_streaming': False
        }
        logger.info(f"✅ Camera {camera_id} added")
        return self.cameras[camera_id]


    def _build_stream_uri(self, camera_id: str) -> Optional[str]:
        """Build RTSP URI manually if not provided by ONVIF."""
        camera = self.cameras.get(camera_id)
        if not camera:
            return None

        username = quote(camera['username'])
        password = quote(camera['password'])
        ip = camera['ip']

        rtsp_uri = f"rtsp://{username}:{password}@{ip}:554/Streaming/Channels/101"
        return rtsp_uri
    
    async def start_streaming(self, camera_id: str) -> bool:
        """Start video streaming for a camera."""
        camera = self.cameras.get(camera_id)
        if not camera:
            logger.error(f"Camera {camera_id} not found.")
            return False

        stream_uri = self._build_stream_uri(camera_id)
        success = await self.stream_service.start_stream(camera_id, stream_uri)
        if success:
            camera['is_streaming'] = True
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
