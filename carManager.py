import numpy as np
import copy
from config import g
from car import Car, C_States
from env import Env
from vpython import vector, sphere, color, sleep, mag, mag2
import random
from trafficlight import TrafficLight
from event import TL_Event


class Lane:

    def __init__(self, max_cars, max_cars_on_road, lane_start_pos : vector, lane_end_pos : vector, stop_line_pos, car_rot_deg):
        self.cars = np.empty(max_cars, dtype=type(Car))
        self.max_cars = max_cars
        self.max_cars_on_road = max_cars_on_road
        self.cars_on_road = 0
        self.lane_start = lane_start_pos
        self.lane_end = lane_end_pos
        self.stop_line_pos = stop_line_pos

        # Pointers to point to the cars that are currently on the road
        self.start_ptr = 0
        self.end_ptr = 0

        # generate all cars, set all to invisible
        for i in range(0,self.max_cars):
            self.cars[i] = Car(self.lane_start, car_rot_deg, visible=False)

        # for awareness of traffic lights
        self.TL = None

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

    def check_bounds(self):
        # print (self.cars[self.start_ptr].vehicle.pos)
        # print(mag(self.cars[self.start_ptr].vehicle.pos))
        if abs(self.cars[self.start_ptr].lane_pos) > g.size*0.5:
            self.deactivate() # this always pops the furthest along car

    def update_closest_distance(self):
        # TODO: CHANGE THESE VARIABLE NAMES!!!!!!!!!!!

        if self.cars_on_road == 0:
            return

        first_car_behind_light = False
        # determine the closest distance based on whether its a car or the traffic light for the farthest car
        if self.cars[self.start_ptr].lane_pos > self.stop_line_pos:
            self.cars[self.start_ptr].update_distances(None)
        else:
            first_car_behind_light = True
            if self.TL.get_state == TL_Event.GREEN:
                self.cars[self.start_ptr].update_distances(None)
            else:
                self.cars[self.start_ptr].update_distances(self.stop_line_pos \
                    - self.cars[self.start_ptr].lane_pos)
        
        # get the car in front and subtract it from the current car and that is the distance between them
        # range starts at 1 to ignore furthest along car
        # wont get executed if theres only one car on the road
        for i in range(1, self.cars_on_road):
            idx = (self.start_ptr + i) % self.max_cars
            # first car is in front of the light so here we need to check which car is behind the light
            if not first_car_behind_light:
                if self.cars[idx].lane_pos > self.stop_line_pos:
                    self.cars[idx].update_distances(
                        self.cars[(idx+1) % self.max_cars].lane_pos
                            - self.cars[idx].lane_pos)
                else:
                    self.cars[idx].update_distances(
                        self.stop_line_pos - self.cars[idx].lane_pos)
            else:
                self.cars[idx].update_distances(
                    self.cars[(idx+1) % self.max_cars].lane_pos
                        - self.cars[idx].lane_pos)

    def set_TL_reference(self, TL : TrafficLight):
        self.TL = TL




            
    


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
                                 self.env.stop_line_position[i],
                                 self.car_rot[i])





        # for item in self.lanes:
        #     sphere(pos = item.lane_start, radius=10, color = color.green)
        #     sphere(pos = item.lane_end, radius=10, color= color.red)



    def run(self, curr_time):
        # will be used to add cars on the fly, but for now ill do an add function
        # read file and import all the times that cars will be spawned? or do randomly? 
        # probably randomly long term but fixed for now.

        # this function will do two things: determine whether a new car will be spawned or deleted. 
        # AND it will run all the individual cars state machine? or should the lane do that? 
        # CHECKING FOR CAR DEACTIVATING SHOULD BE IN HERE AS ITS THE CAR MANAGER.
        for lane in self.lanes:
            # Check the furthest along car to see where it is
            lane.check_bounds()
            lane.update_closest_distance()

            # Run all the car state machines
            for car in lane.cars:
                car.run(curr_time)
    


    # add a car to a lane. if idx is not specified, a random lane is picked.
    def add_car(self, idx = -1 ):
        if idx == -1:
            self.lanes[random.randint(0,self.num_lanes-1)].activate()
        elif idx >= 0 and idx < (self.num_lanes):
            self.lanes[idx].activate()

    def set_TL_references(self, TLs : list):
        self.lanes[0].set_TL_reference(TLs[3])
        self.lanes[1].set_TL_reference(TLs[3])
        self.lanes[2].set_TL_reference(TLs[0])
        self.lanes[3].set_TL_reference(TLs[0])
        self.lanes[4].set_TL_reference(TLs[2])
        self.lanes[5].set_TL_reference(TLs[2])
        self.lanes[6].set_TL_reference(TLs[1])
        self.lanes[7].set_TL_reference(TLs[1])



