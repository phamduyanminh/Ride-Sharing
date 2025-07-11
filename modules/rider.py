from typing import List
from .user import User

class Rider(User):
    def __init__(self, user_id: str, email: str, user_name: str, longitude: float = 0.0, latitude: float = 0.0):
        super().__init__(user_id, email, user_name)
        self.ride_history: List[Ride] = [] 
        self.current_location: Location = Location(longitude, latitude)