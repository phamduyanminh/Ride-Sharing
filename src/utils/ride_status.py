from enum import Enum

class RideStatus(Enum):
    NONE = "None"
    REQUESTED = "Requested"
    IN_PROGRESS = "In Progress"
    CANCELLED = "Cancelled"
    COMPLETED = "Completed"