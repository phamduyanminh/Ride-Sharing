from __future__ import annotations
from typing import List
from pyqtree import Index
from src.modules.driver import Driver
from src.modules.rider import Rider
from src.modules.ride import Ride
from src.utils.location import Location

KM_PER_DEGREE = 111.0

class RideSystem:
    def __init__(self, operational_area: List[float]):
        self.drivers: List[Driver] = []
        self.riders: List[Rider] = []
        self.rides: List[Ride] = []
        self.spatial_index = Index(bbox=operational_area)   
    
    def create_ride_request(self, rider: Rider, destination: Location):
        # Calculate distance and create ride object
        distance = rider.current_location.calculate_distance_in_km(destination)
        new_ride = Ride(
            rider = rider, 
            start_location = rider.current_location, 
            end_location = destination, 
            distance = distance
            )
        # Track new ride
        self.rides.append(new_ride)
        # Set the ride's status and the rider's current rid
        new_ride.request_ride() 
        rider.current_ride = new_ride
        # Process the request to find a driver
        self.process_ride_request(new_ride)
        print(f"Rider {rider.user_name} has requested a ride from {rider.current_location} to {destination}.")
        
        
    # Add a rider to the system
    def register_rider(self, rider: Rider):
        self.riders.append(rider)
        print(f"Rider {rider.user_name} registered.")
    
    # Add a driver to the system and insert into spatial index
    def register_driver(self, driver: Driver):
        self.drivers.append(driver)
        location = driver.current_location
        self.spatial_index.insert(
            item=driver,
            bbox=[location.longitude, location.latitude, location.longitude, location.latitude]
        )
        print(f"Driver {driver.user_name} registered.")
    
    # Update the driver's location in the system
    def update_driver_location(self, driver: Driver, new_latitude: float, new_longitude: float):
        old_location = driver.current_location
        self.spatial_index.remove(
            item=driver,
            bbox=[old_location.longitude, old_location.latitude, old_location.longitude, old_location.latitude]
        )
        
        driver.update_location(new_latitude, new_longitude)
        new_location = driver.current_location
        self.spatial_index.insert(
            item=driver,
            bbox=[new_location.longitude, new_location.latitude, new_location.longitude, new_location.latitude]
        )

    # Process a ride request
    def process_ride_request(self, ride: Ride):
        print(f"System is processing ride...")
        suitable_drivers = self.find_suitable_drivers(ride)
        
        assigned_driver = None
        if not suitable_drivers:
            print("No drivers found in the operational area.")
        else:
            for driver in suitable_drivers:
                print(f"Offering ride to {driver.user_name}...")
                if driver.decide_on_ride(ride):
                    assigned_driver = driver
                    break
        
        if assigned_driver:
            ride.assign_driver(assigned_driver)
            assigned_driver.accept_ride(ride)
        else:
            print(f"No available drivers accepted the ride. The ride will be cancelled.")
            ride.cancel_ride()
    
    # Search for drivers within a specified radius in km 
    def find_suitable_drivers(self, ride: Ride) -> Driver | None:
        print("Searching for drivers within 3km...")
        drivers = self.search_driver_in_radius_km(ride, 3.0)
        
        if not drivers:
            print("No drivers found. Expanding search to 6km...")
            drivers = self.search_driver_in_radius_km(ride, 6.0)
        
        return drivers

    # Search list of drivers within a specified radius in km using bounding box
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
        candidate_drivers = self.spatial_index.intersect(bbox=search_bbox)

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