import os
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import create_database, database_exists


from src.database.config.config import config


Base = declarative_base()
_engine = None

ENGINE_CONFIG = {
    'echo': True,
    'pool_size': 5,
    'max_overflow': 10,
    'pool_timeout': 30,
    'pool_recycle': 3600,
    'pool_pre_ping': True,
}

# Create a db engine from config
def get_engine():
    global _engine

    if _engine is None:
        database_url = os.getenv('DATABASE_URL')

        if database_url:
              print("Docker mode...")
              _engine = create_engine(
                database_url, 
                **ENGINE_CONFIG
                )
        else:
            print("Local mode...")
            params = config()
            connection_string = (
                f"postgresql://{params['user']}:{params['password']}"
                f"@{params['host']}:{params['port']}/{params['database']}"
            )
            _engine = create_engine(
                connection_string, 
                **ENGINE_CONFIG
                )

    return _engine

# Create db session
def get_session():
    engine = get_engine()
    Session = sessionmaker(bind=engine)
    return Session()

# Initialize database
def init_database():
    database_url = os.getenv('DATABASE_URL')

    if database_url:
        url = database_url
    else:
        params = config()
        url = (
            f"postgresql://{params['user']}:{params['password']}"
            f"@{params['host']}:{params['port']}/{params['database']}"
        )

    # Create database if it doesn't exist
    if not database_exists(url):
        print("[INIT] Database does not exist. Creating...")
        create_database(url)
        print("[INIT] Database created successfully.")
    else:
        print("[INIT] Database already exists.")

    # Get engine and create PostGIS extension + tables
    engine = get_engine()

    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis"))
        conn.commit()
        print("[INIT] PostGIS extension enabled.")
    
    from src.database.models.user_model import UserModel
    from src.database.models.driver_model import DriverModel
    from src.database.models.rider_model import RiderModel
    from src.database.models.ride_model import RideModel

    Base.metadata.create_all(engine)
    print("[INIT] All tables created/verified.")