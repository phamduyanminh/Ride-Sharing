# Mini Ride-Sharing Simulator

## Introduction and Project Overview
> **Note:** This document provides a comprehensive guide and structured plan for developing a mini ride-sharing simulator in Python. The objective is to create a simplified, in-memory simulation of core logic that powers ride services like Lyft or Uber. This project will focus on essential interactions between riders, drivers and the system that coordinates them, providing a solid foundation for understanding the complexities of real-world and large-scale distributed applications.

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
1. Euclidean Distance
   - Euclidean Distance measures the straightest and shortest path between two points.
2. Haversine 
   - Haversine measures the shortest distance between 2 points on a sphere using their latitudes and longtitudes measured along the surface.
