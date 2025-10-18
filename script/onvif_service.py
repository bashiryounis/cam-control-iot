import asyncio
import logging
from onvif import ONVIFCamera
from typing import Dict, Optional
import sys

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("PTZ")

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
    ) -> bool:
        """Connect to an ONVIF camera and initialize services."""
        try:
            camera = ONVIFCamera(ip, port, username, password)
            device_info = await asyncio.get_event_loop().run_in_executor(
                None, camera.devicemgmt.GetDeviceInformation
            )
            ptz_service = camera.create_ptz_service()
            media_service = camera.create_media_service()
            profiles = await asyncio.get_event_loop().run_in_executor(
                None, media_service.GetProfiles
            )
            
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
            logger.info(f"✅ Connected to camera {camera_id} at {ip}:{port}")
            logger.info(f"Device Info: {device_info}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to connect to camera {camera_id}: {e}")
            return False

    async def move_continuous(self, camera_id: str, pan: float, tilt: float, zoom: float = 0) -> bool:
        """Start continuous PTZ movement."""
        try:
            config = self.camera_configs.get(camera_id)
            if not config:
                return False
            ptz_service = config['ptz_service']
            profile_token = config['profiles'][0].token

            req = ptz_service.create_type('ContinuousMove')
            req.ProfileToken = profile_token
            req.Velocity = {'PanTilt': {'x': pan, 'y': tilt}, 'Zoom': {'x': zoom}}

            await asyncio.get_event_loop().run_in_executor(None, ptz_service.ContinuousMove, req)
            logger.info(f"🎯 Moving camera {camera_id}: pan={pan}, tilt={tilt}, zoom={zoom}")
            return True
        except Exception as e:
            logger.error(f"❌ PTZ move failed for {camera_id}: {e}")
            return False

    async def stop_movement(self, camera_id: str) -> bool:
        """Stop PTZ movement."""
        try:
            config = self.camera_configs.get(camera_id)
            if not config:
                return False
            ptz_service = config['ptz_service']
            profile_token = config['profiles'][0].token

            req = ptz_service.create_type('Stop')
            req.ProfileToken = profile_token
            req.PanTilt = True
            req.Zoom = True

            await asyncio.get_event_loop().run_in_executor(None, ptz_service.Stop, req)
            logger.info(f"🛑 Camera {camera_id} stopped.")
            return True
        except Exception as e:
            logger.error(f"❌ PTZ stop failed for {camera_id}: {e}")
            return False

async def main():
    service = ONVIFService()
    
    # Camera info
    camera_id = "PTZ_1"
    ip = "192.168.100.171"
    port = 80
    username = "admin"
    password = "PSTC#100200300"
    
    # Connect camera
    success = await service.connect_camera(camera_id, ip, port, username, password)
    if not success:
        print("❌ Connection failed.")
        return
    
    print("\n🎮 Camera connected! Type commands:")
    print("   w = tilt up | s = tilt down | a = pan left | d = pan right")
    print("   z = zoom in | x = zoom out | q = stop | e = exit\n")
    
    while True:
        cmd = input("Command: ").strip().lower()
        if cmd == 'w':
            await service.move_continuous(camera_id, 0, 0.3)
        elif cmd == 's':
            await service.move_continuous(camera_id, 0, -0.3)
        elif cmd == 'a':
            await service.move_continuous(camera_id, -0.3, 0)
        elif cmd == 'd':
            await service.move_continuous(camera_id, 0.3, 0)
        elif cmd == 'z':
            await service.move_continuous(camera_id, 0, 0, 0.3)
        elif cmd == 'x':
            await service.move_continuous(camera_id, 0, 0, -0.3)
        elif cmd == 'q':
            await service.stop_movement(camera_id)
        elif cmd == 'e':
            await service.stop_movement(camera_id)
            print("👋 Exiting.")
            break
        else:
            print("⚠️ Invalid command. Use w/s/a/d/z/x/q/e.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user.")
