from sqlalchemy.orm import Session
from typing import Optional, Tuple
import uuid

from src.database.models.user_model import UserModel
from src.database.models.rider_model import RiderModel

class RiderRepository:

    """
    Get rider by id with user information
    Args:
        session (Session): The database session
        rider_id (str): The rider id to be retrieved
    Returns:
        Optional[Tuple[UserModel, RiderModel]]: Tuple of user and rider models if found
    """
    def get_rider(self, session: Session, rider_id: str) -> Optional[Tuple[UserModel, RiderModel]]:
        rider_result = (
            session.query(UserModel, RiderModel)
            .join(RiderModel, UserModel.user_id == RiderModel.user_id)
            .filter(UserModel.user_id == uuid.UUID(rider_id))
            .first()
        )
        return rider_result
    

    """
    Update rider's current ride
    Args:
        session (Session): The database session
        rider_id (str): The rider ID
        ride_id (Optional[str]): The ride ID
    """
    def update_rider_current_ride(self, session: Session, rider_id: str, ride_id: Optional[str]):
        rider = session.query(RiderModel).filter(
            RiderModel.user_id == uuid.UUID(rider_id)
        ).first()

        if rider is None:
            raise ValueError("Rider not found")
        
        rider.current_ride_id = uuid.UUID(ride_id) if ride_id else None