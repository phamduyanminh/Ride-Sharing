from sqlalchemy import Column, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .base import Base

class DriverModel(Base):
    __tablename__ = 'drivers'
    
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id', ondelete='CASCADE'), primary_key=True)
    is_available = Column(Boolean, default=True)
    current_ride_id = Column(UUID(as_uuid=True))
    
    # Relationship to user
    user = relationship("UserModel", backref="driver_profile")