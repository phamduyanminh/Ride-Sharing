import unittest
from unittest.mock import Mock
from src.models.rider import Rider

class TestRider(unittest.TestCase):
    def setUp(self):
        self.rider = Rider(
            email="mptest@gmail.com",
            user_name="mpham",
            longitude=-79.60,
            latitude=43.60
        )
        
    def test_rider_init(self):
        self.assertEqual(self.rider.email, "mptest@gmail.com")
        self.assertEqual(self.rider.user_name, "mpham")
        self.assertEqual(self.rider.current_location.longitude, -79.60)
        self.assertEqual(self.rider.current_location.latitude, 43.60)
        self.assertIsNone(self.rider.current_ride)
        self.assertEqual(self.rider.ride_history, [])
        
    def test_update_location(self):
        new_latitude = 43.65
        new_longitude = -79.70
        
        self.rider.update_location(new_latitude, new_longitude)
        self.assertEqual(self.rider.current_location.latitude, new_latitude)
        self.assertEqual(self.rider.current_location.longitude, new_longitude)
    
    def test_ride_completed(self):
        mock_ride = Mock()
        mock_ride.id = "ride123"
        
        self.rider.current_ride = mock_ride
        self.rider.ride_completed()
        self.assertIsNone(self.rider.current_ride)
        self.assertEqual(len(self.rider.ride_history), 1)
        self.assertIn(mock_ride, self.rider.ride_history)