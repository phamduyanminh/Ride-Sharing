import logging
from geoalchemy2.shape import to_shape


from src.database.models.base import get_session, init_database
from src.models.location.location import Location
from src.database.models.user_model import UserModel, UserTypeEnum
from src.database.repositories.user_repository import UserRepository
from src.database.repositories.driver_repository import DriverRepository
from src.database.repositories.rider_repository import RiderRepository
from src.database.repositories.ride_repository import RideRepository
from src.models.users.driver import Driver
from src.models.users.rider import Rider
from src.models.ride.ride import Ride


def has_existing_data(session) -> bool:
    count = session.query(UserModel).filter_by(user_type=UserTypeEnum.driver).count()
    return count > 0


def ask_continue(step_name: str) -> bool:
    while True:
        response = input(f"\n[Step {step_name} completed. Continue to next step? (y/n)]").strip().lower()
        if response in ('yes', 'y'):
            return True
        elif response in ('no', 'n'):
            return False
        else:
            print("Invalid input. Please enter 'y' or 'n'.")

def print_step_header(step_num: int, title: str):
      print(f"\n{'='*60}")
      print(f"  STEP {step_num}: {title}")
      print(f"{'='*60}")


def print_result(label: str, value):
    print(f"  -> {label}: {value}")




def run_simulation():
    logging.info("===================================================")
    logging.info("       MINI RIDE-SHARING SIMULATOR STARTUP       ")
    logging.info("===================================================")

    # Initialize database
    init_database()
    
    # Initialize repositories directly
    user_repo = UserRepository()
    driver_repo = DriverRepository()
    rider_repo = RiderRepository()
    ride_repo = RideRepository()

    # Create single session for all operations
    session = get_session()
    session_id = id(session)
    print(f"[Session Created] ID: {session_id}")

    skip_resgistration = has_existing_data(session)
    if skip_resgistration:
        print("[INFO] Existing drivers found. Skipping registration steps.")

        # Load existing riders from database
        rider_records = session.query(UserModel).filter_by(user_type=UserTypeEnum.rider).all()
        riders = []
        for r in rider_records:
            loc = to_shape(r.current_location)
            riders.append(Rider(
                email=r.email,
                user_name=r.user_name,
                longitude=loc.x,
                latitude=loc.y,
                user_id=r.user_id
            ))
        if not riders:
            print("[ERROR] No existing riders found in database. Cannot proceed.")
            return
    else:
        # ============================================================
        # STEP 1: Register Drivers
        # ============================================================
        print_step_header(1, "REGISTER DRIVERS")

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
            user_repo.create_driver(session, driver)
            print_result("Registered Driver", f"{driver.user_name} ({driver.email})")

        session.flush()
        print_result("Total Drivers", len(drivers))

        if not ask_continue("Register Drivers"):
            raise InterruptedError("User cancelled")

        # ============================================================
        # STEP 2: Register Riders
        # ============================================================
        print_step_header(2, "REGISTER RIDERS")

        riders = [
            Rider(email="tr1@email.com", user_name="Pham", longitude=-79.65, latitude=43.60),
            Rider(email="tr2@email.com", user_name="Fam", longitude=-79.62, latitude=43.59)
        ]

        for rider in riders:
            user_repo.create_rider(session, rider)
            print_result("Registered Rider", f"{rider.user_name} ({rider.email})")

        session.flush()
        print_result("Total Riders", len(riders))

        if not ask_continue("Register Riders"):
            raise InterruptedError("User cancelled")

    try:
        # ============================================================
        # STEP 3: Pham Requests a Ride
        # ============================================================
        print_step_header(3, "PHAM REQUESTS A RIDE")

        pham = riders[0]
        destination = Location(latitude=43.65, longitude=-79.59)
        distance = pham.current_location.calculate_distance_in_km(destination)

        new_ride = Ride(
            rider=pham,
            start_location=pham.current_location,
            end_location=destination,
            distance=distance
        )
        new_ride.request_ride()

        ride_model = ride_repo.create_ride(session, new_ride)
        rider_repo.update_rider_current_ride(session, pham.user_id, new_ride.ride_id)
        session.flush()

        print_result("Ride ID", str(ride_model.ride_id))
        print_result("Ride Status", ride_model.ride_status.name)
        print_result("Distance (km)", f"{distance:.2f}")

        if not ask_continue("Request Ride"):
            raise InterruptedError("User cancelled")

        # ============================================================
        # STEP 4: Find Available Drivers
        # ============================================================
        print_step_header(4, "FIND AVAILABLE DRIVERS")

        available_drivers = driver_repo.find_available_drivers_within_radius(
            session,
            pham.current_location,
            radius_km=3.0
        )

        if not available_drivers:
            print("  No drivers within 3km. Expanding to 6km...")
            available_drivers = driver_repo.find_available_drivers_within_radius(
                session,
                pham.current_location,
                radius_km=6.0
            )

        print_result("Available Drivers Found", len(available_drivers))
        for i, (user_model, driver_model) in enumerate(available_drivers, 1):
            print(f" {i}. {user_model.user_name} (Available: {driver_model.is_available})")

        if not available_drivers:
            print("\n  No drivers available. Cancelling ride...")
            ride_repo.cancel_ride(session, str(ride_model.ride_id))
            rider_repo.update_rider_current_ride(session, pham.user_id, None)
            session.flush()
            raise InterruptedError("No drivers available")

        if not ask_continue("Find Drivers"):
            raise InterruptedError("User cancelled")

        # ============================================================
        # STEP 5: Assign Driver to Ride
        # ============================================================
        print_step_header(5, "ASSIGN DRIVER TO RIDE")

        # Pick first available driver
        assigned_user, assigned_driver = available_drivers[0]

        ride_repo.assign_driver(session, str(ride_model.ride_id), str(assigned_user.user_id))
        driver_repo.set_availability(session, str(assigned_user.user_id), False)
        driver_repo.update_driver_current_ride(session, str(assigned_user.user_id), str(ride_model.ride_id))
        session.flush()

        updated_ride = ride_repo.get_ride(session, str(ride_model.ride_id))

        print_result("Assigned Driver", assigned_user.user_name)
        print_result("Ride Status", updated_ride.ride_status.name)
        print_result("Driver Availability", "False (busy)")

        if not ask_continue("Assign Driver"):
            raise InterruptedError("User cancelled")

        # ============================================================
        # STEP 6: Start Ride
        # ============================================================
        print_step_header(6, "START RIDE (Driver picks up Rider)")

        ride_repo.start_ride(session, str(ride_model.ride_id))

        # Update driver location to pickup point
        start_point = to_shape(updated_ride.start_location)
        start_location = Location(latitude=start_point.y, longitude=start_point.x)
        user_repo.update_location(session, str(assigned_user.user_id), start_location)
        session.flush()

        started_ride = ride_repo.get_ride(session, str(ride_model.ride_id))

        print_result("Ride Status", started_ride.ride_status.name)
        print_result("Driver Location", f"Pickup point ({start_location.latitude}, {start_location.longitude})")

        if not ask_continue("Start Ride"):
            raise InterruptedError("User cancelled")

        # ============================================================
        # STEP 7: Complete Ride
        # ============================================================
        print_step_header(7, "COMPLETE RIDE (Reached destination)")

        ride_repo.complete_ride(session, str(ride_model.ride_id))

        # Update driver location to destination
        end_point = to_shape(updated_ride.end_location)
        end_location = Location(latitude=end_point.y, longitude=end_point.x)
        user_repo.update_location(session, str(assigned_user.user_id), end_location)

        # Clear current ride and set driver available
        rider_repo.update_rider_current_ride(session, pham.user_id, None)
        driver_repo.update_driver_current_ride(session, str(assigned_user.user_id), None)
        driver_repo.set_availability(session, str(assigned_user.user_id), True)
        session.flush()

        completed_ride = ride_repo.get_ride(session, str(ride_model.ride_id))
        final_driver = user_repo.get_driver(session, str(assigned_user.user_id))

        print_result("Ride Status", completed_ride.ride_status.name)
        print_result("Driver Location", f"Destination ({end_location.latitude}, {end_location.longitude})")
        print_result("Driver Availability", final_driver[1].is_available if final_driver else "N/A")

        if not ask_continue("Complete Ride"):
            raise InterruptedError("User cancelled")

        # ============================================================
        # STEP 8: Verify Final State
        # ============================================================
        print_step_header(8, "VERIFY FINAL STATE")

        rider_current = ride_repo.get_rider_current_ride(session, pham.user_id)
        rider_history = ride_repo.get_rider_rides_history(session, pham.user_id)

        print_result("Rider Has Active Ride", "YES" if rider_current else "NO")
        print_result("Rider Completed Rides", len(rider_history) if rider_history else 0)

        print("\n" + "-"*60)
        print("  ALL STEPS COMPLETED SUCCESSFULLY!")
        print("-"*60)

        # Ask user for final commit confirmation 
        final_confirm = input("\nCommit all changes to database? (yes/no): ").strip().lower()

        if final_confirm in ('yes', 'y'):
            session.commit()
            print("\n[SUCCESS] All changes COMMITTED to database!")
        else:
            raise InterruptedError("User chose not to commit")

    except InterruptedError as e:
        print(f"\n[ROLLBACK] {e}")
        print("[ROLLBACK] Rolling back all changes...")
        session.rollback()
        print("[ROLLBACK] Database unchanged.")

    except Exception as e:
        print(f"\n[ERROR] {e}")
        print("[ROLLBACK] Rolling back all changes...")
        session.rollback()
        import traceback
        traceback.print_exc()

    finally:
        session.close()
        print(f"\n[Session Closed] ID: {session_id}")
        logging.info("\n===================================================")
        logging.info("               SIMULATION COMPLETE               ")
        logging.info("===================================================")
        
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