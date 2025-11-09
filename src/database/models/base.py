import os
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from src.database.config.config import config

Base = declarative_base()
_engine = None

# Create a db engine from config
def get_engine():
    global _engine

    if _engine is None:
        database_url = os.getenv('DATABASE_URL')

        if database_url:
              print("Docker mode...")
              _engine = create_engine(database_url, echo=True)
        else:
            print("Local mode...")
            params = config()
            connection_string = (
                f"postgresql://{params['user']}:{params['password']}"
                f"@{params['host']}:{params['port']}/{params['database']}"
            )
            _engine = create_engine(connection_string, echo=True)

    return _engine

# Create db session
def get_session():
    engine = get_engine()
    Session = sessionmaker(bind=engine)
    return Session()

