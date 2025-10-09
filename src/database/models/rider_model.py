from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .base import Base

class RiderModel(Base):
    __tablename__ = 'riders'
    
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id', ondelete='CASCADE'), primary_key=True)
    current_ride_id = Column(UUID(as_uuid=True))
    
    # Relationship to user
    user = relationship("UserModel", backref="rider_profile")