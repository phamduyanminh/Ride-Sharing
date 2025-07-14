from abc import ABC

class User(ABC):
    def __init__(self, user_id: str, email: str, user_name:str):
        self.user_id: str = user_id
        self.email: str = email
        self.user_name: str = user_name