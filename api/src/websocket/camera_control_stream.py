import logging
import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from src.service.camera_service import CameraService
from src.websocket.utils import stream_frames  

router = APIRouter()
logger = logging.getLogger(__name__)

camera_service = CameraService()


@router.websocket("/camera/{camera_id}/combined")
async def camera_combined_endpoint(websocket: WebSocket, camera_id: str):
    """Combined WebSocket endpoint for both streaming and control."""
    await websocket.accept()
    
    streaming_active = False
    stream_task = None
    
    try:
        while True:
            data = await websocket.receive_json()
            action = data.get('action')
            msg_type = data.get('type', 'control')  # Default to control
            
            if msg_type == 'stream':
                # Handle stream actions
                if action == 'start':
                    if not streaming_active:
                        success = await camera_service.start_streaming(camera_id)
                        if success:
                            streaming_active = True
                            stream_task = asyncio.create_task(
                                stream_frames(websocket, camera_id)
                            )
                            await websocket.send_json({
                                "type": "stream_status", 
                                "status": "started"
                            })
                            
                elif action == 'stop':
                    if streaming_active:
                        streaming_active = False
                        if stream_task:
                            stream_task.cancel()
                        await camera_service.stop_streaming(camera_id)
                        await websocket.send_json({
                            "type": "stream_status", 
                            "status": "stopped"
                        })
                        
            elif msg_type == 'control':
                # Handle control actions
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
                        "success": success
                    })
                    
                elif action == 'stop':
                    success = await camera_service.stop_camera_movement(camera_id)
                    await websocket.send_json({
                        "type": "control_ack",
                        "action": "stop", 
                        "success": success
                    })
            
            elif msg_type == 'ping':
                await websocket.send_json({"type": "pong"})
                
    except WebSocketDisconnect:
        logger.info(f"Combined connection closed for camera {camera_id}")
    finally:
        # Cleanup
        if streaming_active and stream_task:
            stream_task.cancel()
        if streaming_active:
            await camera_service.stop_streaming(camera_id)
        await camera_service.stop_camera_movement(camera_id)