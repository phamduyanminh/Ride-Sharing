CREATE DATABASE ride_sharing;
CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TYPE user_type AS ENUM ('driver', 'rider');
CREATE TYPE ride_status AS ENUM ('NEW', 'REQUESTED', 'PICKING_UP', 'IN_TRIP', 'COMPLETED', 'CANCELLED');

-- Users table (base for both drivers and riders)
CREATE TABLE users (
    user_id UUID PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    user_name VARCHAR(100) NOT NULL,
    user_type user_type NOT NULL,
    current_location GEOMETRY(POINT, 4326),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Drivers table (extends users)
CREATE TABLE drivers (
    user_id UUID PRIMARY KEY REFERENCES users(user_id) ON DELETE CASCADE,
    is_available BOOLEAN DEFAULT TRUE,
    current_ride_id UUID
);

-- Riders table (extends users)
CREATE TABLE riders (
    user_id UUID PRIMARY KEY REFERENCES users(user_id) ON DELETE CASCADE,
    current_ride_id UUID
);

-- Rides table
CREATE TABLE rides (
    ride_id UUID PRIMARY KEY,
    rider_id UUID NOT NULL REFERENCES users(user_id),
    driver_id UUID REFERENCES users(user_id),
    ride_status ride_status DEFAULT 'NEW',
    start_location GEOMETRY(POINT, 4326) NOT NULL,
    end_location GEOMETRY(POINT, 4326) NOT NULL,
    distance_km DECIMAL(10, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create spatial indexes 
CREATE INDEX idx_users_location ON users USING GIST (current_location);
CREATE INDEX idx_rides_start_location ON rides USING GIST (start_location);
CREATE INDEX idx_rides_end_location ON rides USING GIST (end_location);

-- Create regular indexes
CREATE INDEX idx_drivers_available ON drivers (is_available);
CREATE INDEX idx_rides_status ON rides (ride_status);
CREATE INDEX idx_rides_rider ON rides (rider_id);
CREATE INDEX idx_rides_driver ON rides (driver_id);