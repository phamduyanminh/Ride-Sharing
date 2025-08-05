import unittest
from unittest.mock import Mock
from ...src.models.rider import Rider
from ...src.usecases.location import Location

class TestRider(unittest.TestCase):
    def setUp(self):
        self.rider = Rider(
            email="mptest@gmail.com",
            user_name="mpham",
            longitude=-79.60,
            latitude=43.60
        )
    
    def test_request_ride(self):
        mock_ride_system = Mock() 
        destination = Location(latitude=43.7, longitude=-79.7)
        
        self.rider.request_ride(mock_ride_system, destination)
        mock_ride_system.create_ride_request.assert_called_once_with(self.rider, destination)