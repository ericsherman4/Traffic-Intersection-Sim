# Traffic Intersection Simulation and LiDAR Demo

Traffic Intersection Simulation built using python with VPython / GlowScript for graphics. LiDAR Demo is built using python and Pygame for graphics.

*This project was the final design project for ECE 1895 - Junior Design Fundamentals at the University of Pittsburgh. This README serves as the final report for this project.*

# Design Overview

The goal of this project was to explore simulating a 8-lane traffic intersection and implementing some vehicle behavior by giving vehicles some basic intelligence. The idea was to have some top level code to handle the spawning and de-spawning of vehicles and once placed into the simulation, each car would react to vehicles in front of it and also react to the traffic light. Another goal was to implement vehicles turning right / left at the intersection.

At a high level, we need the cars to be able to 'see' the traffic light. Which traffic light the car needs to check will depend on what lane the car is in. Therefore, the lanes need to distinct from each other and assigned some kind of identifier that the cars can use. The cars also need to know the car in front of its speed and also the distance to that car and the distance to the traffic light. From these requirements, two implementations were brainstormed when planning on how to tackle this:

## Queues
Each lane is implemented as a queue. For each index, we check index+1 (the car in front of the current car) and then can determine the distance to that car and that car's velocity. When the car is close to the intersection, we check the queue of the oncoming traffic for determining when the car can turn (yield left turn).

## Software LiDAR
This approach involved implementing a LiDAR that would shoot lines out in all directions on the x-y plane. The traffic light and other cars could all have bounding boxes (made up of lanes). Using line intersection formulas, we can see where the lines being shot out from the car intersect with bounding boxes of other objects. Then, we have the intersection point of the lines and the position of the car which can be used to determine the distance to that object. The queue implementation mentioned in the section above would still be used - this is just an alternate way of getting the cars speed and velocity without directly accessing it. This is a more realistic approach as autonomous vehicles cant just immediately determine the position and velocity of the cars around it. 

## Final Design
The final design omits the software LiDAR approach due to concerns about simulation performance. However, a demo of the software LiDAR was implemented using another graphics library named Pygame, which doubles tool for making video games in python.

Queues were actually omitted as well due to the lack of memory management features with the vpython graphics library (https://www.glowscript.org/docs/VPythonDocs/delete.html). As a result of this discovery, a ring buffer with start and end pointers was used instead. More on this implementation later.

The final design makes the use of object orientated programming, data structures, different algorithms and simulation concepts such as an implementation of an adaptive cruise control (ACC) algorithm (car controller), discretized PID controllers (backbone of ACC algorithm), and backward implicit Euler method (how the car updates its state). 

# Preliminary Design Verification
Because this was a software project, different features of the simulation were added incrementally and tested before moving on to implementing the next chunk of code. Having a visual piece in the project allows for easy visual verification of the different sections of code.

Throughout the design implementation, several issues arose such as the inability to delete graphics objects from memory. Most of these issues were discovered early on and these forced changes to the end architecture. These changes are highlighted below.

# Design Implementation

First, I will begin by just laying it all on the table, and then breaking it down piece by piece. The code structure and files are as follows: 

- vpython_sim
  - Simulation of the Traffic Intersection. This uses Vpython/Glowscript as the graphics library.
  - Files
    - [car.py](vpython_sim/car.py)
    - [carManager.py](vpython_sim/carManager.py)
    - [config.py](vpython_sim/config.py)
    - [env.py](vpython_sim/env.py)
    - [event.py](vpython_sim/event.py)
    - [gui_control.py](vpython_sim/gui_control.py)
    - [jup_note_code.py](vpython_sim/jup_note_code.py)
    - [lane.py](vpython_sim/lane.py)
    - [main.py](vpython_sim/main.py)
    - [pid.py](vpython_sim/pid.py)
    - [simulation.py](vpython_sim/simulation.py)
    - [trafficlight.py](vpython_sim/trafficlight.py)
    - [trafficlightManger.py](vpython_sim/trafficlightManger.py)
    - [TrafficIntersectionSim.ipynb](vpython_sim/TrafficIntersectionSim.ipynb)
- pygame_sim
  - Simulation of the Software LiDAR. This uses Pygame as the graphics library. 
    - [car.py](pygame_sim/car.py)
    - [config.py](pygame_sim/config.py)
    - [learning.py](pygame_sim/learning.py)
    - [main.py](pygame_sim/main.py)

All of the elements in the vpython simulation and where they fit in the hierarchy is highlighted in this diagram:

![pic](/software_diagram.drawio%20(5).png)


