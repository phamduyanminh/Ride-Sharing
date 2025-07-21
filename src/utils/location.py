from __future__ import annotations
from math import radians, cos, sin, asin, sqrt

class Location:
    def __init__(self, latitude: float, longitude: float):
        if not (-90 <= latitude <= 90):
            raise ValueError("Invalid Latitude: Must be between -90 and 90.")
        if not (-180 <= longitude <= 180):
            raise ValueError("Invalid Longitude: Must be between -180 and 180.")
        self.latitude = latitude
        self.longitude = longitude
    
    def calculate_distance(self, end_location: Location) -> float:
        radius = 6371 # Radius of the Earth in kilometers
        
        # Convert decimal degrees to radians
        start_lat, start_long = map(radians, [self.latitude, self.longitude])
        end_lat, end_long = map(radians, [end_location.latitude, end_location.longitude])
        
        # Haversine formula
        long = end_long - start_long
        lat = end_lat - start_lat
        
        # Square of half the chord length. A chord is a straight line connecting two points on a sphere.
        a = sin(lat/2)**2 + cos(start_lat) * cos(end_lat) * sin(long/2)**2
        
        # Angular distance between 2 points
        c = 2 * asin(sqrt(a))
        
        return radius * c  
        