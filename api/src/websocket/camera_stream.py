import logging
from fastapi import APIRouter, HTTPException, status, BackgroundTasks, WebSocket, WebSocketDisconnect
from src.service.camera_service import CameraService

router = APIRouter()
logger = logging.getLogger(__name__)

camera_service = CameraService()

@router.websocket("/camera/{camera_id}/stream")
async def camera_stream_endpoint(websocket: WebSocket, camera_id: str):
    """WebSocket endpoint for camera video streaming."""
    await websocket.accept()
    
    # Track if streaming is active for this connection
    streaming_active = False
    stream_task = None
    
    try:
        while True:
            data = await websocket.receive_json()
            action = data.get('action')
            
            if action == 'start_stream':
                if not streaming_active:
                    # Start streaming for the camera
                    success = await camera_service.start_streaming(camera_id)
                    if success:
                        streaming_active = True
                        # Start the frame streaming task
                        stream_task = asyncio.create_task(
                            stream_frames(websocket, camera_id)
                        )
                        await websocket.send_json({
                            "type": "stream_status", 
                            "status": "started",
                            "camera_id": camera_id
                        })
                        logger.info(f"Started streaming for camera {camera_id}")
                    else:
                        await websocket.send_json({
                            "type": "error", 
                            "message": f"Failed to start stream for camera {camera_id}"
                        })
                        
            elif action == 'stop_stream':
                if streaming_active:
                    streaming_active = False
                    if stream_task:
                        stream_task.cancel()
                        stream_task = None
                    
                    await camera_service.stop_streaming(camera_id)
                    await websocket.send_json({
                        "type": "stream_status", 
                        "status": "stopped",
                        "camera_id": camera_id
                    })
                    logger.info(f"Stopped streaming for camera {camera_id}")
                    
            elif action == 'get_frame':
                # Get single frame on demand
                frame = await camera_service.get_frame(camera_id)
                if frame:
                    await websocket.send_json({
                        "type": "frame",
                        "camera_id": camera_id,
                        "frame": frame
                    })
                else:
                    await websocket.send_json({
                        "type": "error",
                        "message": "Failed to get frame"
                    })
                    
            elif action == 'ping':
                # Heartbeat response
                await websocket.send_json({"type": "pong"})
                
            else:
                await websocket.send_json({
                    "type": "error",
                    "message": f"Unknown action: {action}"
                })
                
    except WebSocketDisconnect:
        logger.info(f"Stream connection closed for camera {camera_id}")
    except Exception as e:
        logger.error(f"Error in stream endpoint for camera {camera_id}: {e}")
        await websocket.send_json({
            "type": "error",
            "message": "Internal server error"
        })
    finally:
        # Cleanup on disconnect
        if streaming_active and stream_task:
            stream_task.cancel()
        if streaming_active:
            await camera_service.stop_streaming(camera_id)

