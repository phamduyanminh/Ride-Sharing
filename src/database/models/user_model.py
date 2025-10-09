from sqlalchemy import Column, String, Enum, DateTime
from sqlalchemy.dialects.postgresql import UUID
from geoalchemy2 import Geometry
from datetime import datetime
import enum

from .base import Base

class UserTypeEnum(enum.Enum):
    driver = "driver"
    rider = "rider"

class UserModel(Base):
    __tablename__ = "users"

    user_id = Column(UUID(as_uuid=True), primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    user_name = Column(String(50), nullable=False)
    user_type = Column(Enum(UserTypeEnum), nullable=False)
    current_location = Column(Geometry("POINT", srid=4326))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    
