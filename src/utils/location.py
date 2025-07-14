class Location:
    def __init__(self, latitude: float, longitude: float):
        if not (-90 <= latitude <= 90):
            raise ValueError("Invalid Latitude: Must be between -90 and 90.")
        if not (-180 <= longitude <= 180):
            raise ValueError("Invalid Longitude: Must be between -180 and 180.")
        self.latitude = latitude
        self.longitude = longitude