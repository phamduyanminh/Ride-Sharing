from typing import List
from .user import User
from .ride import Ride
from ..usecases.location import Location

class Rider(User):
    def __init__(self, email: str, user_name: str, longitude: float, latitude: float):
        super().__init__(email, user_name)
        self.current_location = Location(latitude, longitude)
        self.current_ride: Ride | None = None
        self.ride_history: List[Ride] = [] 
    
    def update_location(self, latitude: float, longitude: float):
        self.current_location = Location(latitude, longitude)
        print(f"Rider {self.user_name} location updated to {self.current_location}.")
    
    def ride_completed(self):
        if not self.current_ride:
            raise Exception("No ride to complete!")
        
        self.ride_history.append(self.current_ride)
        print(f"Ride {self.current_ride.ride_id} completed by {self.user_name}.")
        self.current_ride = None