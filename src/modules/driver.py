from typing import List
from .user import User
from src.utils.location import Location
from src.modules.ride import Ride

class Driver(User):
    def __init__(self, email: str, user_name: str, longitude: float, latitude: float):
        super().__init__(email, user_name) 
        self.current_location: Location = Location(latitude, longitude)
        self.is_available: bool = True
        self.current_ride: Ride | None = None
        self.drive_history: List[Ride] = [] 
    
    # Update driver's location
    def update_location(self, latitude: float, longitude: float):
        self.current_location = Location(latitude, longitude)
        print(f"Driver {self.user_name} location updated to {self.current_location}.")
    
    # Driver accepts a ride
    def accept_ride(self, ride: Ride):
        if not self.is_available:
            raise Exception("Driver is not available to accept a new ride.")
        
        self.current_ride = ride
        self.is_available = False
        print(f"Driver {self.user_name} has accepted a ride from {ride.start_location} to {ride.end_location}.")
    
    # Driver completes a ride
    def complete_ride(self):
        if self.current_ride is None:
            raise Exception("No ride to complete.")
        
        self.drive_history.append(self.current_ride)
        self.current_ride = None
        self.is_available = True
        print(f"Driver {self.user_name} has completed a ride.")
    
    # Driver cancels a ride
    def cancel_ride(self, ride: Ride):
        if self.current_ride is None:
            raise Exception("No current ride to cancel.")
        
        self.current_ride = None
        self.is_available = True
        print(f"Driver {self.user_name} has cancelled a ride from {ride.start_location} to {ride.end_location}.")