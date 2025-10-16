from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from src.service.camera import schema, curd
from src.core.db import get_db as get_async_session

router = APIRouter()

# ----------------------------#
# Create Camera               #
# ----------------------------#
@router.post("/", response_model=schema.CameraRead, status_code=status.HTTP_201_CREATED)
async def create_camera(
    camera: schema.CameraCreate,
    db: AsyncSession = Depends(get_async_session)
):
    return await curd.create_camera(db, camera)

# ----------------------------#
# Read All Cameras            #
# ----------------------------#
@router.get("/", response_model=List[schema.CameraRead])
async def list_cameras(db: AsyncSession = Depends(get_async_session)):
    return await curd.get_cameras(db)

# ----------------------------#
# Read Single Camera          #
# ----------------------------#
@router.get("/{camera_id}", response_model=schema.CameraRead)
async def get_camera(camera_id: str, db: AsyncSession = Depends(get_async_session)):
    camera = await curd.get_camera(db, camera_id)
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    return camera

# ----------------------------#
# Update Camera               #
# ----------------------------#
@router.put("/{camera_id}", response_model=schema.CameraRead)
async def update_camera(
    camera_id: str,
    camera_update: schema.CameraUpdate,
    db: AsyncSession = Depends(get_async_session)
):
    camera = await curd.update_camera(db, camera_id, camera_update)
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    return camera

# ----------------------------#
# Delete Camera               #
# ----------------------------#
@router.delete("/{camera_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_camera(camera_id: str, db: AsyncSession = Depends(get_async_session)):
    deleted = await curd.delete_camera(db, camera_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Camera not found")
    return None
