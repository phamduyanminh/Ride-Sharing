from typing import Dict
from src.models.driver import Driver
from src.models.rider import Rider
from src.models.ride import Ride


class SingletonClass:
    def __init__(self):
        self.drivers: Dict[str, Driver] = {}
        self.riders: Dict[str, Rider] = {}
        self.rides: Dict[str, Ride] = {}
    
    def add_driver(self, driver: Driver):
        self.drivers[driver.user_id] = driver
        
    def get_driver(self, driver_id: Driver) -> Driver:
        return self.drivers.get(driver_id)
    
    def add_rider(self, rider: Rider):
        self.riders[rider.user_id] = rider
    
    def get_rider(self, rider_id: str) -> Rider:
        return self.riders.get(rider_id)

    def add_ride(self, ride: Ride):
        self.rides[ride.ride_id] = ride
    
    def get_ride(self, ride_id: str) -> Ride:
        return self.rides.get(ride_id)