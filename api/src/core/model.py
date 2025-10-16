import uuid
from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from src.core.db import Base

# ----------------------------------------#
# Camera Model                             #
# ----------------------------------------#

class Camera(Base):
    """
    Represents a network or PTZ camera device.

    Attributes:
        id (str): Unique identifier (UUID) for the camera.
        name (str): Unique camera name.
        ip_address (str): Camera IP address.
        port (str): Camera port (default 80).
        username (str): Camera login username.
        password (str): Camera login password.
        is_active (bool): Whether the camera is currently active.
        image (str, optional): Image path or URL representing the camera.
    """
    __tablename__ = "cameras"

    id: str = Column(String,primary_key=True,default=lambda: str(uuid.uuid4()),unique=True,index=True,doc="Unique camera identifier")
    name: str = Column(String, index=True, nullable=False, doc="camera name")
    ip_address: str = Column(String, nullable=False, doc="Camera IP address")
    port: str = Column(String, default="80", nullable=False, doc="Camera port")
    username: str = Column(String, nullable=False, doc="Camera login username")
    password: str = Column(String, nullable=False, doc="Camera login password")
    image: str = Column(String,nullable=True,doc="Image path or URL representing the camera")
    is_active: bool = Column(Boolean,default=False,doc="Indicates if the camera is currently active")
