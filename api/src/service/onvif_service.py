from onvif import ONVIFCamera
from typing import Dict, Optional, Tuple
import asyncio
import logging

logger = logging.getLogger(__name__)

class ONVIFService:
    """Handles ONVIF protocol communication and PTZ operations."""
    
    def __init__(self):
        self.cameras: Dict[str, ONVIFCamera] = {}
        self.camera_configs: Dict[str, dict] = {}
    
    async def connect_camera(
        self, 
        camera_id: str, 
        ip: str, 
        port: int, 
        username: str, 
        password: str, 
        wsdl_path: str = '/etc/onvif/wsdl/'
    ) -> bool:
        """Connect to an ONVIF camera and initialize services."""
        try:
            # Create ONVIF camera instance
            camera = ONVIFCamera(ip, port, username, password, wsdl_path)
            
            # Test connection by getting device info
            device_info = await asyncio.get_event_loop().run_in_executor(
                None, camera.devicemgmt.GetDeviceInformation
            )
            
            # Initialize PTZ service
            ptz_service = camera.create_ptz_service()
            media_service = camera.create_media_service()
            
            # Get profiles for streaming and PTZ control
            profiles = await asyncio.get_event_loop().run_in_executor(
                None, media_service.GetProfiles
            )
            
            # Store camera and configuration
            self.cameras[camera_id] = camera
            self.camera_configs[camera_id] = {
                'ip': ip,
                'port': port,
                'username': username,
                'device_info': device_info,
                'profiles': profiles,
                'ptz_service': ptz_service,
                'media_service': media_service
            }
            
            logger.info(f"Successfully connected to camera {camera_id} at {ip}:{port}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to camera {camera_id}: {e}")
            return False
    
    def get_camera(self, camera_id: str) -> Optional[ONVIFCamera]:
        """Get ONVIF camera instance."""
        return self.cameras.get(camera_id)
    
    def get_camera_config(self, camera_id: str) -> Optional[dict]:
        """Get camera configuration and services."""
        return self.camera_configs.get(camera_id)
    
    async def move_continuous(self, camera_id: str, pan: float, tilt: float, zoom: float = 0) -> bool:
        """Start continuous PTZ movement."""
        try:
            config = self.camera_configs.get(camera_id)
            if not config:
                return False
            
            ptz_service = config['ptz_service']
            profile_token = config['profiles'][0].token
            
            # Create movement request
            velocity = {
                'PanTilt': {'x': pan, 'y': tilt},
                'Zoom': {'x': zoom}
            }
            
            await asyncio.get_event_loop().run_in_executor(
                None, 
                ptz_service.ContinuousMove,
                {'ProfileToken': profile_token, 'Velocity': velocity}
            )
            return True
            
        except Exception as e:
            logger.error(f"PTZ move failed for camera {camera_id}: {e}")
            return False
    
    async def stop_movement(self, camera_id: str) -> bool:
        """Stop PTZ movement."""
        try:
            config = self.camera_configs.get(camera_id)
            if not config:
                return False
            
            ptz_service = config['ptz_service']
            profile_token = config['profiles'][0].token
            
            await asyncio.get_event_loop().run_in_executor(
                None,
                ptz_service.Stop,
                {'ProfileToken': profile_token, 'PanTilt': True, 'Zoom': True}
            )
            return True
            
        except Exception as e:
            logger.error(f"PTZ stop failed for camera {camera_id}: {e}")
            return False
    
    def get_stream_uri(self, camera_id: str) -> Optional[str]:
        """Get RTSP stream URI for the camera."""
        try:
            config = self.camera_configs.get(camera_id)
            if not config:
                return None
            
            media_service = config['media_service']
            profile_token = config['profiles'][0].token
            
            # Get stream URI
            stream_setup = {'Stream': 'RTP-Unicast', 'Protocol': 'RTSP'}
            uri_response = media_service.GetStreamUri({
                'StreamSetup': stream_setup,
                'ProfileToken': profile_token
            })
            
            return uri_response.Uri
            
        except Exception as e:
            logger.error(f"Failed to get stream URI for camera {camera_id}: {e}")
            return None