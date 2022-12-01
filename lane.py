import random
from car import Car, C_States
import numpy as np
from event import TL_Event, C_Event
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

        # Events
        self.turn_event_trigger = False
        self.turn_event_dir = None
        self.turn_event_car_idx = None

    def get_car_count(self):
        return self.cars_on_road

    def lane_full(self):
        return self.cars_on_road == self.max_cars_on_road

    def lane_empty(self):
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
        print("CAR DEACTIVATED")
        self.cars[self.start_ptr].invisible()
        self.cars[self.start_ptr].reset(self.lane_start)
        self.cars_on_road -= 1
        self.start_ptr = (self.start_ptr + 1) % self.max_cars 

    # Insert a car into the lane (for when cars turn into the lane)
    # 0 indexing for idx
    def insert(self, idx, car : Car):
        
        # print(f" id of old car: {id(car)} ")
        if self.lane_full():
            print("NO ROOM TO ADD CAR!")
            return False
        # 0th car is the one that is furthest along in the lane 
        if idx <0 or idx > (g.max_cars-1):
            print("INVALID INDEX")
            return False
        print(f"idx before for loop value IN INSERT: {idx}")
        print(f"self.end_ptr = {self.end_ptr} and abs and end val is {abs(idx - self.end_ptr)}")
        for i in range(idx, idx + abs(idx - self.end_ptr)):
            loop_index = idx + (idx + abs(idx - self.end_ptr)) - 1 - i
            print(f"loop index is {loop_index}")
            temp = self.cars[loop_index % self.max_cars]
            self.cars[(loop_index+1) % self.max_cars].invisible()
            self.cars[(loop_index+1) % self.max_cars].reset(self.lane_start)
            self.cars[(loop_index+1) % self.max_cars] = copy.deepcopy(temp)
            self.cars[(loop_index+1) % self.max_cars].vehicle = temp.vehicle.clone()
            temp.invisible()
            temp.reset(self.lane_start)
            # del temp
        # print(f"pos of passed in car {car.vehicle.pos}")
        self.cars[idx].invisible()
        self.cars[idx].reset(self.lane_start)
        self.cars[idx] = copy.deepcopy(car) # this should run
        self.cars[idx].vehicle = car.vehicle.clone()
        car.invisible()
        car.reset(self.lane_start)
        # print(f"pos after deepcopy {self.cars[idx].vehicle.pos}")
        # print(f"new id: {id(self.cars[idx])}" )
        self.end_ptr = (self.end_ptr + 1) % self.max_cars
        self.cars_on_road +=1
        # print(f"new car visible? {self.cars[idx].vehicle.visible}")

        # insert always takes car from another lane, so need to modify the car object
        # determine what the rot degree is based on where it came from.
        # print(f"check if og car, rotation = {self.cars[idx].rotation}")
        # print(f"pos before {self.cars[idx].vehicle.pos}")
        og_rot_deg = self.cars[idx].rotation
        if self.cars[idx].pending_right_turn:
            self.cars[idx].set_direction_flags(og_rot_deg - 90)
        elif self.cars[idx].pending_left_turn:
            self.cars[idx].set_direction_flags(og_rot_deg + 90)

        # print(f"check if og car, rotation = {self.cars[idx].rotation}")

        # print(self.cars[idx].xaxis_plus)
        # print(self.cars[idx].zaxis_plus)
        # print(self.cars[idx].xaxis_minus)
        # print(self.cars[idx].zaxis_minus)
        # print(f'present state: {self.cars[idx].pr_state}')
        # print(f'present state: {self.cars[idx].nx_state}')


        self.cars[idx].lane_identifer = self.identifier

        return True

    def remove(self, idx):
        if self.lane_empty():
            print("NOTHING TO REMOVE LANE EMPTY")
            return False
        if idx <0 or idx > (g.max_cars-1):
            print("INVALID INDEX")
            return False
        
        # for the car thats being removed, reset it 
        self.cars[idx].invisible()
        self.cars[idx].reset(self.lane_start)
        print("REMOVE LOOP")
        print(f"idx before for loop value: {idx}")
        print(f"self.end_ptr = {self.end_ptr} and the end idx = {abs(idx - self.end_ptr) -1}")
        end = abs(idx - self.end_ptr)-1
        for i in range(idx, idx+ end): # minus 1 because end_ptr points to empty loc
            temp = self.cars[(i+1) % self.max_cars]
            self.cars[i % self.max_cars] = copy.deepcopy(temp)
            self.cars[i % self.max_cars].vehicle = temp.vehicle.clone()
            temp.invisible()
            temp.reset(self.lane_start)
            # del temp
            
            print(f"CAR HAS BEEN COPIED: i = {i}")

            # print(f" pending right turn: {self.cars[i % self.max_cars].pending_right_turn}")

        # -1 mod 8 = 7
        print(f"the index its reseting: {(idx+end) % self.max_cars}")
        print(f"startptr: {self.start_ptr}")
        self.cars[(idx+end) % self.max_cars].invisible()
        self.cars[(idx+end) % self.max_cars].reset(self.lane_start) 
        
        # print(f" pending right turn: {self.cars[self.start_ptr].pending_right_turn}")

        self.end_ptr = (self.end_ptr - 1) % self.max_cars
        self.cars_on_road -=1

        # print(f"end of the remove function call {self.cars_on_road} and {self.end_ptr}")

        return True

    # Check to see if the car is still within the lane
    def check_bounds(self):
        if abs(self.cars[self.start_ptr].lane_pos) > g.size*0.5:
            self.deactivate() # this always pops the furthest along car

    # Handle turning event
    def handle_turn_event(self, idx, action : C_Event):
        actual_idx = (self.start_ptr + idx) % self.max_cars
        if action == C_Event.TURN_RIGHT:
            self.cars[actual_idx].pending_right_turn = True
        elif action == C_Event.TURN_LEFT:
            self.cars[actual_idx].pending_left_turn = True
        else:
            print(f"ERROR: TURN EVENT HANDLER GIVEN OTHER ACTION THAN TURNING, {action}")

    def update_closest_distance(self):

        if self.lane_empty():
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
        # if self.identifier == 0:
        #     if self.cars[self.start_ptr].lane_pos >= self.stop_line_pos:
        #         self.cars[self.start_ptr].pending_right_turn = True
        
        # Debug 
        # self.debug()

        # For debug
        self.TL_state_prev = self.TL.get_state()

    def debug(self):
        if self.identifier == 0:
            if self.TL.get_state() != self.TL_state_prev:
                thing = ""
                if self.TL.get_state() == TL_Event.GREEN:
                    thing = "green"
                elif self.TL.get_state() == TL_Event.RED:
                    thing = "red"
                elif self.TL.get_state() == TL_Event.YELLOW:
                    thing = "yellow"
                print(f"state change detected, now its {thing}")
            print(f'0-4: {self.cars[0].distance_to_nearest_obj}\t{self.cars[1].distance_to_nearest_obj}\t{self.cars[2].distance_to_nearest_obj}\t{self.cars[3].distance_to_nearest_obj} ' )
            # print(f'lead car {self.cars[self.start_ptr].distance_to_nearest_obj}, lead car pos {self.cars[self.start_ptr].lane_pos} ,following car {self.cars[self.start_ptr+1].distance_to_nearest_obj} and ptr {self.start_ptr} 2nd car pos {self.cars[self.start_ptr+1].lane_pos}')
            # print(f'4th car dis {self.cars[4].distance_to_nearest_obj}, lane pos {self.cars[4].lane_pos} vel {self.cars[4].vel}, stop line pos: {self.stop_line_pos} lead_veh_vel{self.cars[4].lead_veh_vel}')
            # print(f' 3rd car {self.cars[2].distance_to_nearest_obj}')  

    # Update the car with the car in front of it's velocity
    def update_lead_veh_vel(self):
        for i in range(1, self.cars_on_road):
            idx = (self.start_ptr + i) % self.max_cars
            self.cars[idx].set_lead_vehicle_pos(self.cars[(idx-1) % self.max_cars].vel)

    def check_for_turn_events(self):
        inverted = self.identifier < 6 and self.identifier > 1
        for i in range(0, self.cars_on_road):
            idx = (self.start_ptr + i) % self.max_cars
            if (inverted and self.cars[idx].lane_pos <= self.stop_line_pos) \
                    or (not inverted and self.cars[idx].lane_pos >= self.stop_line_pos ):
                if not self.cars[idx].execute_event_now:
                    if self.cars[idx].pending_right_turn:
                        self.turn_event_trigger = True
                        self.turn_event_dir = C_Event.TURN_RIGHT
                        self.turn_event_car_idx = idx
                        self.cars[idx].execute_event_now = True
                        print("code ran in check for turn events. setting trigger to true")
                        print(id(self.cars[idx]))
                    elif self.cars[idx].pending_left_turn:
                        self.turn_event_trigger = True
                        self.turn_event_dir = C_Event.TURN_LEFT
                        self.turn_event_car_idx = idx
                        self.cars[idx].execute_event_now = True
                        print("code ran 2")

    def get_idx_to_insert(self):

        if self.lane_empty():
            return self.start_ptr

        print(f"num cars in lane {self.cars_on_road}")

        inverted = self.identifier < 6 and self.identifier > 1
        print(f' inverted: {inverted}')
        for i in range(0, self.cars_on_road):
            idx = (self.start_ptr + i) % self.max_cars
            if inverted and self.cars[idx].lane_pos > self.stop_line_pos:
                return idx
            elif (not inverted) and self.cars[idx].lane_pos < self.stop_line_pos:
                return idx

        # if the first if and the for loop didnt catch it,
        # then all the cars are in front of the stop line adn the place to insert
        # is the last index.
        return self.end_ptr
            

    # Store a reference to the traffic light so the Lane can view its state
    def set_TL_reference(self, TL : TrafficLight):
        self.TL = TL




            
    

