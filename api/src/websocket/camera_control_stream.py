import logging
import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from src.service.camera_service import CameraService
from src.service.camera import curd
from src.core.db import get_db

router = APIRouter()
logger = logging.getLogger(__name__)

camera_service = CameraService()


async def stream_frames(websocket: WebSocket, camera_id: str):
    """Stream video frames to WebSocket client."""
    try:
        while True:
            frame = await camera_service.get_frame(camera_id)
            if frame:
                await websocket.send_json({
                    "type": "frame",
                    "frame": frame
                })
            await asyncio.sleep(0.033)  # ~30 FPS
    except asyncio.CancelledError:
        logger.info(f"Stream task cancelled for camera {camera_id}")
    except Exception as e:
        logger.error(f"Error streaming frames for camera {camera_id}: {e}")


@router.websocket("/camera/{camera_id}/combined")
async def camera_combined_endpoint(websocket: WebSocket, camera_id: str):
    """
    Combined WebSocket endpoint for camera streaming and PTZ control.
    Fetches camera from database and connects via ONVIF.
    """
    await websocket.accept()

    streaming_active = False
    stream_task = None
    camera_connected = False

    try:
        async for db_session in get_db():
            break  # Get a single DB session
        camera = await curd.get_camera(db_session, camera_id)
        if not camera:
            await websocket.send_json({
                "type": "error",
                "message": f"Camera {camera_id} not found in database"
            })
            await websocket.close()
            return

        # ✅ Connect to camera via ONVIF
        success = await camera_service.add_camera(
            camera_id=camera_id,
            ip=camera.ip_address,
            port=camera.port,
            username=camera.username,
            password=camera.password
        )

        if not success:
            await websocket.send_json({
                "type": "error",
                "message": f"Failed to connect to camera {camera_id} via ONVIF"
            })
            await websocket.close()
            return

        camera_connected = True
        await websocket.send_json({
            "type": "info",
            "message": f"Camera {camera_id} connected successfully"
        })
        logger.info(f"Camera {camera_id} connected via ONVIF")

        # ✅ Main WebSocket message loop
        while True:
            data = await websocket.receive_json()
            logger.info(f"Received from camera {camera_id}: {data}")

            msg_type = data.get('type', 'control')
            action = data.get('action')

            # 🎥 Handle streaming actions
            if msg_type == 'stream':
                if action == 'start' and not streaming_active:
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
                        logger.info(f"Streaming started for camera {camera_id}")
                    else:
                        await websocket.send_json({
                            "type": "error",
                            "message": "Failed to start stream"
                        })

                elif action == 'stop' and streaming_active:
                    streaming_active = False
                    if stream_task:
                        stream_task.cancel()
                        try:
                            await stream_task
                        except asyncio.CancelledError:
                            pass
                    await camera_service.stop_streaming(camera_id)
                    await websocket.send_json({
                        "type": "stream_status",
                        "status": "stopped"
                    })
                    logger.info(f"Streaming stopped for camera {camera_id}")

            # 🎮 Handle PTZ control
            elif msg_type == 'control':
                if action == 'move':
                    # Normalize pan/tilt/zoom to -1..1
                    pan = max(min(data.get('pan', 0), 1), -1)
                    tilt = max(min(data.get('tilt', 0), 1), -1)
                    zoom = max(min(data.get('zoom', 0), 1), -1)

                    success = await camera_service.move_camera(
                        camera_id,
                        pan,
                        tilt,
                        zoom
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

            # 🔄 Heartbeat
            elif msg_type == 'ping':
                await websocket.send_json({"type": "pong"})

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for camera {camera_id}")

    except Exception as e:
        logger.error(f"Error in WebSocket for camera {camera_id}: {e}")
        try:
            await websocket.send_json({
                "type": "error",
                "message": str(e)
            })
        except:
            pass

    finally:
        # 🧹 Cleanup
        if streaming_active and stream_task:
            stream_task.cancel()
            try:
                await stream_task
            except asyncio.CancelledError:
                pass
        if streaming_active:
            await camera_service.stop_streaming(camera_id)
        if camera_connected:
            await camera_service.stop_camera_movement(camera_id)

        # ✅ Close DB session cleanly
        if db_session:
            await db_session.close()

        logger.info(f"Cleanup completed for camera {camera_id}")
