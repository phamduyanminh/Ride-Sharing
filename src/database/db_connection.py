import psycopg2
from src.database.config.config import config

def connect():
    connection = None 
    try:
        params = config()
        print("Connecting to postgreSQL database...")
        connection = psycopg2.connect(**params)
        
        # Create a cursor object
        cursor = connection.cursor()
        print("PostgreSQL database version:")
        cursor.execute('Select version()')

        db_version = cursor.fetchone()
        print(db_version)
        
        # Close the cursor
        cursor.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if connection is not None:
            connection.close()
            print("Database connection closed.")
        
connect()