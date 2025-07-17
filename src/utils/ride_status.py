from enum import Enum

class RideStatus(Enum):
    NEW = "New"
    REQUESTED = "Requested"
    PICKING_UP = "Picking Up"
    IN_TRIP = "In Trip"
    CANCELLED = "Cancelled"
    COMPLETED = "Completed"