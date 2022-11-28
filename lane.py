import random
from car import Car
import numpy as np
from event import TL_Event
import copy
from trafficlight import TrafficLight
from config import g
from vpython import vector


# The lane class uses a numpy array in order to store the car objects for each Lane. There is a bit of structure built around the array
# such as inserting into an index and shifting (for when a car turns into the lane), the use of start and end pointers to move through the array
# like a ring buffer as cars spawn and despawn, and activate and deactivate functions to move the start and end pointers. 

class Lane:

    def __init__(self, identifier, max_cars, max_cars_on_road, lane_start_pos : vector, lane_end_pos : vector, stop_line_pos, car_rot_deg):

        # No arg seeds the random generator with the system time.
        random.seed()
        
        # Create the car array and initialize and store all the info about the Lane
        self.cars = np.empty(max_cars, dtype=type(Car))
        self.max_cars = max_cars
        self.max_cars_on_road = max_cars_on_road
        self.cars_on_road = 0
        self.lane_start = lane_start_pos
        self.lane_end = lane_end_pos
        self.stop_line_pos = stop_line_pos
        self.identifier = identifier

        # Pointers to point to the section of the array that is currently on the road
        self.start_ptr = 0
        self.end_ptr = 0

        # Generate all cars, set all to invisible
        for i in range(0,self.max_cars):
            self.cars[i] = Car(self.lane_start, car_rot_deg, self.identifier, False)

        # Give lane awareness fo the traffic light
        self.TL = None
        self.TL_state_prev = None   # used for debugging!

    def get_car_count(self):
        return self.cars_on_road

    def lane_full(self):
        return self.cars_on_road == self.max_cars_on_road

    def is_empty(self):
        return self.cars_on_road == 0

    # Put a car on a road (activates from back (end_ptr))
    def activate(self):
        if(not self.lane_full()): 
            self.cars[self.end_ptr].reset(self.lane_start)
            self.cars[self.end_ptr].visible()
            self.cars_on_road += 1
            self.end_ptr = (self.end_ptr + 1) % self.max_cars

    # Take a car off the road (activates from front(start_ptr))
    def deactivate(self):
        self.cars[self.start_ptr].invisible()
        self.cars_on_road -= 1
        self.start_ptr = (self.start_ptr + 1) % self.max_cars 

    # Insert a car into the lane (for when cars turn into the lane)
    def insert(self, idx, car : Car):
        # idx is defined as the index of the current cars on the road (zero-indexed)
        # 0th car is the one that is furthest along in the lane 
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
        self.cars[actual_idx] = copy.deepcopy(car)

    # Check to see if the car is still within the lane
    def check_bounds(self):
        if abs(self.cars[self.start_ptr].lane_pos) > g.size*0.5:
            self.deactivate() # this always pops the furthest along car

    def update_closest_distance(self):

        if self.is_empty():
            return 

        # Determine the closest distance based on whether its a car or the traffic light for the lead car
        # Some lanes coordinate axes is backwards (car is traveling in the negative direction instead of the forward)
        # If lane 2-5, then the lane_pos is greater than the stop line pos (more positive)
        # If the lead car is past the stop line, then no distance
        if (self.cars[self.start_ptr].lane_pos < self.stop_line_pos and self.identifier < 6 and self.identifier > 1) or \
                (self.cars[self.start_ptr].lane_pos > self.stop_line_pos and not(self.identifier < 6 and self.identifier > 1)):
            self.cars[self.start_ptr].update_distances(None)
        else:
            # Else lead car is behind the stop line
            if self.TL.get_state() == TL_Event.GREEN:
                self.cars[self.start_ptr].update_distances(None)
            else:
                # Else the light is yellow or red
                dis = abs(self.cars[self.start_ptr].lane_pos - self.stop_line_pos)
                if self.TL.get_state() == TL_Event.YELLOW and dis < g.car_dis_thres_yellow and self.cars[self.start_ptr].vel > g.car_vel_thres_yellow:
                    # Ignore the light if it meets distance and velocity thresholds while light is yellow.
                    self.cars[self.start_ptr].update_distances(None)
                else: 
                    # Else oblige to the light.
                    self.cars[self.start_ptr].update_distances(dis)         
            
        # Determine the closest distance for the rest of the cars.
        # Range starts at 1 to ignore lead car and loop won't get executed if there's one car on the road
        # Loop only goes through the current cars on the road and ignores the rest
        for i in range(1, self.cars_on_road):
            
            # Calculate the correct index
            idx = (self.start_ptr + i) % self.max_cars

            # Calculate two distances, to the light and then to the nearest car,
            # then take the min of the two.
            dis_to_car = 0
            dis_to_light = 0

            # Find the distance to the car, adjusting for lane direction
            if self.identifier < 6 and self.identifier > 1:
                dis_to_car = self.cars[idx].lane_pos - self.cars[(idx-1) % self.max_cars].lane_pos
            else:
                dis_to_car = self.cars[(idx-1) % self.max_cars].lane_pos - self.cars[idx].lane_pos

            # Find the distance to the light. If the light is green there is no limit distance
            if self.TL.get_state() == TL_Event.GREEN:
                dis_to_light = dis_to_car
            else: 
                # Else the light is yellow or red
                # First check whether the car is behind the light or not, adjusting for lane direction
                if self.identifier < 6 and self.identifier > 1: 
                    # Check if the car is in front of the stop line
                    if self.cars[idx].lane_pos < self.stop_line_pos:
                        # If so, set the dis_to_light to be equal to dis_to_car
                        # Taking the min of the two, so this guarantees correct one is picked.
                        dis_to_light = dis_to_car
                    else:
                        # Else the car is behind the stop line and the light is red/yellow. Calculate the distance
                        dis_to_light =  self.cars[idx].lane_pos - self.stop_line_pos
                        # Check if light is yellow and if it meets thresholds, ignore the light
                        if self.TL.get_state() == TL_Event.YELLOW and dis_to_light < g.car_dis_thres_yellow and self.cars[idx].vel > g.car_vel_thres_yellow:
                            dis_to_light = dis_to_car
                else:
                    # Else repeat the calculation but adjusting for the other lane direction  
                    if self.cars[idx].lane_pos > self.stop_line_pos:
                        dis_to_light = dis_to_car
                    else:
                        dis_to_light = self.stop_line_pos - self.cars[idx].lane_pos
                        if self.TL.get_state() == TL_Event.YELLOW and dis_to_light < g.car_dis_thres_yellow and self.cars[idx].vel > g.car_vel_thres_yellow:
                            dis_to_light = dis_to_car

            # Update the cars nearest distance by taking min of dis_to_car and dis_to_light
            self.cars[idx].update_distances(min(dis_to_car, dis_to_light))

        # TEMP
        if self.identifier == 0:
            if self.cars[self.start_ptr].lane_pos >= self.stop_line_pos:
                self.cars[self.start_ptr].pending_right_turn = True
        
        # Debug 
        # self.debug()

        # For debug
        self.TL_state_prev = self.TL.get_state()

    def debug(self):
        if self.identifier == 3:
            if self.TL.get_state() != self.TL_state_prev:
                thing = ""
                if self.TL.get_state() == TL_Event.GREEN:
                    thing = "green"
                elif self.TL.get_state() == TL_Event.RED:
                    thing = "red"
                elif self.TL.get_state() == TL_Event.YELLOW:
                    thing = "yellow"
                print(f"state change detected, now its {thing}")
            print(f'lead cars dis: {self.cars[self.start_ptr].distance_to_nearest_obj} ptr = {self.start_ptr}' )
            print(f'lead car {self.cars[self.start_ptr].distance_to_nearest_obj}, lead car pos {self.cars[self.start_ptr].lane_pos} ,following car {self.cars[self.start_ptr+1].distance_to_nearest_obj} and ptr {self.start_ptr} 2nd car pos {self.cars[self.start_ptr+1].lane_pos}')
            print(f'4th car dis {self.cars[4].distance_to_nearest_obj}, lane pos {self.cars[4].lane_pos} vel {self.cars[4].vel}, stop line pos: {self.stop_line_pos} lead_veh_vel{self.cars[4].lead_veh_vel}')
            print(f' 3rd car {self.cars[2].distance_to_nearest_obj}')  

    # Update the car with the car in front of it's velocity
    def update_lead_veh_vel(self):
        for i in range(1, self.cars_on_road):
            idx = (self.start_ptr + i) % self.max_cars
            self.cars[idx].set_lead_vehicle_pos(self.cars[(idx-1) % self.max_cars].vel)

    # Store a reference to the traffic light so the Lane can view its state
    def set_TL_reference(self, TL : TrafficLight):
        self.TL = TL




            
    

