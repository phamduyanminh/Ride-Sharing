from geoalchemy2.shape import to_shape

from simulation.base import (
    BaseSimulation,
    print_step_header,
    print_result,
    ask_continue,
    load_existing_riders
)
from src.models.location.location import Location
from src.models.ride.ride import Ride


class RideCompletionSimulation(BaseSimulation):
    """Scenario 1: Full ride lifecycle from request to completion."""

    name = "Ride Completion Simulation"

    def run(self) -> bool:
        riders = load_existing_riders(self.session)
        if not riders:
            print("[ERROR] No riders found in database. Run setup first.")
            return False

        pham = riders[0]

        # STEP 1: Pham Requests a Ride
        print_step_header(1, "PHAM REQUESTS A RIDE")

        destination = Location(latitude=43.65, longitude=-79.59)
        distance = pham.current_location.calculate_distance_in_km(destination)

        new_ride = Ride(
            rider=pham,
            start_location=pham.current_location,
            end_location=destination,
            distance=distance
        )
        new_ride.request_ride()

        ride_model = self.ride_repo.create_ride(self.session, new_ride)
        self.rider_repo.update_rider_current_ride(self.session, pham.user_id, new_ride.ride_id)
        self.session.flush()

        print_result("Ride ID", str(ride_model.ride_id))
        print_result("Ride Status", ride_model.ride_status.name)
        print_result("Distance (km)", f"{distance:.2f}")

        if not ask_continue("Request Ride"):
            raise InterruptedError("User cancelled")

        # STEP 2: Find Available Drivers
        print_step_header(2, "FIND AVAILABLE DRIVERS")

        available_drivers = self.driver_repo.find_available_drivers_within_radius(
            self.session,
            pham.current_location,
            radius_km=3.0
        )

        if not available_drivers:
            print("  No drivers within 3km. Expanding to 6km...")
            available_drivers = self.driver_repo.find_available_drivers_within_radius(
                self.session,
                pham.current_location,
                radius_km=6.0
            )

        print_result("Available Drivers Found", len(available_drivers))
        for i, (user_model, driver_model) in enumerate(available_drivers, 1):
            print(f"  {i}. {user_model.user_name} (Available: {driver_model.is_available})")

        if not available_drivers:
            print("\n  No drivers available. Cancelling ride...")
            self.ride_repo.cancel_ride(self.session, str(ride_model.ride_id))
            self.rider_repo.update_rider_current_ride(self.session, pham.user_id, None)
            self.session.flush()
            raise InterruptedError("No drivers available")

        if not ask_continue("Find Drivers"):
            raise InterruptedError("User cancelled")

        # STEP 3: Assign Driver to Ride
        print_step_header(3, "ASSIGN DRIVER TO RIDE")

        assigned_user, assigned_driver = available_drivers[0]

        self.ride_repo.assign_driver(self.session, str(ride_model.ride_id), str(assigned_user.user_id))
        self.driver_repo.set_availability(self.session, str(assigned_user.user_id), False)
        self.driver_repo.update_driver_current_ride(self.session, str(assigned_user.user_id), str(ride_model.ride_id))
        self.session.flush()

        updated_ride = self.ride_repo.get_ride(self.session, str(ride_model.ride_id))

        print_result("Assigned Driver", assigned_user.user_name)
        print_result("Ride Status", updated_ride.ride_status.name)
        print_result("Driver Availability", "False (busy)")

        if not ask_continue("Assign Driver"):
            raise InterruptedError("User cancelled")

        # STEP 4: Start Ride
        print_step_header(4, "START RIDE (Driver picks up Rider)")

        self.ride_repo.start_ride(self.session, str(ride_model.ride_id))

        start_point = to_shape(updated_ride.start_location)
        start_location = Location(latitude=start_point.y, longitude=start_point.x)
        self.user_repo.update_location(self.session, str(assigned_user.user_id), start_location)
        self.session.flush()

        started_ride = self.ride_repo.get_ride(self.session, str(ride_model.ride_id))

        print_result("Ride Status", started_ride.ride_status.name)
        print_result("Driver Location", f"Pickup point ({start_location.latitude}, {start_location.longitude})")

        if not ask_continue("Start Ride"):
            raise InterruptedError("User cancelled")

        # STEP 5: Complete Ride
        print_step_header(5, "COMPLETE RIDE (Reached destination)")

        self.ride_repo.complete_ride(self.session, str(ride_model.ride_id))

        end_point = to_shape(updated_ride.end_location)
        end_location = Location(latitude=end_point.y, longitude=end_point.x)
        self.user_repo.update_location(self.session, str(assigned_user.user_id), end_location)

        self.rider_repo.update_rider_current_ride(self.session, pham.user_id, None)
        self.driver_repo.update_driver_current_ride(self.session, str(assigned_user.user_id), None)
        self.driver_repo.set_availability(self.session, str(assigned_user.user_id), True)
        self.session.flush()

        completed_ride = self.ride_repo.get_ride(self.session, str(ride_model.ride_id))
        final_driver = self.user_repo.get_driver(self.session, str(assigned_user.user_id))

        print_result("Ride Status", completed_ride.ride_status.name)
        print_result("Driver Location", f"Destination ({end_location.latitude}, {end_location.longitude})")
        print_result("Driver Availability", final_driver[1].is_available if final_driver else "N/A")

        if not ask_continue("Complete Ride"):
            raise InterruptedError("User cancelled")

        # STEP 6: Verify Final State
        print_step_header(6, "VERIFY FINAL STATE")

        rider_current = self.ride_repo.get_rider_current_ride(self.session, pham.user_id)
        rider_history = self.ride_repo.get_rider_rides_history(self.session, pham.user_id)

        print_result("Rider Has Active Ride", "YES" if rider_current else "NO")
        print_result("Rider Completed Rides", len(rider_history) if rider_history else 0)

        print("\n" + "-"*60)
        print("  ALL STEPS COMPLETED SUCCESSFULLY!")
        print("-"*60)

        # Final commit confirmation
        final_confirm = input("\nCommit all changes to database? (y/n): ").strip().lower()

        if final_confirm in ('yes', 'y'):
            self.session.commit()
            print("\n[SUCCESS] All changes COMMITTED to database!")
            return True
        else:
            raise InterruptedError("User chose not to commit")