from sqlalchemy import Column, String, Enum, Numeric, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from geoalchemy2 import Geometry
from datetime import datetime
import enum

from .base import Base

class RideStatusEnum(enum.Enum):
    NEW = "NEW"
    REQUESTED = "REQUESTED"
    PICKING_UP = "PICKING_UP"
    IN_TRIP = "IN_TRIP"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

class RideModel(Base):
    __tablename__ = 'rides'
    
    ride_id = Column(UUID(as_uuid=True), primary_key=True)
    rider_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'), nullable=False)
    driver_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'))
    ride_status = Column(Enum(RideStatusEnum), default=RideStatusEnum.NEW)
    start_location = Column(Geometry('POINT', srid=4326), nullable=False)
    end_location = Column(Geometry('POINT', srid=4326), nullable=False)
    distance_km = Column(Numeric(10, 2))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)