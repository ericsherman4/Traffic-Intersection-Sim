# Traffic Intersection Simulation and LiDAR Demo

Traffic Intersection Simulation built using python with VPython / GlowScript for graphics. LiDAR Demo is built using python and Pygame for graphics. An [anaconda distribution of python](https://www.anaconda.com/) and [conda environments](https://docs.conda.io/en/latest/) were used for this simulation.

*This project was the final design project for ECE 1895 - Junior Design Fundamentals at the University of Pittsburgh. This README serves as the final report for this project.*

## INSERT VIDEOS HERE, ADD NIGHT MODE VIDEO

# Design Overview

The goal of this project was to explore simulating a 8-lane traffic intersection and implementing some vehicle behavior by giving vehicles some basic intelligence. The idea was to have some top level code to handle the spawning and de-spawning of vehicles and once placed into the simulation, each car would react to vehicles in front of it and also react to the traffic light. Another goal was to implement vehicles turning right / left at the intersection.

At a high level, we need the cars to be able to 'see' the traffic light. Which traffic light the car needs to check will depend on what lane the car is in. Therefore, the lanes need to be distinct from each other and assigned some kind of identifier that the cars can use. The cars also need to know the car in front of its speed and also the distance to that car and the distance to the traffic light. From these requirements, two implementations were brainstormed during planning:

## Queues
Each lane is implemented as a queue. For each index, we check index+1 (the car in front (car A) of the current car (car B)) and then can get the distance to car A and car A's velocity. When the car is close to the intersection, we check the queue of the oncoming traffic for determining when the car can turn (yield left turn).

## Software LiDAR
This approach involved implementing a LiDAR that would shoot lines out in all directions on the x-y plane. The traffic light and other cars could all have bounding boxes (made up of lines). Using line intersection formulas, we can see where the lines being shot out from the car intersect with bounding boxes of other objects. Then, we have the intersection point of the lines and the position of the car which can be used to determine the distance to that object. The queue implementation mentioned in the section above would still be used - this is just an alternate way of getting the cars speed and velocity without directly accessing it. This is a more realistic approach as autonomous vehicles cant just immediately determine the position and velocity of the cars around it. 

## Final Design
The final design omits the software LiDAR approach due to concerns about simulation performance. However, a demo of the software LiDAR was implemented using another graphics library named Pygame, which doubles as a tool for creating video games in python.

Queues were actually omitted as well due to the lack of memory management features with the vpython graphics library (https://www.glowscript.org/docs/VPythonDocs/delete.html). As a result of this discovery, a ring buffer with start and end pointers was used instead. More on this implementation later.

The final design makes the use of object orientated programming, data structures, different algorithms and simulation concepts such as an implementation of an adaptive cruise control (ACC) algorithm (car controller), discretized PID controllers (backbone of ACC algorithm), and backward implicit Euler method (how the car updates its state). 

# Preliminary Design Verification
Because this was a software project, different features of the simulation were added incrementally and tested before moving on to implementing the next chunk of code. Having a visual piece in the project allows for easy visual verification of the different sections of code.

Throughout the design implementation, several issues arose such as the inability to delete graphics objects from memory. Most of these issues were discovered early on and these forced changes to the end architecture. These changes are highlighted below.

# Design Implementation & Testing

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

All of the elements in the vpython simulation and where they fit in the hierarchy is highlighted in the following diagram. The diagram also contains a description of the classes. It is recommend to read the class descriptions to get a better understanding of the code structure.

*Click the image to open high-res version.*
![pic](/report/software_diagram.drawio%20(5).png)

## Vpython Simulation Deep Dive

### Jupyter Notebook 

For most of the development for the Vpython simulation, Jupyter Notebook was used. Vpython has been implemented to work well in Jupyter Notebook and the framework provided makes it easy to rapidly run and test code verses running it outside of a notebook. However, there are some pit falls that I have noticed with this approach and that is inconsistencies with the simulation behavior, even with the exact same code being run. As an example, the rate() call (sets a limit on many times a loop can run per second) sometimes wasn't properly triggering which results in the simulation completing within less than a second. There were also  weird memory behavior with the priority queue class. This eventually led to moving away from using Jupyter Notebook. The Vpython library supports this by creating a local web server to display the graphics. This resulted in significantly better results. 

The Jupyter Notebook code to run the simulation looked like this:

Cell 1
```
# NEED TO RUN THIS CELL BEFORE RUNNING CELL BELOW FOR THE FIRST TIME
# ONLY NEED TO RUN THIS CELL ONCE (OR EVERYTIME KERNAL IS RESET)
# https://ipython.org/ipython-doc/3/config/extensions/autoreload.html
# https://stackoverflow.com/questions/54923554/jupyter-class-in-different-notebook
%load_ext autoreload
%autoreload 2
```
Cell 2
```
%reload_ext autoreload

from main import *
sim_main()
```

This code used some Jupyter Notebook directives to reload external libraries every time they were changed. Then it called the main simulation function.

The new approach was to create a normal python file with the code that is in the cell 2 above. This file, jup_note_code.py, was then used to call the sim_main(). Obviously this approach lacks some nice code control that Jupyter Notebook offered. Therefore, gui_control.py was created, which gives me the ability to pause and resume the simulation, and to quit the simulation (simply closing the tab or calling exit() doesn't work well because it doesn't close the web server and keeps the code hanging.)

### High Level Code Description

As seen from the diagram, the code is comprised of several nested objects. The intention was to give each level in the hierarchy different types of control. For example, we have the car class which should just be responsible for the looks of the vehicles and the vehicles kinematics. However, a higher level controller was needed to coordinate all of these vehicles.The car manager was born for this purpose. However, as mentioned above, there needs to be some way for cars to identify the lane that they are currently in. Hence, I created a lane class which has a finer grain of control over cars than the car manager. The lane class feeds each individual car in the simulation with information about other cars such as the distance to nearest obstacle, velocity of the car in front, etc. The car manager has higher level functionality and its main purpose is to control multiple instances of the lane class. It handles simulation events related to car objects and moving cars between lanes. 

The same train of thought was applied for the traffic lights. Once the class for the traffic light was made, I need something to coordinate these traffic lights. The traffic light manager class was born to remedy this; it has the ability to generate events for a specific traffic light to change its color. The simulation class then pops these events off of the global queue when the simulation time is greater than the event time stamp. This global queue is also shared with the car manager which generates events related to car objects such as when to spawn in a car and when they should turn. 

### Implementation Steps
*Pulled from commit history; text is slightly modified.*

1. Work on the map (ground, roads (no lane lines), and the traffic light).
2. Infrastructure and class organization. Instead of writing all the code in Jupyter Notebook cells, did research how to implement code in files outside of the notebook, and then have this code loaded into Jupyter Notebook. This let me use Visual Studio Code to write code in which provides much easier navigation through the code. 
3. Finished traffic light and implemented a state machine based on timers internal to the class. 
4. Added road lines.
5. Work in progress on car manager class, lane class, and car class state machine. 
6. Cars can now move on the road at constant velocity. 
7. Changed simulation time variable from milliseconds to seconds and work in progress on the car state machine. 
8. Implemented car deceleration using a map function when it detects other cars (untested). (More on this later.)
9. Created event class and traffic light manager.
10. Revamped traffic light class to be event driven. 
11. Continued to work on car deceleration but it barely works and wasn't robust enough. 
12. Implemented adaptive cruise control algorithm (modified PID controller). Cars seem to respond to other cars and the traffic light.
13. Fixed bug where cars would respond to the traffic light even though they passed it, cars respond better to yellow light (decide whether to stop or continue based on speed / distance), cars respond to other cars working in all lanes now.
14.  Added car events to generate cars and played around with lighting and the environment settings.
15.  Added random max acceleration, deceleration, start speed, and max speed. Tuned PID controller.
16.  Major code clean up and bug fixes.
17.  Clean up of traffic light manager.
18.  Prototype of turning action done. 
19.  Single case of turning from lane 0 works. 
20.  Two turns from lane 0 works.
21.  Lane 0 turning  with cars in both 0 and 7 working. 
22.  Fixed camera view and bug fix with car reset() working.
23.  Reorganized repo, tuning and clean up.
24.  Added pause, resume, and kill command for vpython simulation. Moving away from Jupyter Notebook. 
25.  Removed ignored files from cache.


### Controlling the Car's Speed and Acceleration

After doing some math calculations, I devised control based on a map function (to map one range of values to another range of values). I would be mapping the change in the distance between two cars from the range of some offset to some safe value to the range of 0 to the max deceleration. When the change in distance between the two cars is high (representing the car rapidly approaching the car in front of it), then the deceleration value would be high. I would also be dynamically feeding the map function a different safe value based on the cars speed. This approach was naive and didn't work very well. For one, I was feeding the change in distance between two cars. If the trailing car was very close to the lead car and they were both going constant velocities, then the change in distance wouldn't change and so the cars wouldn't space out as they should when traveling higher speeds. Additionally, this function only decelerated the car, so there were holes in the logic for figuring out when the cars should be accelerating. 

This is when I pivoted to looking into adaptive cruise control (ACC) implementations as this is essentially what I was trying to make. This is when I ran into this masters thesis: [Design and Implementation of an Adaptive Cruise Control Algorithm](https://etd.ohiolink.edu/apexprod/rws_etd/send_file/send?accession=osu1626889287593463&disposition=inline). This implementation uses a PID control loop, with the proportional term using distance error and the integral and derivative term using velocity error. There was some additional logic around the PID controller to handle different scenarios such as when the car in front's velocity is higher than the set velocity, when the follow distance is greater than a certain amount, and when the target velocity is less than set velocity. For my implementation, the car's set velocity was the car's max speed. The following shows the block diagram of the ACC implementation. A few of the blocks were omitted from my implementation as there are no brake or accelerator pedals in my case.

![pic](/report/ACC%20Block%20Diagram.png)

As for the PID controller itself, I followed an implementation I found on youtube that discretizes the PID control and offers some additional checks such as integral anti-windup and a low pass filter on the derivative term. An overview of this implementation can be found here [PID Controller Implementation in Software - Phil's Lab #6](https://www.youtube.com/watch?v=zOByx3Izf5U&t=734s). This implementation was modified so that it could be used with the ACC implementation.

### Challenges

There were a few challenges throughout this simulation that took some time to overcome. For one, the plane that the cars drive on is the x-z plane, with y being the vertical. The origin of the game is at (0,0,0). Four of the lanes would be traveling in the positive direction but the other lanes would not be. The logic had to be more complicated because of this. One of the other challenges was deleting objects. Vpython objects cannot be deleted in memory so this drove me to changing the architecture in the beginning from queues to a ring buffer. 

When it came to implementing turning in the simulation, which requires inserting, removing, and shifting objects in the ring buffer, I ran into problems with performance during deep copies of the vpython objects. In C++, my approach would be to have the lane class hold an array of pointers to car objects, which would all be pre-generated. Therefore, instead of doing deep copies of objects, I would just have to move pointers around. I am not sure if this is possible to do with objects stored in numpy arrays, however, it should be achievable in python (maybe with another data structure). At this time, I began doing some research of other graphics libraries available out there. This research can be found here [graphics_research.md](graphics_research.md). 

To try out one of them, pygame, I decided to implement the software LiDAR approach that was mentioned in the Design Overview section.  

## Pygame

A majority of the time was spent learning how to use the library. I mainly used the documentation on the pygame website and this tutorial [The Ultimate Introduction to Pygame](https://www.youtube.com/watch?v=AY9MnQ4x3zk&t=8611s). The implementation of the LiDAR demo was pretty straight forward. There was a car class that handled the cars kinematics, control, and display ion the game. The car is controlled using the W,A,S,D keys. The car would placed in the center of a screen. A list of 2D points would be passed into the simulation and a function would draw lines (walls) between all points, creating a closed polygon. A for loop generates x number of lines that shoot out from the car in all directions. These act as the 'lasers'. Another for loop finds all of the line intersections between the car lines and the walls in the environment. After a bunch of bounds checking (because the lines are actually line segments), a red dot is displayed if it satisfies the bound checks. The last thing I worked on was hiding in-game controls such as hiding the walls and changing the number of lines that shot out from the car. This approach is what I would have liked to use it for the vpython simulation but eventually omitted it because of the computational load. 

# Summary, Conclusions, and Future Work





