from abc import ABC, abstractmethod

class User(ABC):
    def __init__(self, email: str, user_name:str):
        self.user_id: str = email
        self.email: str = email
        self.user_name: str = user_name
    
    @abstractmethod
    def update_location(self, latitude: float, longitude: float):
        pass