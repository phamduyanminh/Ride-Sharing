from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from src.database.config.config import config

Base = declarative_base()

# Create a db engine from config
def get_engine():
    params = config()
    connection_string = (
        f"postgresql://{params['user']}:{params['password']}"
        f"@{params['host']}:{params['port']}/{params['database']}"
    )
    return create_engine(connection_string, echo=True)

# Create db session
def get_session():
    engine = get_engine()
    Session = sessionmaker(bind=engine)
    return Session()

