from __future__ import annotations
from typing import List
import uuid
from uuid import uuid5

from ..users.rider import Rider
from ..users.driver import Driver
from ..location.location import Location
from .ride_status import RideStatus

NAME_SPACE = uuid.NAMESPACE_DNS
NAME = "ridesharingapp.com"

class Ride:
    def __init__(self, rider: Rider, start_location: Location, end_location: Location, driver: Driver = None, distance: float = 0.0):
        self.ride_id: str = str(uuid5(NAME_SPACE, NAME))
        self.rider: Rider = rider
        self.driver: Driver = driver
        self.ride_status: RideStatus = RideStatus.NEW
        self.start_location: Location = start_location
        self.end_location: Location = end_location
        self.distance: float = distance
    
    # Get ride information
    def get_ride_info(self) -> str:
        if self.ride_status == RideStatus.IN_TRIP:
            return (
                f"Ride ID: {self.ride_id}, status: {self.ride_status.value}\n"
                f"Driver: {self.driver.user_name} - Rider: {self.rider.user_name}\n"
                f"Distance: {self.distance} km"
            )
        return "N/A"

    # Check if ride is active
    def ride_is_active(self) -> bool:
        return self.ride_status in [RideStatus.REQUESTED, RideStatus.PICKING_UP, RideStatus.IN_TRIP]
    
    # Handle request for a ride
    def request_ride(self):
        if self.ride_status == RideStatus.NEW:
            self.ride_status = RideStatus.REQUESTED
            print(f"Ride {self.ride_id} has been requested.")
        else:
            raise Exception("Ride can only be requested if it is in NEW status.")
    
    # Assign a driver to a ride
    def assign_driver(self, driver: Driver):
        if self.ride_status == RideStatus.REQUESTED:
            self.driver = driver
            self.ride_status = RideStatus.PICKING_UP
            print(f"Driver {driver.user_name} assigned to ride {self.ride_id}.")
        else:
            raise Exception("Cannot assign driver to a ride that is not in REQUESTED status.")
    
    # Start the ride:
    def start_ride(self):
        if self.ride_status == RideStatus.PICKING_UP:
            if self.driver:
                self.driver.update_location(self.start_location.latitude, self.start_location.longitude)
            self.ride_status = RideStatus.IN_TRIP
            print(f"Ride {self.ride_id} has started.")
        else:
            raise Exception("Cannot start a ride that is not in picking-up status.")

    # Complete the ride
    def complete_ride(self):
        if self.ride_status != RideStatus.IN_TRIP:
            raise Exception("Cannot complete a ride that is not in-trip.")
        if self.driver:
            self.driver.update_location(self.end_location.latitude, self.end_location.longitude)
        self.ride_status = RideStatus.COMPLETED
        print(f"Ride {self.ride_id} has been completed.")
    
    # Cancel the ride
    def cancel_ride(self):
        if self.ride_status == RideStatus.CANCELLED:
            return False
        
        if self.ride_status not in [RideStatus.PICKING_UP, RideStatus.REQUESTED]:
            raise Exception("Cannot cancel a ride that is already in-trip or has finished.")

        self.ride_status = RideStatus.CANCELLED
        print(f"Ride {self.ride_id} has been cancelled.")
        return True