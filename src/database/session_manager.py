import logging
from contextlib import contextmanager
from src.database.models.base import get_session


logger = logging.getLogger(__name__)

@contextmanager
def session_scope():
    session = get_session()

    try:
        yield session
        session.commit()
        logger.debug("Session committed successfully.")
    except Exception as e:
        logger.error(f"An error occurred during session_scope: {e}")
        session.rollback()
        raise
    finally:
        session.close()