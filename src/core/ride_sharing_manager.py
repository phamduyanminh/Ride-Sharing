from typing import Optional, Tuple
from sqlalchemy.orm import Session

from src.database.models.base import get_session
from src.database.models.user_model import UserModel
from src.database.models.driver_model import DriverModel
from src.database.models.rider_model import RiderModel
from src.database.models.ride_model import RideModel
from src.database.repositories.user_repository import UserRepository
from src.database.repositories.driver_repository import DriverRepository
from src.database.repositories.rider_repository import RiderRepository
from src.database.repositories.ride_repository import RideRepository
from src.models.users.driver import Driver
from src.models.users.rider import Rider
from src.models.ride.ride import Ride


class RideSharingManager:
    def __init__(self):
        self.db_session = get_session()
        self.user_repo = UserRepository(self.db_session)
        self.driver_repo = DriverRepository(self.db_session)
        self.rider_repo = RiderRepository(self.db_session)
        self.ride_repo = RideRepository(self.db_session)
    
    
    """
    This function registers a rider in the system.
    Args:
        rider (Rider): The rider object to be registered.
    """
    def register_rider(self, rider: Rider):
        print(f"Registering rider {rider.user_name}...")
        self.user_repo.create_rider(rider)
        print(f"{rider.user_name} has been registered.")
    
    
    """
    This function retrieves a rider by their ID.
    Args:
        rider_id (str): The ID of the rider.
    Returns:
        Optional[Tuple[UserModel, RiderModel]]: The tuple of user and rider models if found, else None.
    """
    def get_rider(self, rider_id: str) -> Optional[Tuple[UserModel, RiderModel]]:
        print(f"Getting rider {rider_id} information...")
        return self.rider_repo.get_rider(rider_id)
    
    
    """
    This function registers a driver in the system and adds them to the spatial index.
    Args:
        driver (Driver): The driver object.
    """    
    def register_driver(self, driver: Driver):
        self.user_repo.create_driver(driver)
        print(f"Driver {driver.user_name} has been registered.")
        
    
    """
    This function retrieves a driver by their ID.
    Args:
        Optional[Tuple[UserModel, DriverModel]]: The tuple of user and driver models if found, else None.
    """
    def get_driver(self, driver_id: str) -> Optional[Tuple[UserModel, DriverModel]]:
        print(f"Getting driver {driver_id} information...")
        return self.driver_repo.get_driver(driver_id)
    
    
    """
    This function adds a ride to the system.
    Args:
        ride (Ride): The ride object.
    """
    def add_ride(self, ride: Ride):
        print(f"Creating ride - {ride.ride_id}...")
        self.ride_repo.create_ride(ride)
        print(f"Ride {ride.ride_id} has been created.")
    
    
    """
    This function retrieves a ride by its ID.
    Args:
        ride_id (str): The ID of the ride.
    Returns:
        Optional[RideModel]: The ride model if found, else None.
    """
    def get_ride(self, ride_id: str) -> Optional[RideModel]:
        print(f"Getting ride {ride_id} information...")
        return self.ride_repo.get_ride(ride_id)

ride_sharing_manager_object = RideSharingManager()