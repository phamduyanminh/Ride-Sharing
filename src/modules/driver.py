from typing import List
from .user import User

class Driver(User):
    def __init__(self, user_id: str, email: str, user_name: str, longitude: float = 0.0, latitude: float = 0.0):
        super().__init__(user_id, email, user_name) 
        if (-180 <= longitude <= 180) and (-90 <= latitude <= 90):
            self.current_location = (latitude, longitude)
        else:
            raise ValueError("Invalid coordinates: Longitude must be between -180 and 180, Latitude must be between -90 and 90.")
        self.is_available = True
        self.current_ride = None
        self.drive_history: List = [] 