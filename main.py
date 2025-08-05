import random
from datetime import datetime

from src.models.driver import Driver
from .src.models.rider import Rider
from .src.utils.location import Location
from .src.utils.ride_system import RideSystem

# TODO - Only call use-cases functions, don't call any model function
def run_simulation():
    print("===================================================")
    print("      MINI RIDE-SHARING SIMULATOR STARTUP      ")
    print("===================================================")

    # --- SETUP THE SYSTEM ---
    # Define a bounding box for Mississauga [min_lon, min_lat, max_lon, max_lat]
    mississauga_bbox = [-79.8, 43.5, -79.5, 43.7]
    ride_system = RideSystem(operational_area=mississauga_bbox)
    print("\nRide-Sharing System initialized for Mississauga.")

    # --- CREATE AND REGISTER DRIVERS & RIDERS ---
    print("\n--- Registering Participants ---")
    drivers = [
        Driver(email="td1@email.com", user_name="Minh", longitude=-79.64, latitude=43.59),
        Driver(email="td2@email.com", user_name="Mike", longitude=-79.60, latitude=43.62),
        Driver(email="td3@email.com", user_name="Martin", longitude=-79.70, latitude=43.58)
    ]
    for driver in drivers:
        ride_system.register_driver(driver)

    riders = [
        Rider(email="tr1@email.com", user_name="Pham", longitude=-79.65, latitude=43.60),
        Rider(email="tr2@email.com", user_name="Fam", longitude=-79.62, latitude=43.59)
    ]
    for rider in riders:
        ride_system.register_rider(rider)

    # SCENARIO 1: A RIDER COMPLETES A FULL TRIP ---
    print("\n===================================================")
    print("      SCENARIO 1: RICK REQUESTS A RIDE      ")
    print("===================================================")
    try:
        rick = riders[0]
        # Destination within the bbox
        destination = Location(latitude=43.65, longitude=-79.59) 
        
        print(f"\n{rick.user_name} is requesting a ride to {destination}...")
        rick.request_ride(ride_system, destination)

        # Check the state of the system
        active_rides = ride_system.get_active_rides()
        print(f"\nSYSTEM CHECK: There are {len(active_rides)} active rides.")

        # Manually progress the ride for simulation purposes
        current_ride = rick.current_ride
        if current_ride and current_ride.driver:
            driver = current_ride.driver
            print(f"\n--- Ride is in progress with {driver.user_name} ---")
            
            # 1. Driver starts the trip
            driver.start_trip()
            print(f"Ride status: {current_ride.ride_status.value}")

            # 2. Driver completes the trip
            print("\n--- Reached destination ---")
            # Note: In the fixed code, complete_ride() on the Ride object handles everything
            current_ride.complete_ride()
            
            # Verify final state
            print(f"\nIs {driver.user_name} available now? {driver.is_available}")
            print(f"Does {rick.user_name} have a current ride? {rick.current_ride is not None}")
            print(f"Rides in {driver.user_name}'s history: {len(driver.drive_history)}")
            
        else:
            print("\n--- Ride request was not accepted by any driver. ---")

    except Exception as e:
        print(f"An error occurred during Scenario 1: {e}")
        
    # SCENARIO 2: A RIDER CANCELS A RIDE ---
    print("\n===================================================")
    print("      SCENARIO 2: FAM CANCELS HER RIDE      ")
    print("===================================================")
    try:
        fam = riders[1]
        destination_fam = Location(latitude=43.7, longitude=-79.7)
        
        print(f"\n{fam.user_name} is requesting a ride to {destination_fam}...")
        fam.request_ride(ride_system, destination_fam)

        ride_to_cancel = fam.current_ride
        if ride_to_cancel:
            assigned_driver = ride_to_cancel.driver
            print(f"\nRide {ride_to_cancel.ride_id} has been created.")
            if assigned_driver:
                print(f"Driver {assigned_driver.user_name} was assigned and is on their way.")
                print(f"Is {assigned_driver.user_name} available? {assigned_driver.is_available}")

            # Riya decides to cancel
            print(f"\n...Oh no, {fam.user_name} needs to cancel the ride!...")
            fam.cancel_ride()

            # Verify final state
            print(f"\nRide status: {ride_to_cancel.ride_status.value}")
            if assigned_driver:
                 print(f"Is {assigned_driver.user_name} available now? {assigned_driver.is_available}")

        else:
            print("\n--- Ride request was not accepted, so there's nothing to cancel. ---")
            
    except Exception as e:
        print(f"An error occurred during Scenario 2: {e}")

    print("\n===================================================")
    print("              SIMULATION COMPLETE              ")
    print("===================================================")


if __name__ == "__main__":
    run_simulation()