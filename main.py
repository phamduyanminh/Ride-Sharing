from src.core.singleton import singleton_object
from src.models.driver import Driver
from src.models.rider import Rider
from src.usecases.location import Location
from src.usecases.ride_system import RideSystem
from models.ride_status import RideStatus

def run_simulation():
    print("===================================================")
    print("       MINI RIDE-SHARING SIMULATOR STARTUP       ")
    print("===================================================")

    # --- SETUP THE SYSTEM ---
    mississauga_bbox = [-79.8, 43.5, -79.5, 43.7]
    ride_system = RideSystem(operational_area=mississauga_bbox)
    print("\nRide-Sharing System initialized for Mississauga.")

    # --- CREATE AND REGISTER DRIVERS & RIDERS ---
    print("\n--- Registering Participants ---")
    drivers = [
        Driver(email="td1@email.com", user_name="Minh", longitude=-79.64, latitude=43.59),
        Driver(email="td2@email.com", user_name="Mike", longitude=-79.60, latitude=43.62),
        Driver(email="td3@email.com", user_name="Martin", longitude=-79.70, latitude=43.58),
        Driver(email="td4@email.com", user_name="Min", longitude=-79.68, latitude=43.55),
        Driver(email="td5@email.com", user_name="Mart", longitude=-79.55, latitude=43.68),
        Driver(email="td6@email.com", user_name="Kevin", longitude=-79.75, latitude=43.61),
        Driver(email="td7@email.com", user_name="Micheal", longitude=-79.62, latitude=43.66),
        Driver(email="td8@email.com", user_name="Mi", longitude=-79.58, latitude=43.52),
        Driver(email="td9@email.com", user_name="Mark", longitude=-79.72, latitude=43.69)
    ]
    for driver in drivers:
        singleton_object.register_driver(driver)

    riders = [
        Rider(email="tr1@email.com", user_name="Pham", longitude=-79.65, latitude=43.60),
        Rider(email="tr2@email.com", user_name="Fam", longitude=-79.62, latitude=43.59)
    ]
    for rider in riders:
        singleton_object.register_rider(rider)

    # SCENARIO 1: A RIDER COMPLETES A FULL TRIP ---
    print("\n===================================================")
    print("       SCENARIO 1: PHAM REQUESTS A RIDE        ")
    print("===================================================")
    try:
        pham = riders[0]
        destination = Location(latitude=43.65, longitude=-79.59)
        
        # Use the system to request the ride
        current_ride = ride_system.request_ride(pham, destination)

        if current_ride and current_ride.driver:
            driver = current_ride.driver
            print(f"\n--- Ride is in progress with {driver.user_name} ---")
            
            # Simulate trip progress
            current_ride.start_ride()
            print(f"Ride status: {current_ride.ride_status.value}")
            
            print("\n--- Reached destination ---")
            ride_system.complete_ride(current_ride)
            
            # Verify final state
            print(f"\nIs {driver.user_name} available now? {driver.is_available}")
            print(f"Does {pham.user_name} have a current ride? {pham.current_ride is not None}")
        else:
            print("\n--- Ride request was not accepted by any driver. ---")

    except Exception as e:
        print(f"An error occurred during Scenario 1: {e}")
        
    # SCENARIO 2: A RIDER CANCELS A RIDE ---
    print("\n===================================================")
    print("        SCENARIO 2: FAM CANCELS HER RIDE         ")
    print("===================================================")
    try:
        fam = riders[1]
        destination_fam = Location(latitude=43.7, longitude=-79.7)
        
        ride_to_cancel = ride_system.request_ride(fam, destination_fam)

        if ride_to_cancel and ride_to_cancel.ride_status != RideStatus.CANCELLED:
            assigned_driver = ride_to_cancel.driver
            print(f"\nRide {ride_to_cancel.ride_id} created with driver {assigned_driver.user_name}.")
            
            print(f"\n...Oh no, {fam.user_name} needs to cancel the ride!...")
            ride_system.cancel_ride(ride_to_cancel)

            # Verify final state
            print(f"\nRide status: {ride_to_cancel.ride_status.value}")
            if assigned_driver:
                print(f"Is {assigned_driver.user_name} available now? {assigned_driver.is_available}")
        else:
            print("\n--- Ride request was not accepted, so there's nothing to cancel. ---")
            
    except Exception as e:
        print(f"An error occurred during Scenario 2: {e}")

    
    # SCENARIO 3: A DRIVER CANCELS A RIDE ---
    print("\n===================================================")
    print("        SCENARIO 3: DRIVER CANCELS THE RIDE         ")
    print("===================================================")
    try:
        fam = riders[1]
        destination_fam = Location(latitude=43.63, longitude=-79.57)
        print(f"\n{fam.user_name} needs another ride to run more errands.")
        ride = ride_system.request_ride(pham, destination_fam)

        if ride and ride.driver:
            assigned_driver = ride.driver
            print(f"\nRide {ride.ride_id} assigned to driver {assigned_driver.user_name}.")
            print("Driver is on the way to pick up the rider...")

            print(f"Current ride status before cancellation: {ride.ride_status.value}")

            print(f"\nUnexpected issue! Driver {assigned_driver.user_name} must cancel the ride.")
            assigned_driver.cancel_ride(ride)
            ride_system.cancel_ride(ride)

            print(f"\nRide status after driver cancellation: {ride.ride_status.value}")
            print(f"Is {assigned_driver.user_name} available now? {assigned_driver.is_available}")
            print(f"Does {fam.user_name} have a current ride? {fam.current_ride is not None}")
        else:
            print("\n--- No driver accepted the ride, so cancellation is not needed. ---")
    
    except Exception as e:
        print(f"An error occurred during Scenario 3: {e}")

    print("\n===================================================")
    print("               SIMULATION COMPLETE               ")
    print("===================================================")

if __name__ == "__main__":
    run_simulation()
