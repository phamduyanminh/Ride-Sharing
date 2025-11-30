# Mini Ride-Sharing Simulator

## Introduction and Project Overview
>
> This document provides a comprehensive guide and structured plan for developing a mini ride-sharing simulator in Python. The objective is to create a simplified, in-memory simulation of core logic that powers ride services like Lyft or Uber. This project will focus on essential interactions between riders, drivers and the system that coordinates them, providing a solid foundation for understanding the complexities of real-world and large-scale distributed applications.

## Core Features

1. User Registration
   - Onboard new users, designating them as driver or rider.
2. Location Management
   - Allow drivers and riders to update their location.
3. Proximity Search
   - Enable the system to find all available drivers within a specified radius of a rider.
4. Ride Request & Matching
   - Enable rider to request a trip and match them with a suitable, nearby driver.
5. Ride Status Management
   - Handle driver's decision to accept or decline a ride request.
6. Ride Lifecycle
   - Track the status of a ride from starting point to destination.
7. Tracking System
   - Provide a list of all currently active rides within the system.

## Algorithms

The main algorithm challenge in this ride-sharing project is efficiently finding nearby drivers based on rider's location. This involves 2 key steps:

1. Calculating the distance between 2 points, rider's location to driver's location.
2. Searching for all available drivers within a given radius.

### Algorithms for Distance Calculation: Euclidean Distance vs Haversine
>
> [!NOTE]
>
> - **Euclidean Distance:** Euclidean Distance measures the straightest and shortest path between two points.
> 
> - **Haversine:** Haversine measures the shortest distance between 2 points on a sphere using their latitudes and longtitudes measured along the surface.

Due to the reason the Euclidean Distance formula treats earth like a flat surface, it will leads to some significant errors. Therefore, the Haversine formula is the chosen method for the distance calculations in this project.

### Algorithms for Finding Available Nearby Drivers: Brute-Force vs Spatial Indexing
>
> [!NOTE]
>
> - **Brute-Force:** A Brute-Force search is the most basic way to find the nearest object. In Brute-Force search, you will find the distance from rider to every single available nearby driver in the system. Then it picks the on with the shortest distance.
> 
> - **Spatial Index:** Spatial Index is a technique used to efficiently store and retrieve spatial data like points, lines, and polygons based on the location. Instead of searching through all the data, a spatial index creates a map that helps quickly identify relevant data for a query, significantly speeding up spatial operations like finding all available drivers within a certain radius.

Brute-Force Search is simple to implement; however, it will become very slow as the number of drivers increases. Meanwhile, Spatial Index method remains fast even if you have many drivers. Therefore, Spatial Index is the chosen method for the finding available nearby drivers.


## System Design

### Entities
Our project system will have 4 main entities. Each represent a Python class:

- `User`: The base enity hold common information of the app users.
  - **Attributes**: `user_id`, `email`, `user_name`
- `Rider`: A user who requests a ride. This class inherits from `User` class.
  - **Attributes**: `current_location`
- `Driver`: A user who provides riding service. This class inherits from `User` class.
  - **Attributes**: `current_location`, `is_available`
- `Ride`: Represent a trip from starting point to destination. This entity will connect with `Rider` and `Driver`.
  - **Attributes**: `ride_id`, `rider`, `driver`, `start_location`, `end_location`, `status` ("`new`", "`requested`", "`in_progress`", "`cancelled`", "`completed`")

### Entity Relationships

This entity relationships define how entites interact with each other in the project.

- `User` -> `Rider`/`Driver`:
  - A `Rider` is a `User`
  - A `Driver` is a `User`

- `Ride` -> `Rider` & `Driver`:
  - A `Ride` has one `Rider`
  - A `Ride` has one `Driver`

- A `Rider` can has many `Ride`
- A `Driver` can has many `Ride`


### Activate Python environment

- `.\.venv\Scripts\Activate.ps1`

### Start and run the docker-compose

- Start the docker-compose in detached mode: `docker-compose up -d`
- Run test-case step-by-step: `docker-compose run app`
- Run test-case step-by-step without user input: `docker-compose run -d -e AUTO_CONTINUE=true app`
- Stop the docker-compose: `docker-compose down`
- Stop the docker-compose and remove all data: `docker-compose down -v`

### SQL information

- username: postgres
- password: bunz3120
- database: ride_sharing

### Basics SQL Shell commands

- `\l` - List all databases
- `\c <database_name>` - Connect to a database
- `\dt` - List all tables
- `\d <table_name>` - Describe a table
- `CREATE DATABASE <database_name>;` - Create a database
- `DROP DATABASE <database_name>;` - Drop a database
- `\q` - Quit

### Access DB via Docker CLI/Terminal

- Access the databse in docker-compose: `docker exec -it ride_sharing_postgres psql -U postgres -d ride_sharing`
- See all created rides: `SELECT ride_id, ride_status, distance_km FROM rides;`
- See all created users: `SELECT user_name, user_type FROM users;`
- See information of drivers:
  `SELECT 
      u.user_id,
      u.email,
      u.user_name,
      u.user_type,
      ST_X(u.current_location) AS longitude,
      ST_Y(u.current_location) AS latitude,
      ST_AsText(u.current_location) AS location_wkt,
      u.created_at,
      u.updated_at,
      d.is_available,
      d.current_ride_id
  FROM users u
  JOIN drivers d ON u.user_id = d.user_id
  ORDER BY u.user_name;`
- See information of riders:
  `SELECT 
      u.user_id,
      u.email,
      u.user_name,
      u.user_type,
      ST_X(u.current_location) AS longitude,
      ST_Y(u.current_location) AS latitude,
      ST_AsText(u.current_location) AS location_wkt,
      u.created_at,
      u.updated_at,
      r.current_ride_id
  FROM users u
  JOIN riders r ON u.user_id = r.user_id
  ORDER BY u.user_name;
  ride_sharing=# SELECT 
      u.user_id,
      u.email,
      u.user_name,
      u.user_type,
      ST_X(u.current_location) AS longitude,
      ST_Y(u.current_location) AS latitude,
      ST_AsText(u.current_location) AS location_wkt,
      u.created_at,
      u.updated_at,
      r.current_ride_id
  FROM users u
  JOIN riders r ON u.user_id = r.user_id
  ORDER BY u.user_name;`
- See history ride of a rider: 
  `SELECT 
      r.ride_id,
      r.ride_status,
      r.distance_km,
      r.created_at,
      u_driver.user_name AS driver_name
  FROM rides r
  JOIN users u_rider ON r.rider_id = u_rider.user_id
  LEFT JOIN users u_driver ON r.driver_id = u_driver.user_id
  WHERE u_rider.user_name = 'Pham'
  ORDER BY r.created_at DESC;`

### TODO

- [X] Write unit test
- [ ] Write integration (end-to-end) testing. Create user A, B, C -> drivers and D, E, F -> riders
- [X] Docker: compose up/down (research about this)
- [X] Research how to setup docker with PostGIS
- [X] PostgesSQL should be placed in models -> implementing through ORM 
- [X] Move all logic into database (request ride, update ride, cancel ride)
- [ ] Each step in the simulation should be processed by user's input as enter
- [ ] Setup debugging environment
- [ ] Session should be able to either commit or rollback based on the entire request status (success or failure)
  - [ ] Each request should have its own session
  - [ ] Each session should have a database transaction

### Future Implementations

- External spatial service (PostGis)
- External map service (path finding)
- Write APIs service (postman, automation test postman, newman can run postman through CI/CD)
- Observability
- Asynchronize
- Real-time
