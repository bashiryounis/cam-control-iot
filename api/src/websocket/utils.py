import logging
import asyncio
from fastapi import WebSocket
from src.service.camera_service import CameraService

logger = logging.getLogger(__name__)

camera_service = CameraService()


async def stream_frames(websocket: WebSocket, camera_id: str):
    """Background task to continuously stream frames."""
    try:
        while True:
            frame = await camera_service.get_frame(camera_id)
            if frame:
                await websocket.send_json({
                    "type": "frame",
                    "camera_id": camera_id,
                    "frame": frame,
                    "timestamp": asyncio.get_event_loop().time()
                })
            else:
                # If no frame available, send error and break
                await websocket.send_json({
                    "type": "stream_error",
                    "message": "No frame available"
                })
                break
                
            # Control frame rate (~30 FPS)
            await asyncio.sleep(0.033)
            
    except asyncio.CancelledError:
        logger.info(f"Frame streaming cancelled for camera {camera_id}")
    except Exception as e:
        logger.error(f"Error streaming frames for camera {camera_id}: {e}")

