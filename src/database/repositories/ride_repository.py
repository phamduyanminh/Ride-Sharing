from sqlalchemy.orm import Session
from geoalchemy2.functions import ST_MakePoint, ST_SetSRID
from geoalchemy2.elements import WKBElement
from typing import Optional, List
import uuid

from src.database.models.rider_model import RiderModel
from src.database.models.ride_model import RideModel, RideStatusEnum
from src.models.ride.ride import Ride
from src.models.location.location import Location

class RideRepository:
    
    def location(self, location: Location) -> WKBElement:
        return ST_SetSRID(ST_MakePoint(location.longitude, location.latitude), 4326)


    """
    This function create ride and add in database
    Args:
        session (Session): The database session
        ride (Ride): The ride object to be created
    Return:
        RideModel: The created ride model
    """
    def create_ride(self, session: Session, ride: Ride) -> RideModel:
        new_ride = RideModel(
            ride_id = uuid.UUID(ride.ride_id),
            rider_id = uuid.UUID(ride.rider.user_id),
            driver_id = uuid.UUID(ride.driver.user_id) if ride.driver else None,
            ride_status = RideStatusEnum[ride.ride_status.name],
            start_location = self.location(ride.start_location),
            end_location = self.location(ride.end_location),
            distance_km = ride.distance
        )
        session.add(new_ride)
        return new_ride


    """
    This function get ride from database based on given ride id
    Args:
        session (Session): The database session
        ride_id (str): The ride id to be retrieved
    Return:
        RideModel: The retrieved ride model
    """
    def get_ride(self, session: Session, ride_id: str) -> Optional[RideModel]:
        return (
            session.query(RideModel)
            .filter_by(ride_id = uuid.UUID(ride_id))
            .first()
        )


    """
    This function update the ride status
    Args:
        session (Session): The database session
        ride_id (str): The ride id to be updated
        new_status (RideStatusEnum): The new status
        current_status (Optional[RideStatusEnum]): The current status to be checked
    Return:
        RideModel: The updated ride model
    """
    def update_status(self, session: Session, ride_id: str, new_status: RideStatusEnum, current_status: set[RideStatusEnum]) -> RideModel:
        ride = self.get_ride(session, ride_id)
        if not ride:
            raise ValueError("Cannot find ride")
        if current_status and ride.ride_status not in current_status:
            raise ValueError(f"Invalid ride status transition: current status is {ride.ride_status}, expected one of {list(current_status)}")
        
        ride.ride_status = new_status      
        return ride


    """
    This function start a ride and update in database
    Args:
        session (Session): The database session
        ride_id (str): The ride id to be started
    Return:
        RideModel: The started ride model
    """
    def start_ride(self, session: Session, ride_id: str) -> RideModel:
        return self.update_status(session, ride_id, RideStatusEnum.IN_TRIP, current_status={RideStatusEnum.PICKING_UP})


    """
    This function complete a ride and update in the database
    Args:
        session (Session): The database session
        ride_id (str): The ride id to be completed
    Return:
        RideModel: The completed ride model
    """
    def complete_ride(self, session: Session, ride_id: str) -> RideModel:
        return self.update_status(session, ride_id, RideStatusEnum.COMPLETED, current_status={RideStatusEnum.IN_TRIP})


    """
    This function cancel a ride and update in database
    Args:
        session (Session): The database session
        ride_id (str): The ride id to be cancelled
    Return:
        RideModel: The cancelled ride model
    """
    def cancel_ride(self, session: Session, ride_id: str) -> RideModel:
        return self.update_status(session, ride_id, RideStatusEnum.CANCELLED, current_status={RideStatusEnum.REQUESTED, RideStatusEnum.PICKING_UP})

    
    """
    This function assign ride to driver and update in database
    Args:
        session (Session): The database session
        ride_id (str): The ride id to assign the driver to
        driver_id (str): The driver id to be assigned
    Return:
        RideModel: The updated ride model with assigned driver
    """
    def assign_driver(self, session: Session, ride_id: str, driver_id: str) -> RideModel:
        ride = self.get_ride(session, ride_id)

        if not ride:
            raise ValueError("Cannot find ride")
        if ride.ride_status != RideStatusEnum.REQUESTED:
            raise ValueError("Cannot assign driver to a ride that is not in REQUESTED status")
        
        ride.driver_id = uuid.UUID(driver_id)
        ride.ride_status = RideStatusEnum.PICKING_UP
        return ride
    

    """
    This function get all active rides from database
    Args:
        session (Session): The database session
    Return:
        List[RideModel]: The list of active rides
    """
    def get_active_rides(self, session: Session) -> List[RideModel]:
        return(
            session.query(RideModel)
            .filter(
                RideModel.ride_status.in_([
                    RideStatusEnum.REQUESTED,
                    RideStatusEnum.PICKING_UP, 
                    RideStatusEnum.IN_TRIP
                ])
            )
            .all()
        )
    

    """
    This function get all completed rides for a driver in database
    Args:
        session (Session): The database session
        driver_id (str): The driver id to be retrieved
    Return:
        List[RideModel]: The list of complete rides for the driver
    """
    def get_driver_rides_history(self, session: Session, driver_id: str) -> Optional[List[RideModel]]:
        return (
            session.query(RideModel)
            .filter(RideModel.driver_id == uuid.UUID(driver_id))
            .filter(RideModel.ride_status == RideStatusEnum.COMPLETED)
            .order_by(RideModel.created_at.desc())
            .all()
        )

    
    """
    This function get all completed rides for a rider in database
    Args:
        session (Session): The database session
        rider_id (str): The rider id to be retrieved
    Return:
        List[RideModel]: The list of complete rides for the rider
    """
    def get_rider_rides_history(self, session: Session, rider_id: str) -> Optional[List[RideModel]]:
        return (
            session.query(RideModel)
            .filter(RideModel.rider_id == uuid.UUID(rider_id))
            .filter(RideModel.ride_status == RideStatusEnum.COMPLETED)
            .order_by(RideModel.created_at.desc())
            .all()
        )
    

    """
    This function get current ride for a rider in database
    Args:
        session (Session): The database session
        rider_id (str): The rider id to be retrieved
    Return:
        RideModel: The current ride for the rider
    """
    def get_rider_current_ride(self, session: Session, rider_id: str) -> Optional[RideModel]:
      return (
          session.query(RideModel)
          .filter(RideModel.rider_id == uuid.UUID(rider_id))
          .filter(RideModel.ride_status.in_([
              RideStatusEnum.REQUESTED,
              RideStatusEnum.PICKING_UP,
              RideStatusEnum.IN_TRIP
          ]))
          .first()
      )