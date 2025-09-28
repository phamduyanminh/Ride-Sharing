# Mini Ride-Sharing Simulator

## Introduction and Project Overview
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
> [!NOTE]
> - **Euclidean Distance:** Euclidean Distance measures the straightest and shortest path between two points.
> 
> - **Haversine:** Haversine measures the shortest distance between 2 points on a sphere using their latitudes and longtitudes measured along the surface.

Due to the reason the Euclidean Distance formula treats earth like a flat surface, it will leads to some significant errors. Therefore, the Haversine formula is the chosen method for the distance calculations in this project.

### Algorithms for Finding Available Nearby Drivers: Brute-Force vs Spatial Indexing
> [!NOTE]
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
   - **Attirbutes**: `current_location`
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

### TODO - FIX BUGS 
- Add feature: driver can cancel ride as well
- Write unit test
- Write integration (end-to-end) testing. Create user A, B, C -> drivers and D, E, F -> riders
- Docker: compose up/down (research about this)
- Research how to setup docker with PostGIS
- PostgesSQL should be placed in models -> implementing through ORM 

### Future Ideas:
- Integrate PostgreSQL or MySQL to save driver and rider information
- External spatial service (PostGis)
- External map service (path finding)
- Write APIs service (postman, automation test postman, newman can run postman through CI/CD) 
- Observability 
- Asynchronize 
- Real-time 