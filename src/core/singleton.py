from typing import Dict
from pyqtree import Index

from src.models.driver import Driver
from src.models.rider import Rider
from src.models.ride import Ride


class SingletonClass:
    def __init__(self):
        self.drivers: Dict[str, Driver] = {}
        self.riders: Dict[str, Rider] = {}
        self.rides: Dict[str, Ride] = {}
        self.spatial_index: Index = None
    
    
    """
    This function registers a rider in the system.
    Args:
        rider (Rider): The rider object to be registered.
    """
    def register_rider(self, rider: Rider):
        self.riders[rider.user_id] = rider
        print(f"{rider.user_name} has been registered.")
    
    
    """
    This function retrieves a rider by their ID.
    Args:
        rider_id (str): The ID of the rider.
    Returns:
        Rider: The rider object if found, else None.
    """
    def get_rider(self, rider_id: str) -> Rider:
        return self.riders.get(rider_id)
    
    
    """
    This function initializes the spatial index for driver locations.
    Args:
        operational_area (List[float]): The bounding box for the operational area [minX, minY, maxX, maxY].
    """    
    def initialize_spatial_index(self, operational_area: List[float]):
        self.spatial_index = Index(bbox = operational_area)
    
    
    """
    This function registers a driver in the system and adds them to the spatial index.
    Args:
        driver (Driver): The driver object.
    """    
    def resgister_driver(self, driver: Driver):
        if self.spatial_index is None:
            raise Exception("Spatial index not initialized.")
        self.drivers[driver.user_id] = driver
        location = driver.current_location
        self.spatial_index.insert(
            item=driver,
            bbox=[location.longitude, location.latitude, location.longitude, location.latitude]
        )
        print(f"{driver.user_name} has been registered.")
        
    
    """
    This function retrieves a driver by their ID.
    Args:
        driver_id (str): The ID of the driver.
    """
    def get_driver(self, driver_id: Driver) -> Driver:
        return self.drivers.get(driver_id)
    
    
    """
    This function adds a ride to the system.
    Args:
        ride (Ride): The ride object.
    """
    def add_ride(self, ride: Ride):
        self.rides[ride.ride_id] = ride
    
    
    """
    This function retrieves a ride by its ID.
    Args:
        ride_id (str): The ID of the ride.
    """
    def get_ride(self, ride_id: str) -> Ride:
        return self.rides.get(ride_id)

singleton_object = SingletonClass()