from __future__ import annotations
from typing import List
import random

from src.models.driver import Driver
from src.models.rider import Rider
from src.models.ride import Ride
from src.usecases.location import Location
from src.core.singleton import singleton_object

KM_PER_DEGREE = 111.0

class RideSystem:
    def __init__(self, operational_area: List[float]):
        singleton_object.initialize_spatial_index(operational_area)
    
    
    """ 
    Rider requests a ride 
    Args:
        rider (Rider): The rider requesting the ride
        destination (Location): The destination of the ride
    """
    def request_ride(self, rider: Rider, destination: Location) -> Ride:
        if rider.current_ride:
            raise Exception("Rider already has an ongoing ride!")
        
        distance = rider.current_location.calculate_distance_in_km(destination)
        new_ride = Ride(
            rider = rider,
            start_location = rider.current_location,
            end_location = destination,
            distance = distance
        )
        singleton_object.add_ride(new_ride)
        new_ride.request_ride()
        rider.current_ride = new_ride
        print(f"Rider {rider.user_name} has requested a ride from {rider.current_location} to {destination}.")
        self.process_ride_request(new_ride)
        return new_ride
    
    
    """
    Rider cancels a ride
    Args:
        ride (Ride): The ride to be cancelled
    """
    def cancel_ride(self, ride: Ride):
        if not ride.cancel_ride():
            return
        rider = ride.rider
        driver = ride.driver
        
        if rider:
            rider.current_ride = None
        if driver:
            driver.is_available = True
            driver.current_ride = None
    
    
    """ 
    Complete a ride
    Args:
        ride (Ride): The ride has been completed
    """
    def complete_ride(self, ride: Ride):
        rider = ride.rider
        driver = ride.driver
        
        if not rider:
            raise Exception("No rider to complete this ride!")
        if not driver:
            raise Exception("No driver to complete this ride!")
        
        ride.complete_ride()
        rider.ride_history.append(ride)
        rider.current_ride = None
        driver.drive_history.append(ride)
        driver.is_available = True
        driver.current_ride = None
        print(f"{rider.user_name} has completed ride for {driver.user_name}")

    
    """ 
    Process a ride request by finding and assigning a suitable driver (random assignment)
    Args:
        ride (Ride): The ride to be processed
    """
    def process_ride_request(self, ride: Ride):
        print(f"System is processing ride...")
        suitable_drivers = self.find_suitable_drivers(ride)
        
        assigned_driver = None
        if not suitable_drivers:
            print("No drivers found in the operational area.")
        else:
            assigned_driver = random.choice(suitable_drivers)
            print(f"Driver {assigned_driver.user_name} has accepted the ride.")

        
        if assigned_driver:
            ride.assign_driver(assigned_driver)
            assigned_driver.accept_ride(ride)
        else:
            print(f"No available drivers accepted the ride. The ride will be cancelled.")
            ride.cancel_ride()
    
    """
    Find suitable drivers for a ride within 3km, expanding to 6km if none found
    Args:
        ride (Ride): The ride to find drivers for
    """
    def find_suitable_drivers(self, ride: Ride) -> Driver | None:
        print("Searching for drivers within 3km...")
        drivers = self.search_driver_in_radius_km(ride, 3.0)
        
        if not drivers:
            print("No drivers found. Expanding search to 6km...")
            drivers = self.search_driver_in_radius_km(ride, 6.0)
        
        return drivers

    
    """
    Search for available drivers within a specified radius using spatial indexing and Haversine formula
    Args:
        ride (Ride): Using ride's starting location to find drivers
        radius_km (float): The search radius in kilometers
    """
    def search_driver_in_radius_km(self, ride: Ride, radius_km: float) -> List[Driver]:
        rider_location = ride.start_location
        
        # Coarse search using bounding box
        degree_radius = radius_km / KM_PER_DEGREE # 360 / 3.14 (pi) = 114.0 degrees per km
        search_bbox = [
            rider_location.longitude - degree_radius,
            rider_location.latitude - degree_radius,
            rider_location.longitude + degree_radius,
            rider_location.latitude + degree_radius
        ]
        candidate_drivers = singleton_object.spatial_index.intersect(bbox=search_bbox)

        # Filter available drivers
        available_drivers = [d for d in candidate_drivers if d.is_available]
        
        if not available_drivers:
            print(f"No available drivers found in {radius_km} km bounding box.")
            return []
        
        # Find the closest driver using Haversine algorithm
        closest_drivers = []
        for driver in available_drivers:
            distance = rider_location.calculate_distance_in_km(driver.current_location)
            if distance <= radius_km:
                closest_drivers.append((driver, distance))

        sorted_closest_drivers = sorted(closest_drivers, key=lambda x: x[1])
        sorted_drivers = [driver for driver, distance in sorted_closest_drivers]
        return sorted_drivers