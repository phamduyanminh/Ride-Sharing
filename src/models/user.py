from abc import ABC, abstractmethod
import uuid
from uuid import uuid5

NAME_SPACE = uuid.NAMESPACE_DNS
NAME = "ridesharingapp.com"

class User(ABC):
    def __init__(self, email: str, user_name:str):
        self.user_id: str = str(uuid5(NAME_SPACE, NAME + email))
        self.email: str = email
        self.user_name: str = user_name
    
    @abstractmethod
    def update_location(self, latitude: float, longitude: float):
        pass