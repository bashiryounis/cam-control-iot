from pydantic import BaseModel, HttpUrl
from typing import Optional

# ----------------------------#
# Base schema for Camera      #
# ----------------------------#
class CameraBase(BaseModel):
    name: str
    ip_address: str
    port: int
    username: str
    password: str
    is_active: Optional[bool] = False
    image: Optional[str] = None

# ----------------------------#
# Schema for creating Camera  #
# ----------------------------#
class CameraCreate(CameraBase):
    pass

# ----------------------------#
# Schema for updating Camera  #
# ----------------------------#
class CameraUpdate(BaseModel):
    name: Optional[str] = None
    ip_address: Optional[str] = None
    port: Optional[int] = None
    username: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    image: Optional[str] = None

# ----------------------------#
# Schema for reading Camera   #
# ----------------------------#
class CameraRead(CameraBase):
    id: str

    class Config:
        orm_mode = True
