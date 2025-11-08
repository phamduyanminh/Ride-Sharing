import logging
from contextlib import contextmanager
from sqlalchemy.orm import Session
from src.database.models.base import get_session


@contextmanager
def session_scope():
    session = get_session()

    try:
        yield session
        session.commit()
    except Exception:
        logging.info(f"An error occurred during session_scope: {Exception}")
        session.rollback()
        raise
    finally:
        session.close()