import uuid

# Convert string or UUID to UUID
def to_uuid(value) -> uuid.UUID:
    if value is None:
        return None
    if isinstance(value, uuid.UUID):
        return value
    return uuid.UUID(value)