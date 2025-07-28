from __future__ import annotations
from typing import List, TYPE_CHECKING
from pyqtree import Index
from src.modules.driver import Driver
from src.modules.ride import Ride
from src.utils.location import Location

KM_PER_DEGREE = 111.0

class RideSystem:
    def __init__(self, operational_area: List[float]):
        self.drivers: List[Driver] = []
        self.spatial_index = Index(bbox=operational_area)        
    
    def add_driver(self, driver: Driver):
        self.drivers.append(driver)
        location = driver.current_location
        self.spatial_index.insert(
            item=driver,
            bbox=[location.longitude, location.latitude, location.longitude, location.latitude]
        )
    
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
    
    def process_ride_request(self, ride: Ride):
       print(f"System is processing ride {ride.ride_id}...") 
       most_suitable_driver = self.find_most_suitable_driver(ride)
       
       if most_suitable_driver:
           most_suitable_driver.accept_ride(ride)
       else:
           ride.cancel_ride()
    
    def find_most_suitable_driver(self, ride: Ride) -> Driver | None:
        print("Searching for drivers within 3km...")
        
        # Parameter of a circle of the earth is 2 * pi * R, where R = 6371KM
        # Ratio of 3km to paramter is 3 / (2 * pi * 6371)
        # Therefore, 3km to radius is (3 / (2 * pi * 6371)) * (2*pi) = 3/6371 rad
        driver = self.search_driver_in_radius_km(ride, 3.0)
        if not driver:
            print("No drivers found. Expanding search to 6km...")
            driver = self.search_driver_in_radius_km(ride, 6.0)
        
        return driver
    
    def search_driver_in_radius_km(self, ride: Ride, radius_km: float) -> Driver | None:
        rider_location = ride.start_location
        
        # Coarse search using bounding box
        # TODO:
        # Create a constant for degree
        # Add unit for search_driver_in_radius_km
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
            return None
        
        # Find the closest driver using Haversine algorithm
        closest_driver = None
        closest_distance = float('inf')
        
        for driver in available_drivers:
            distance = rider_location.calculate_distance_in_km(driver.current_location)
            if distance <= radius_km and distance < closest_distance:
                closest_distance = distance
                closest_driver = driver
        
        if closest_driver:
            print(f"Found driver {closest_driver.user_name} at {closest_distance:.2f} km away.")

        return closest_driver