from sqlalchemy.orm import Session
from geoalchemy2.functions import ST_MakePoint, ST_SetSRID
from typing import Optional
import uuid

from src.database.models.ride_model import RideModel
from src.models.ride.ride import Ride

class RideRepository:
    def __init__(self, session: Session):
        self.session = session
    
    """
    """
    def create_ride(self, ride: Ride) -> RideModel:
        pass