import logging

from simulation.base import (
    BaseSimulation,
    print_step_header,
    print_result,
    ask_continue,
    load_existing_riders
)
from src.models.location.location import Location
from src.models.ride.ride import Ride


class RideCancelationSimulation(BaseSimulation):
    """Scenario 2: Rider requests a ride then cancels it."""

    name = "Rider Cancels Ride Simulation"

    def run(self) -> bool:
        riders = load_existing_riders(self.session)
        if len(riders) < 2:
            print("[ERROR] Need at least 2 riders. Run setup first.")
            return False

        fam = riders[1]

        # STEP 1: Fam Requests a Ride
        print_step_header(1, f"{fam.user_name.upper()} REQUESTS A RIDE")

        destination = Location(latitude=43.7, longitude=-79.7)
        distance = fam.current_location.calculate_distance_in_km(destination)

        new_ride = Ride(
            rider=fam,
            start_location=fam.current_location,
            end_location=destination,
            distance=distance
        )
        new_ride.request_ride()

        ride_model = self.ride_repo.create_ride(self.session, new_ride)
        self.rider_repo.update_rider_current_ride(self.session, fam.user_id, new_ride.ride_id)
        self.session.flush()

        print_result("Ride ID", str(ride_model.ride_id))
        print_result("Ride Status", ride_model.ride_status.name)
        print_result("Distance (km)", f"{distance:.2f}")

        if not ask_continue("Request Ride"):
            raise InterruptedError("User cancelled")

        # STEP 2: Find and Assign Driver
        print_step_header(2, "FIND AND ASSIGN DRIVER")

        available_drivers = self.driver_repo.find_available_drivers_within_radius(
            self.session,
            fam.current_location,
            radius_km=6.0
        )

        if not available_drivers:
            print("  No drivers available. Nothing to cancel.")
            self.ride_repo.cancel_ride(self.session, str(ride_model.ride_id))
            self.rider_repo.update_rider_current_ride(self.session, fam.user_id, None)
            self.session.flush()
            return True

        assigned_user, assigned_driver = available_drivers[0]

        self.ride_repo.assign_driver(self.session, str(ride_model.ride_id), str(assigned_user.user_id))
        self.driver_repo.set_availability(self.session, str(assigned_user.user_id), False)
        self.driver_repo.update_driver_current_ride(self.session, str(assigned_user.user_id), str(ride_model.ride_id))
        self.session.flush()

        print_result("Assigned Driver", assigned_user.user_name)
        print_result("Driver is on the way", "...")

        if not ask_continue("Assign Driver"):
            raise InterruptedError("User cancelled")

        # STEP 3: Rider Cancels the Ride
        print_step_header(3, f"{fam.user_name.upper()} CANCELS THE RIDE")

        print(f"\n  ...Oh no, {fam.user_name} needs to cancel the ride!...")

        self.ride_repo.cancel_ride(self.session, str(ride_model.ride_id))
        self.rider_repo.update_rider_current_ride(self.session, fam.user_id, None)
        self.driver_repo.update_driver_current_ride(self.session, str(assigned_user.user_id), None)
        self.driver_repo.set_availability(self.session, str(assigned_user.user_id), True)
        self.session.flush()

        # Verify final state
        cancelled_ride = self.ride_repo.get_ride(self.session, str(ride_model.ride_id))
        final_driver = self.user_repo.get_driver(self.session, str(assigned_user.user_id))

        print_result("Ride Status", cancelled_ride.ride_status.name)
        print_result(f"Is {assigned_user.user_name} available now?", final_driver[1].is_available if final_driver else "N/A")

        print("\n" + "-"*60)
        print("  RIDER CANCELLATION COMPLETED!")
        print("-"*60)

        # Final commit confirmation
        final_confirm = input("\nCommit all changes to database? (y/n): ").strip().lower()

        if final_confirm in ('yes', 'y'):
            self.session.commit()
            print("\n[SUCCESS] All changes COMMITTED to database!")
            return True
        else:
            raise InterruptedError("User chose not to commit")