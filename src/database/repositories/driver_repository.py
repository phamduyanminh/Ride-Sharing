from geoalchemy2 import Geography
from sqlalchemy.orm import Session
from geoalchemy2.functions import ST_DWithin, ST_Distance, ST_MakePoint, ST_SetSRID, ST_Within
from typing import List, Optional, Tuple
import uuid

from src.database.models.user_model import UserModel
from src.database.models.driver_model import DriverModel
from src.models.location.location import Location

class DriverRepository:
    def __init__(self, session: Session):
        self.session = session
    
    """
    Find available drivers within a radius
    Args:
        location (Location): The location to search for drivers
        radius_km (float): The radius in kilometers
    Returns:
        List[UserModel]: The list of available drivers
    """
    def find_available_drivers_within_radius(self, location: Location, radius_km: float) -> List[UserModel]:
        search_point = ST_SetSRID(ST_MakePoint(location.longitude, location.latitude), 4326)
        radius_meter = radius_km * 1000
        driver = (
            self.session.query(UserModel)
            .join(DriverModel, UserModel.user_id == DriverModel.user_id)
            .filter(DriverModel.is_available == True)
            .filter(
                ST_DWithin(
                    UserModel.current_location.cast(Geography),
                    search_point.cast(Geography),
                    radius_meter
                )
            )
            .all()
        )
        return driver
    
    """
    Set driver availability
    Args:
        driver_id (str): The driver ID
        is_available (bool): The availability status
    """
    def set_availability(self, driver_id: str, is_available: bool):
        driver = self.session.query(DriverModel).filter_by(
            user_id = uuid.UUID(driver_id)
            ).first()
        
        if driver is None:
            raise ValueError("Driver not found")
        
        driver.is_available = is_available
        self.session.commit()


    """
    Update driver's current ride
    Args:
        driver_id (str): The driver ID
        ride_id (Optional[str]): The ride ID
    """
    def update_current_ride(self, driver_id: str, ride_id: Optional[str]):
        driver = self.session.query(DriverModel).filter(
            user_id = uuid.UUID(driver_id)
        ).first()

        if driver is None:
            raise ValueError("Driver not found")
        
        driver.current_ride_id = uuid.UUID(ride_id) if ride_id else None
        self.session.commit()

    
    """
    Get driver by id with user information
    Args:
        driver_id (str): The driver id to be retrieved
    Returns:
        Optional[Tuple[UserModel, DriverModel]]: Tuple of user and driver models if found
    """
    def get_driver(self, driver_id: str) -> Optional[Tuple[UserModel, DriverModel]]:
        driver_result = (
            self.session.query(UserModel, DriverModel)
            .join(DriverModel, UserModel.user_id == DriverModel.user_id)
            .filter(UserModel.user_id == uuid.UUID(driver_id))
            .first()
        )
        return driver_result