from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.core.model import Camera
from src.service.camera.schema import CameraCreate, CameraUpdate

# Create camera
async def create_camera(db: AsyncSession, camera: CameraCreate):
    db_camera = Camera(**camera.dict())
    db.add(db_camera)
    await db.commit()
    await db.refresh(db_camera)
    return db_camera

# Get all cameras
async def get_cameras(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(select(Camera).offset(skip).limit(limit))
    return result.scalars().all()

# Get by ID
async def get_camera(db: AsyncSession, camera_id: str):
    result = await db.execute(select(Camera).where(Camera.id == camera_id))
    return result.scalar_one_or_none()

# Update
async def update_camera(db: AsyncSession, camera_id: str, camera: CameraUpdate):
    db_camera = await get_camera(db, camera_id)
    if not db_camera:
        return None
    for field, value in camera.dict(exclude_unset=True).items():
        setattr(db_camera, field, value)
    db.add(db_camera)
    await db.commit()
    await db.refresh(db_camera)
    return db_camera

# Delete
async def delete_camera(db: AsyncSession, camera_id: str):
    db_camera = await get_camera(db, camera_id)
    if not db_camera:
        return None
    await db.delete(db_camera)
    await db.commit()
    return db_camera
