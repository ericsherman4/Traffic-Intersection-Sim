import numpy as np
import copy
from config import g
from car import Car, C_States
from env import Env
from vpython import vector, sphere, color, sleep
import random


class Lane:

    def __init__(self, max_cars, max_cars_on_road, lane_start_pos : vector, lane_end_pos : vector, car_rot_deg):
        self.cars = np.empty(max_cars, dtype=type(Car))
        self.max_cars = max_cars
        self.max_cars_on_road = max_cars_on_road
        self.cars_on_road = 0
        self.lane_start = lane_start_pos
        self.lane_end = lane_end_pos

        # Pointers to point to the cars that are currently on the road
        self.start_ptr = 0
        self.end_ptr = 0

        # generate all cars, set all to invisible
        for i in range(0, self.max_cars):
            self.cars[i] = Car(self.lane_start, car_rot_deg, visible=False)

    def get_car_count(self):
        return self.cars_on_road

    def lane_full(self):
        return self.cars_on_road == self.max_cars_on_road

    def is_empty(self):
        return self.cars_on_road == 0

    # only activates from back 
    def activate(self):
        if(not self.lane_full()): 
            self.cars[self.end_ptr].visible()
            self.cars_on_road += 1
            self.end_ptr = (self.end_ptr + 1) % self.max_cars

    # deactivates from front
    def deactivate(self):
        self.cars[self.start_ptr].invisible()
        self.cars_on_road -= 1
        self.start_ptr = (self.start_ptr + 1) % self.max_cars 

    # idx is defined as the index of the current cars on the road (zero-indexed)
    # 0th car is the one that is furthest along in the lane 
    def insert(self, idx, car : Car):
        actual_idx = (self.start_ptr + idx) % self.max_cars
        if actual_idx > self.end_ptr:
            print("INVALID INDEX")
            return
        end = abs((actual_idx - self.end_ptr))
        for i in range(actual_idx, actual_idx + end):
            # i is just for how many times it runs, do not use for direct indexing.
            idx = self.end_ptr - ((actual_idx + i) % self.max_cars)
            temp = self.cars[idx + 1]
            self.cars[idx] = temp
        self.cars[actual_idx] = copy.copy(car)

            
    


class CarManager:
    # where do I want to keep track of all the cars? 
    # how do i coordinate when cars are generated? 
    # do i just do it forever with different periods between generating cars?
    
    def __init__(self):
        # Total of 8 lanes. 4 going each way so we need 8 data structs. 

        self.num_lanes = 8

        self.lanes = np.empty(self.num_lanes,dtype=Lane)

        self.env = Env()
        self.car_rot = [180, 180, 0, 0, 270, 270, 90, 90]
        
        # generate the lanes

        for i in range(0,self.num_lanes):
            self.lanes[i] = Lane(g.max_cars,g.max_cars_on_road,
                                 self.env.lane_pos_start[i], 
                                 self.env.lane_pos_end[i],
                                 self.car_rot[i])
        


        # for item in self.lanes:
        #     sphere(pos = item.lane_start, radius=10, color = color.green)
        #     sphere(pos = item.lane_end, radius=10, color= color.red)



    def run(self, curr_time_ms):
        # will be used to add cars on the fly, but for now ill do an add function
        # read file and import all the times that cars will be spawned? or do randomly? 
        # probably randomly long term but fixed for now.

        # this function will do two things: determine whether a new car will be spawned or deleted. 
        # AND it will run all the individual cars state machine? or should the lane do that? 
        # CHECKING FOR CAR DEACTIVATING SHOULD BE IN HERE AS ITS THE CAR MANAGER.
        for lane in self.lanes:
            for car in lane.cars:
                car.run(curr_time_ms)
        




    
    def add_car(self, idx : -1 ):
        if idx == -1:
            self.lanes[random.randint(0,self.num_lanes-1)].activate()
        elif idx >= 0 and idx <= (self.num_lanes-1):
            self.lanes[idx].activate()