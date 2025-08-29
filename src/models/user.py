from abc import ABC, abstractmethod
from uuid import uuid7

class User(ABC):
    def __init__(self, email: str, user_name:str):
        self.user_id: str = str(uuid7())
        self.email: str = email
        self.user_name: str = user_name
    
    @abstractmethod
    def update_location(self, latitude: float, longitude: float):
        pass