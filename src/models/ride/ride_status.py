from enum import Enum

class RideStatus(Enum):
    NEW = "NEW"
    REQUESTED = "REQUESTED"
    PICKING_UP = "PICKING_UP"
    IN_TRIP = "IN_TRIP"
    CANCELLED = "CANCELLED"
    COMPLETED = "COMPLETED"