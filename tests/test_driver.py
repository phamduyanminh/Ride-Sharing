import unittest
from unittest.mock import Mock
import models.users.driver as Driver

class TestDriver(unittest.TestCase):
    def setUp(self):
        self.driver = Driver.Driver(
            email="mpdriver@gmail.com",
            user_name="mpdriver",
            longitude=-79.64,
            latitude=43.59
        )
        
        self.mock_ride = Mock()
        self.mock_ride.id = "ride123"
    
    def test_driver_init(self):
        self.assertEqual(self.driver.email, "mpdriver@gmail.com")
        self.assertEqual(self.driver.user_name, "mpdriver")
        self.assertTrue(self.driver.is_available)
        self.assertIsNone(self.driver.current_ride)
        self.assertEqual(self.driver.drive_history, [])
    
    def test_update_location(self):
        new_latitude = 43.70
        new_longitude = -79.80
        
        self.driver.update_location(new_latitude, new_longitude)
        self.assertEqual(self.driver.current_location.latitude, new_latitude)
        self.assertEqual(self.driver.current_location.longitude, new_longitude)
    
    def test_accept_ride(self):        
        self.driver.accept_ride(self.mock_ride)
        self.assertFalse(self.driver.is_available)
        self.assertEqual(self.driver.current_ride, self.mock_ride)
    
    def test_complete_ride(self):
        self.driver.current_ride = self.mock_ride
        self.driver.complete_ride()
        
        self.assertTrue(self.driver.is_available)
        self.assertIsNone(self.driver.current_ride)
        self.assertIn(self.mock_ride, self.driver.drive_history)
        self.assertEqual(len(self.driver.drive_history), 1)
    
    def test_cancel_ride(self):
        self.driver.current_ride = self.mock_ride
        self.driver.cancel_ride(self.mock_ride)

        self.assertTrue(self.driver.is_available)
        self.assertIsNone(self.driver.current_ride)
        # Typically, a cancelled ride would not go into history
        self.assertNotIn(self.mock_ride, self.driver.drive_history)