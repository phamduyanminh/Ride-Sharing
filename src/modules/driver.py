from typing import List
from .user import User
from src.utils.location import Location

class Driver(User):
    def __init__(self, user_id: str, email: str, user_name: str, longitude: float, latitude: float):
        super().__init__(user_id, email, user_name) 
        self.current_location = Location(latitude, longitude)
        self.is_available = True
        self.current_ride = None
        self.drive_history: List = [] 