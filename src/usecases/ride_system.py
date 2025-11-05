from __future__ import annotations
from typing import List
import random
from geoalchemy2 import WKBElement
from geoalchemy2.shape import to_shape
from typing import List, Optional, Tuple


from src.database.models.ride_model import RideModel, RideStatusEnum
from src.database.models.user_model import UserModel
from src.database.models.driver_model import DriverModel
from src.database.repositories.ride_repository import RideRepository
from src.database.repositories.driver_repository import DriverRepository
from src.database.repositories.rider_repository import RiderRepository
from src.database.repositories.user_repository import UserRepository
from src.core.ride_sharing_manager import ride_sharing_manager_object
from src.models.users.driver import Driver
from src.models.users.rider import Rider
from src.models.ride.ride import Ride
from src.models.location.location import Location

KM_PER_DEGREE = 111.0

class RideSystem:
    def __init__(self):
        self.session = ride_sharing_manager_object.db_session
        self.ride_repo = RideRepository(self.session)  
        self.user_repo = UserRepository(self.session)
        self.driver_repo = DriverRepository(self.session)
        self.rider_repo = RiderRepository(self.session)

    
    """ 
    Rider requests a ride 
    Args:
        rider (Rider): The rider requesting the ride
        destination (Location): The destination of the ride
    Return:
        RideModel: The created ride model
    """
    def request_ride(self, rider: Rider, destination: Location) -> RideModel:
        rider_result = self.rider_repo.get_rider(rider.user_id)
        if rider_result:
            _, rider_model = rider_result
            if rider_model.current_ride_id is not None:
                raise ValueError("Rider already has an ongoing ride!")

        distance = rider.current_location.calculate_distance_in_km(destination)
        new_ride = Ride(
            rider=rider,
            start_location=rider.current_location,
            end_location=destination,
            distance=distance
        )
        new_ride.request_ride()

        self.ride_repo.create_ride(new_ride)
        self.rider_repo.update_rider_current_ride(rider.user_id, new_ride.ride_id)
        print(f"Rider {rider.user_name} has requested a ride.")

        self.process_ride_request(new_ride.ride_id)

        updated_ride_model = self.ride_repo.get_ride(new_ride.ride_id)
        return updated_ride_model
     

    """
    Start a ride when driver pickup rider
    Args:
        ride_id (str): The ride id to be started
    """
    def start_ride(self, ride_id: str):
        ride_model = self.ride_repo.get_ride(ride_id)

        if not ride_model:
            raise ValueError(f"Ride with ID {ride_id} not found!")

        if not ride_model.driver_id:
            raise ValueError(f"Cannot start a ride without a driver for ride {ride_id}!")

        self.ride_repo.start_ride(ride_id)

        start_point = to_shape(ride_model.start_location)
        start_location = Location(latitude=start_point.y, longitude=start_point.x)
        self.user_repo.update_location(str(ride_model.driver_id), start_location)
        print(f"Ride {ride_id} has been started!")
    

    """
    Rider cancels a ride
    Args:
        ride_id (str): The ride to be cancelled
    """
    def cancel_ride(self, ride_id: str):
        ride_model = self.ride_repo.get_ride(ride_id)

        if not ride_model:
            raise ValueError(f"Ride with ID {ride_id} not found!")
        
        if ride_model.ride_status not in [RideStatusEnum.REQUESTED, RideStatusEnum.PICKING_UP]:
            raise ValueError(f"Cannot cancel a ride that is not in requested or picking-up status!")
        
        self.ride_repo.cancel_ride(ride_id)

        self.rider_repo.update_rider_current_ride(str(ride_model.rider_id), None)

        if ride_model.driver_id:
            self.driver_repo.update_driver_current_ride(str(ride_model.driver_id), None)
            self.driver_repo.set_availability(str(ride_model.driver_id), True)

        print(f"Ride {ride_id} has been cancelled!")
    

    """ 
    Complete a ride
    Args:
        ride_id (str): The ride has been completed
    """
    def complete_ride(self, ride_id: str):
        ride_model = self.ride_repo.get_ride(ride_id)

        if not ride_model:
            raise ValueError(f"Ride with ID {ride_id} not found!")

        if not ride_model.driver_id:
            raise ValueError("No driver to complete this ride!")
        if not ride_model.rider_id:
            raise ValueError("No rider to complete this ride!")

        self.ride_repo.complete_ride(ride_id)

        end_point = to_shape(ride_model.end_location)
        end_location = Location(latitude=end_point.y, longitude=end_point.x)
        self.user_repo.update_location(str(ride_model.driver_id), end_location)

        self.rider_repo.update_rider_current_ride(str(ride_model.rider_id), None)
        self.driver_repo.update_driver_current_ride(str(ride_model.driver_id), None)
        self.driver_repo.set_availability(str(ride_model.driver_id), True)

        print(f"Ride {ride_id} has been completed!")
    

    """ 
    Process a ride request by finding and assigning a suitable driver (random assignment)
    Args:
        ride (str): The ride id to be processed
    """
    def process_ride_request(self, ride_id: str):
        print(f"System is processing ride...")
        
        ride_model = self.ride_repo.get_ride(ride_id)
        if not ride_model:
            raise ValueError(f"Ride with ID {ride_id} not found!")

        assigned_driver = None
        suitable_drivers = self.find_suitable_drivers(ride_model)
        if not suitable_drivers:
            print("No drivers found in the operational area.")
        else:
            assigned_driver_tuple = random.choice(suitable_drivers)
            driver_user, driver_model = assigned_driver_tuple
            print(f"Driver {driver_user.user_name} has accepted the ride.")
            assigned_driver = (driver_user, driver_model)
        
        if assigned_driver:
            driver_user, driver_model = assigned_driver
            self.ride_repo.assign_driver(ride_id, str(driver_user.user_id))

            self.driver_repo.set_availability(str(driver_user.user_id), False)
            self.driver_repo.update_driver_current_ride(str(driver_user.user_id), ride_id)
        else:
            print(f"No available drivers accepted the ride. The ride will be cancelled.")
            self.ride_repo.cancel_ride(ride_id)
            self.rider_repo.update_rider_current_ride(str(ride_model.rider_id), None)

    
    """
    Find suitable drivers for a ride within 3km, expanding to 6km if none found
    Args:
        ride_model (RideModel): The ride model to find drivers for
    Returns:
        List[Tuple[UserModel, DriverModel]]: List of suitable driver tuples
    """
    def find_suitable_drivers(self, ride_model: RideModel) -> List[Tuple[UserModel, DriverModel]]:
        print("Searching for drivers within 3km...")
        start_point = to_shape(ride_model.start_location)
        rider_location = Location(latitude=start_point.y, longitude=start_point.x)

        drivers = self.search_driver_in_radius_km(rider_location, 3.0)
        
        if not drivers:
            print("No drivers found. Expanding search to 6km...")
            drivers = self.search_driver_in_radius_km(rider_location, 6.0)
        
        return drivers

    
    """
    Search for available drivers within a specified radius using PostGIS spatial indexing
    Args:   
        rider_location (Location): The rider's location
        radius_km (float): The search radius in kilometers
    Returns:
        List[Tuple[UserModel, DriverModel]]: List of available driver tuples
    """
    def search_driver_in_radius_km(self, rider_location: Location, radius_km: float) -> List[Tuple[UserModel, DriverModel]]:
        drivers = self.driver_repo.find_available_drivers_within_radius(rider_location, radius_km)
        print(f"Found {len(drivers)} drivers within {radius_km} km.")
        return drivers
        
