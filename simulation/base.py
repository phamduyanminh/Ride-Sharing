import logging
from abc import ABC, abstractmethod
from geoalchemy2.shape import to_shape


from src.database.models.base import get_session, init_database
from src.database.models.user_model import UserModel, UserTypeEnum
from src.database.repositories.user_repository import UserRepository
from src.database.repositories.driver_repository import DriverRepository
from src.database.repositories.rider_repository import RiderRepository
from src.database.repositories.ride_repository import RideRepository
from src.models.users.rider import Rider


# Shared session management
_shared_session = None
_shared_session_id = None

# Get shared session for all simulations
def get_shared_session():
    global _shared_session, _shared_session_id
    if _shared_session is None:
        init_database()
        _shared_session = get_session()
        _shared_session_id = id(_shared_session)
        print(f"[Session Created] ID: {_shared_session_id}")
    return _shared_session


# Close shared session
def close_shared_session():
    global _shared_session, _shared_session_id
    if _shared_session is not None:
        _shared_session.close()
        print(f"[Session Closed] ID: {_shared_session_id}")
        _shared_session = None
        _shared_session_id = None


def print_step_header(step_num: int, title: str):
    print(f"\n{'='*60}")
    print(f"  STEP {step_num}: {title}")
    print(f"{'='*60}")


def print_result(label: str, value):
    print(f"  -> {label}: {value}")


def ask_continue(step_name: str) -> bool:
    while True:
        response = input(f"\n[Step {step_name} completed. Continue to next step? (y/n)]").strip().lower()
        if response in ('yes', 'y'):
            return True
        elif response in ('no', 'n'):
            return False
        else:
            print("Invalid input. Please enter 'y' or 'n'.")


# Check if there are existing drivers in the database
def has_existing_data(session) -> bool:
    count = session.query(UserModel).filter_by(user_type=UserTypeEnum.driver).count()
    return count > 0


# Load existing riders from database
def load_existing_riders(session) -> list[Rider]:
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
    return riders


# Base simulation class
class BaseSimulation(ABC):
    name: str = "Base Simulation"

    def __init__(self):
        self.user_repo = UserRepository()
        self.driver_repo = DriverRepository()
        self.rider_repo = RiderRepository()
        self.ride_repo = RideRepository()
        self.session = get_shared_session()

    @abstractmethod
    def run(self) -> bool:
        pass


    def execute(self) -> bool:
        """Run the simulation with proper logging."""
        logging.info("=" * 50)
        logging.info(f"       {self.name.upper()}       ")
        logging.info("=" * 50)

        print(f"\n{'='*60}")
        print(f"  RUNNING: {self.name}")
        print(f"{'='*60}")

        try:
            success = self.run()
            if success:
                logging.info(f"       {self.name} COMPLETED       ")
            return success
        except InterruptedError as e:
            print(f"\n[CANCELLED] {e}")
            print("[ROLLBACK] Rolling back changes...")
            self.session.rollback()
            print("[ROLLBACK] Database unchanged.")
            return False
        except Exception as e:
            print(f"\n[ERROR] {e}")
            print("[ROLLBACK] Rolling back changes...")
            self.session.rollback()
            import traceback
            traceback.print_exc()
            return False