import logging
import asyncio
import json
from fastapi import APIRouter, HTTPException, status, BackgroundTasks, WebSocket, WebSocketDisconnect
from src.service.camera_service import CameraService

router = APIRouter()
logger = logging.getLogger(__name__)

camera_service = CameraService()

@router.websocket("/camera/{camera_id}/control")
async def camera_control_endpoint(websocket: WebSocket, camera_id: str):
    """WebSocket endpoint for camera PTZ control."""
    await websocket.accept()
    
    try:
        while True:
            data = await websocket.receive_json()
            action = data.get('action')
            
            if action == 'move':
                success = await camera_service.move_camera(
                    camera_id,
                    data.get('pan', 0),
                    data.get('tilt', 0),
                    data.get('zoom', 0)
                )
                await websocket.send_json({
                    "type": "control_ack",
                    "action": "move",
                    "success": success,
                    "camera_id": camera_id
                })
                
            elif action == 'stop':
                success = await camera_service.stop_camera_movement(camera_id)
                await websocket.send_json({
                    "type": "control_ack",
                    "action": "stop",
                    "success": success,
                    "camera_id": camera_id
                })
                
            elif action == 'ping':
                await websocket.send_json({"type": "pong"})
                
            else:
                await websocket.send_json({
                    "type": "error",
                    "message": f"Unknown control action: {action}"
                })
                
    except WebSocketDisconnect:
        logger.info(f"Control connection closed for camera {camera_id}")
        # Stop any ongoing movement when client disconnects
        await camera_service.stop_camera_movement(camera_id)
    except Exception as e:
        logger.error(f"Error in control endpoint for camera {camera_id}: {e}")


