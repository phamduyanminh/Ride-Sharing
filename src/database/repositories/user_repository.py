from sqlalchemy.orm import Session
from geoalchemy2.functions import ST_MakePoint, ST_SetSRID
from typing import Optional
import uuid

from src.database.models.user_model import UserModel, UserTypeEnum
from src.database.models.driver_model import DriverModel
from src.database.models.rider_model import RiderModel
from src.models.users.driver import Driver
from src.models.users.rider import Rider
from src.models.location.location import Location

class UserRepository:
    def __init__(self, session: Session):
        self.session = session

    """
    Create new driver
    Args:
        driver (Driver): The driver object to be created
    Returns:
        UserModel: The created user model (driver)
    """
    def create_driver(self, driver: Driver) -> UserModel:
        user = UserModel(
            user_id = uuiid.UUID(driver.user_id),
            email = driver.email,
            user_name = driver.user_name,
            user_type = UserTypeEnum.driver,
            current_location = ST_SetSRID(
                ST_MakePoint(
                    driver.current_location.longitude,
                    driver.current_location.latitude
                ),
                4326
            )
        )

        driver_record = DriverModel(
            user_id = uuid.UUID(driver.user_id),
            is_available = driver.is_available
        )

        self.session.add(user)
        self.session.add(driver_record)
        self.session.commit()
        return user

    
    """
    Create new rider
    Args:
        rider (Rider): The rider object to be created
    Returns:
        UserModel: The created user model (rider)
    """
    def create_rider(self, rider: Rider) -> UserModel:
        user = UserModel(
            user_id=uuid.UUID(rider.user_id),
            email=rider.email,
            user_name=rider.user_name,
            user_type=UserTypeEnum.rider,
            current_location=ST_SetSRID(
                ST_MakePoint(rider.current_location.longitude, rider.current_location.latitude),
                4326
            )
        )
        
        # Create rider record
        rider_record = RiderModel(
            user_id=uuid.UUID(rider.user_id)
        )
        
        self.session.add(user)
        self.session.add(rider_record)
        self.session.commit()
        return user
    

    """
    Update user location
    Args:
        user_id (str): The user ID
        location (Location): The new location
    """
    def update_location(self, user_id: str, location: Location):
        user = self.session.query(UserModel).filter_by(user_id=uuid.UUID(user_id)).first()
        if not user:
            raise ValueError("User not found")
    
        user.current_location = ST_SetSRID(
            ST_MakePoint(location.longitude, location.latitude),
            4326
        )
        self.session.commit()