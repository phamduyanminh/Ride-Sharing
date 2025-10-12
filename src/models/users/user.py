from abc import ABC, abstractmethod
import uuid
from uuid import uuid4

NAME_SPACE = uuid.NAMESPACE_DNS
NAME = "ridesharingapp.com"

class User(ABC):
    def __init__(self, email: str, user_name:str):
        self.user_id: str = str(uuid4())
        self.email: str = email
        self.user_name: str = user_name
    
    @abstractmethod
    def update_location(self, latitude: float, longitude: float):
        pass