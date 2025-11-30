from sqlalchemy.orm import Session
from geoalchemy2.functions import ST_MakePoint, ST_SetSRID
from typing import Optional, Tuple
import uuid


from src.database.repositories.utils import to_uuid
from src.database.models.user_model import UserModel, UserTypeEnum
from src.database.models.driver_model import DriverModel
from src.database.models.rider_model import RiderModel
from src.models.users.driver import Driver
from src.models.users.rider import Rider
from src.models.location.location import Location

class UserRepository:

    """
    Create new driver
    Args:
        session (Session): The database session
        driver (Driver): The driver object to be created
    Returns:
        UserModel: The created user model (driver)
    """
    def create_driver(self, session: Session, driver: Driver) -> UserModel:
        existing_user = session.query(UserModel).filter_by(email=driver.email).first()
        if existing_user:
            print("User-Driver already exists")
            return existing_user

        user = UserModel(
            user_id = to_uuid(driver.user_id),
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
            user_id = to_uuid(driver.user_id),
            is_available = driver.is_available
        )

        session.add(user)
        session.add(driver_record)
        return user


    """
    Get driver by id
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
            .filter(UserModel.user_id == to_uuid(driver_id))
            .first()
        )

        return driver_result
    

    """
    Create new rider
    Args:
        session (Session): The database session
        rider (Rider): The rider object to be created
    Returns:
        UserModel: The created user model (rider)
    """
    def create_rider(self, session: Session, rider: Rider) -> UserModel:
        existing_rider = session.query(UserModel).filter_by(email=rider.email).first()
        if existing_rider:
            print("User-Rider already exists")
            return existing_rider

        user = UserModel(
            user_id=to_uuid(rider.user_id),
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
            user_id=to_uuid(rider.user_id)
        )
        
        session.add(user)
        session.add(rider_record)
        return user


    """
    Get rider by id
    Args:
        session (Session): The database session
        rider_id (str): The rider id to be retrieved
    Returns:
        Optional[Tuple[UserModel, RiderModel]]: Tuple of user and rider models if found
    """
    def get_rider(self, session: Session, rider_id: str) -> Optional[Tuple[UserModel, RiderModel]]:
        rider_result = (
            session.query(UserModel, RiderModel)
            .join(RiderModel, UserModel.user_id == RiderModel.user_id)
            .filter(UserModel.user_id == to_uuid(rider_id))
            .first()
        )

        return rider_result


    """
    Update user location
    Args:
        session (Session): The database session
        user_id (str): The user ID
        location (Location): The new location
    """
    def update_location(self, session: Session, user_id: str, location: Location):
        user = session.query(UserModel).filter_by(user_id=to_uuid(user_id)).first()
        if not user:
            raise ValueError("User not found")
    
        user.current_location = ST_SetSRID(
            ST_MakePoint(location.longitude, location.latitude),
            4326
        )