from .rider import Rider
from .driver import Driver
from src.utils.location import Location
from src.utils.ride_status import RideStatus

class Ride:
    def __init__(self, rider: Rider, start_location: Location, end_location: Location, driver: Driver = None):
        self.ride_id: str = id(self)
        self.rider: Rider = rider
        self.driver: Driver = driver
        self.start_location: Location = start_location
        self.end_location: Location = end_location
        self.ride_status: RideStatus = RideStatus.NEW
    
    # Get ride information
    def get_ride_info(self) -> str:
        if self.ride_status == RideStatus.IN_TRIP:
            return (
                f"Ride ID: {self.ride_id}, status: {self.ride_status.value}"
                f"Driver: {self.driver.user_name} - Rider: {self.rider.user_name}"
            )
        return "N/A"

    # Check if ride is active
    def ride_is_active(self) -> bool:
        return self.ride_status == RideStatus.IN_TRIP
    
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
            self.ride_status = RideStatus.IN_TRIP
            print(f"Ride {self.ride_id} has started.")
        else:
            raise Exception("Cannot start a ride that is not in picking-up status.")
    
    # Cancel the ride
    def cancel_ride(self):
        if self.ride_status in [RideStatus.PICKING_UP, RideStatus.REQUESTED]:
            self.ride_status = RideStatus.CANCELLED
            print(f"Ride {self.ride_id} has been cancelled.")
        else:
            raise Exception("Cannot cancel a ride that is in-trip or not in requested status.")

    # Complete the ride
    def complete_ride(self):
        if not self.ride_is_active():
            raise Exception("Cannot complete a ride that is not in-trip.")
        self.ride_status = RideStatus.COMPLETED