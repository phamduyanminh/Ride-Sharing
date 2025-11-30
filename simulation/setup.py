from simulation.base import (
    BaseSimulation,
    print_step_header,
    print_result,
    ask_continue,
    has_existing_data
)
from src.models.users.driver import Driver
from src.models.users.rider import Rider


class SetupSimulation(BaseSimulation):
    """Setup: Register drivers and riders before running simulations."""

    name = "Initial Setup (Register Users)"

    def __init__(self):
        super().__init__()
        self.registered_riders = []

    def run(self) -> bool:
        """Register drivers and riders. Returns True if setup successful."""

        if has_existing_data(self.session):
            print("\n[INFO] Existing data found in database.")
            print("[INFO] Skipping registration - using existing users.")
            return True

        print("\n[INFO] No existing data found. Starting registration...")

        # Register Drivers
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
            self.user_repo.create_driver(self.session, driver)
            print_result("Registered Driver", f"{driver.user_name} ({driver.email})")

        self.session.flush()
        print_result("Total Drivers", len(drivers))

        if not ask_continue("Register Drivers"):
            raise InterruptedError("User cancelled during driver registration")

        # Register Riders
        print_step_header(2, "REGISTER RIDERS")

        riders = [
            Rider(email="tr1@email.com", user_name="Pham", longitude=-79.65, latitude=43.60),
            Rider(email="tr2@email.com", user_name="Fam", longitude=-79.62, latitude=43.59)
        ]

        for rider in riders:
            self.user_repo.create_rider(self.session, rider)
            print_result("Registered Rider", f"{rider.user_name} ({rider.email})")

        self.session.flush()
        print_result("Total Riders", len(riders))

        if not ask_continue("Register Riders"):
            raise InterruptedError("User cancelled during rider registration")

        # Commit the registration
        confirm = input("\nCommit user registration to database? (y/n): ").strip().lower()
        if confirm in ('yes', 'y'):
            self.session.commit()
            print("\n[SUCCESS] Users registered and committed to database!")
            return True
        else:
              raise InterruptedError("User chose not to commit registration")