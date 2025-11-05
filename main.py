import logging
from src.core.ride_sharing_manager import ride_sharing_manager_object
from src.models.location.location import Location
from src.database.models.ride_model import RideStatusEnum
from src.models.users.driver import Driver
from src.models.users.rider import Rider
from src.usecases.ride_system import RideSystem
from src.database.repositories.driver_repository import DriverRepository
from geoalchemy2.shape import to_shape


def run_simulation():
    logging.info("===================================================")
    logging.info("       MINI RIDE-SHARING SIMULATOR STARTUP       ")
    logging.info("===================================================")

    
    mississauga_bbox = [-79.8, 43.5, -79.5, 43.7]
    ride_system = RideSystem()
    logging.info("\nRide-Sharing System initialized for Mississauga.")
    
    logging.info("\n--- Registering Participants ---")
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
    
    driver_ids = []
    for driver in drivers:
        ride_sharing_manager_object.register_driver(driver)
        driver_ids.append(driver.user_id)

    riders = [
        Rider(email="tr1@email.com", user_name="Pham", longitude=-79.65, latitude=43.60),
        Rider(email="tr2@email.com", user_name="Fam", longitude=-79.62, latitude=43.59)
    ]
    
    rider_ids = []
    for rider in riders:
        ride_sharing_manager_object.register_rider(rider)
        rider_ids.append(rider.user_id)

    # SCENARIO 1: A RIDER COMPLETES A FULL TRIP ---
    logging.info("\n===================================================")
    logging.info("       SCENARIO 1: PHAM REQUESTS A RIDE        ")
    logging.info("===================================================")
    try:
        pham = riders[0]
        destination = Location(latitude=43.65, longitude=-79.59)
        
        # Use the system to request the ride
        ride_model = ride_system.request_ride(pham, destination)

        if ride_model and ride_model.driver_id:
            # Get driver info from database
            driver_result = ride_sharing_manager_object.get_driver(str(ride_model.driver_id))
            if driver_result:
                driver_user, driver_model = driver_result
                logging.info(f"\n--- Ride is in progress with {driver_user.user_name} ---")
                
                # Simulate trip progress
                ride_system.start_ride(str(ride_model.ride_id))
                
                # Get updated ride status from database
                updated_ride = ride_sharing_manager_object.get_ride(str(ride_model.ride_id))
                logging.info(f"Ride status: {updated_ride.ride_status.value}")

                logging.info(f"Getting driver information from database...")
                driver_repository = DriverRepository(ride_sharing_manager_object.db_session)
                user_info, driver_info = driver_repository.get_driver(str(ride_model.driver_id))
                logging.info(f"Driver information: {driver_info.is_available}")
                
                logging.info("\n--- Reached destination ---")
                ride_system.complete_ride(str(ride_model.ride_id)) # -> This should be an API
                
                # Verify final state from database
                final_driver_result = ride_sharing_manager_object.get_driver(str(ride_model.driver_id))
                if final_driver_result:
                    _, final_driver_model = final_driver_result
                    logging.info(f"\nIs {driver_user.user_name} available now? {final_driver_model.is_available}")
                
                # Check if rider has current ride
                rider_current_ride = ride_system.ride_repo.get_rider_current_ride(pham.user_id)
                logging.info(f"Does {pham.user_name} have a current ride? {rider_current_ride is not None}")
        else:
            logging.info("\n--- Ride request was not accepted by any driver. ---")

    except Exception as e:
        logging.info(f"An error occurred during Scenario 1: {e}")
        import traceback
        traceback.logging.info_exc()
        
    # SCENARIO 2: A RIDER CANCELS A RIDE ---
    # logging.info("\n===================================================")
    # logging.info("        SCENARIO 2: FAM CANCELS HIS RIDE         ")
    # logging.info("===================================================")
    # try:
    #     fam = riders[1]
    #     destination_fam = Location(latitude=43.7, longitude=-79.7)
        
    #     ride_model = ride_system.request_ride(fam, destination_fam)

    #     if ride_model and ride_model.ride_status != RideStatusEnum.CANCELLED:
    #         if ride_model.driver_id:
    #             # Get driver info from database
    #             driver_result = ride_sharing_manager_object.get_driver(str(ride_model.driver_id))
    #             if driver_result:
    #                 driver_user, _ = driver_result
    #                 logging.info(f"\nRide {ride_model.ride_id} created with driver {driver_user.user_name}.")
                    
    #                 logging.info(f"\n...Oh no, {fam.user_name} needs to cancel the ride!...")
    #                 ride_system.cancel_ride(str(ride_model.ride_id))

    #                 # Verify final state from database
    #                 cancelled_ride = ride_sharing_manager_object.get_ride(str(ride_model.ride_id))
    #                 logging.info(f"\nRide status: {cancelled_ride.ride_status.value}")
                    
    #                 final_driver_result = ride_sharing_manager_object.get_driver(str(ride_model.driver_id))
    #                 if final_driver_result:
    #                     _, final_driver_model = final_driver_result
    #                     logging.info(f"Is {driver_user.user_name} available now? {final_driver_model.is_available}")
    #     else:
    #         logging.info("\n--- Ride request was not accepted, so there's nothing to cancel. ---")
            
    # except Exception as e:
    #     logging.info(f"An error occurred during Scenario 2: {e}")
    #     import traceback
    #     traceback.logging.info_exc()

    
    # # SCENARIO 3: A DRIVER CANCELS A RIDE ---
    # logging.info("\n===================================================")
    # logging.info("        SCENARIO 3: DRIVER CANCELS THE RIDE         ")
    # logging.info("===================================================")
    # try:
    #     fam = riders[1]
    #     destination_fam = Location(latitude=43.63, longitude=-79.57)
    #     logging.info(f"\n{fam.user_name} needs another ride to run more errands.")
    #     ride_model = ride_system.request_ride(fam, destination_fam)

    #     if ride_model and ride_model.driver_id:
    #         # Get driver info from database
    #         driver_result = ride_sharing_manager_object.get_driver(str(ride_model.driver_id))
    #         if driver_result:
    #             driver_user, _ = driver_result
    #             logging.info(f"\nRide {ride_model.ride_id} assigned to driver {driver_user.user_name}.")
    #             logging.info("Driver is on the way to pick up the rider...")

    #             # Get current ride status from database
    #             current_ride = ride_sharing_manager_object.get_ride(str(ride_model.ride_id))
    #             logging.info(f"Current ride status before cancellation: {current_ride.ride_status.value}")

    #             logging.info(f"\nUnexpected issue! Driver {driver_user.user_name} must cancel the ride.")
    #             ride_system.cancel_ride(str(ride_model.ride_id))

    #             # Get updated status from database
    #             cancelled_ride = ride_sharing_manager_object.get_ride(str(ride_model.ride_id))
    #             logging.info(f"\nRide status after driver cancellation: {cancelled_ride.ride_status.value}")
                
    #             # Check driver availability from database
    #             final_driver_result = ride_sharing_manager_object.get_driver(str(ride_model.driver_id))
    #             if final_driver_result:
    #                 _, final_driver_model = final_driver_result
    #                 logging.info(f"Is {driver_user.user_name} available now? {final_driver_model.is_available}")
                
    #             # Check if rider has current ride
    #             rider_current_ride = ride_system.ride_repo.get_rider_current_ride(fam.user_id)
    #             logging.info(f"Does {fam.user_name} have a current ride? {rider_current_ride is not None}")
    #     else:
    #         logging.info("\n--- No driver accepted the ride, so cancellation is not needed. ---")
    
    # except Exception as e:
    #     logging.info(f"An error occurred during Scenario 3: {e}")
    #     import traceback
    #     traceback.logging.info_exc()

    logging.info("\n===================================================")
    logging.info("               SIMULATION COMPLETE               ")
    logging.info("===================================================")

if __name__ == "__main__":
    run_simulation()