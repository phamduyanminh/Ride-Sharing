from sqlalchemy.orm import Session
from geoalchemy2 import Geography
from geoalchemy2.functions import ST_DWithin, ST_MakePoint, ST_SetSRID
from typing import List, Optional, Tuple
import uuid

from src.database.models.user_model import UserModel
from src.database.models.driver_model import DriverModel
from src.models.location.location import Location

class DriverRepository:

    """
    Find available drivers within a radius
    Args:
        session (Session): The database session
        location (Location): The location to search for drivers
        radius_km (float): The radius in kilometers
    Returns:
        List[UserModel]: The list of available drivers
    """
    def find_available_drivers_within_radius(self, session: Session, location: Location, radius_km: float) -> List[Tuple[UserModel, DriverModel]]:
        search_point = ST_SetSRID(ST_MakePoint(location.longitude, location.latitude), 4326)
        radius_meter = radius_km * 1000

        drivers = (
            session.query(UserModel, DriverModel)
            .join(DriverModel, UserModel.user_id == DriverModel.user_id)
            .filter(DriverModel.is_available)
            .filter(
                ST_DWithin(
                    UserModel.current_location.cast(Geography),
                    search_point.cast(Geography),
                    radius_meter
                )
            )
            .all()
        )
        return drivers
    

    """
    Set driver availability
    Args:
        session (Session): The database session
        driver_id (str): The driver ID
        is_available (bool): The availability status
    """
    def set_availability(self, session: Session, driver_id: str, is_available: bool):
        driver = session.query(DriverModel).filter_by(
            user_id = uuid.UUID(driver_id)
            ).first()
        
        if driver is None:
            raise ValueError("Driver not found")
        
        driver.is_available = is_available


    """
    Update driver's current ride
    Args:
        session (Session): The database session
        driver_id (str): The driver ID
        ride_id (Optional[str]): The ride ID
    """
    def update_driver_current_ride(self, session: Session, driver_id: str, ride_id: Optional[str]):
        driver = session.query(DriverModel).filter(
            DriverModel.user_id == uuid.UUID(driver_id)
        ).first()

        if driver is None:
            raise ValueError("Driver not found")
        
        driver.current_ride_id = uuid.UUID(ride_id) if ride_id else None

    
    """
    Get driver by id with user information
    Args:
        session (Session): The database session
        driver_id (str): The driver id to be retrieved
    Returns:
        Optional[Tuple[UserModel, DriverModel]]: Tuple of user and driver models if found
    """
    def get_driver(self, session: Session, driver_id: str) -> Optional[Tuple[UserModel, DriverModel]]:
        driver_result = (
            session.query(UserModel, DriverModel)
            .join(DriverModel, UserModel.user_id == DriverModel.user_id)
            .filter(UserModel.user_id == uuid.UUID(driver_id))
            .first()
        )
        return driver_result