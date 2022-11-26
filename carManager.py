import numpy as np
import copy
from config import g
from car import Car, C_States
from env import Env
from vpython import vector, sphere, color, sleep, mag, mag2
import random
from trafficlight import TrafficLight
from event import TL_Event, Event, C_Event, EventType


class Lane:

    def __init__(self, identifier, max_cars, max_cars_on_road, lane_start_pos : vector, lane_end_pos : vector, stop_line_pos, car_rot_deg):
        self.cars = np.empty(max_cars, dtype=type(Car))
        self.max_cars = max_cars
        self.max_cars_on_road = max_cars_on_road
        self.cars_on_road = 0
        self.lane_start = lane_start_pos
        self.lane_end = lane_end_pos
        self.stop_line_pos = stop_line_pos
        self.identifier = identifier

        # Pointers to point to the cars that are currently on the road
        self.start_ptr = 0
        self.end_ptr = 0

        # generate all cars, set all to invisible
        for i in range(0,self.max_cars):
            self.cars[i] = Car(self.lane_start, car_rot_deg, visible=False)

        # for awareness of traffic lights
        self.TL = None
        # used for debugging!
        self.TL_state_prev = None

    def get_car_count(self):
        return self.cars_on_road

    def lane_full(self):
        return self.cars_on_road == self.max_cars_on_road

    def is_empty(self):
        return self.cars_on_road == 0

    # only activates from back 
    def activate(self):
        if(not self.lane_full()): 
            self.cars[self.end_ptr].reset_pos(self.lane_start)
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

        # first_car_behind_light = False
        # determine the closest distance based on whether its a car or the traffic light for the farthest car
        # some lanes coordinate axes is backwards (car is traveling in the negative direction instead of the forward)
        # lanes 4,5 and 3,2 are backwards

        if self.identifier < 6 and self.identifier > 1:
            if self.cars[self.start_ptr].lane_pos < self.stop_line_pos:
                self.cars[self.start_ptr].update_distances(None)
            else:
                # first_car_behind_light = True # the car is behind the light
                if self.TL.get_state() == TL_Event.GREEN:
                    self.cars[self.start_ptr].update_distances(None)
                else:
                    # flip order of the subtraction here because the lane is backwards
                    dis = self.cars[self.start_ptr].lane_pos - self.stop_line_pos
                    if dis < 25 and self.TL.get_state() == TL_Event.YELLOW:
                        self.cars[self.start_ptr].update_distances(None)
                    else: 
                        self.cars[self.start_ptr].update_distances(dis)
        else:
            if self.cars[self.start_ptr].lane_pos > self.stop_line_pos:
                self.cars[self.start_ptr].update_distances(None)
            else:
                first_car_behind_light = True # the car is behind the light
                if self.TL.get_state() == TL_Event.GREEN:
                    self.cars[self.start_ptr].update_distances(None)
                else:
                    dis = self.stop_line_pos - self.cars[self.start_ptr].lane_pos
                    if dis < 25 and self.TL.get_state() == TL_Event.YELLOW:
                        self.cars[self.start_ptr].update_distances(None)
                    else: 
                        self.cars[self.start_ptr].update_distances(dis)            
            
        
        # if self.identifier == 3:
            # print(f'lane_pos is {self.cars[self.start_ptr].lane_pos} and the stop line is {self.stop_line_pos} and the distance is {self.cars[self.start_ptr].distance_to_nearest_car}' )


        # get the car in front and subtract it from the current car and that is the distance between them
        # range starts at 1 to ignore furthest along car
        # wont get executed if theres only one car on the road
    

        for i in range(1, self.cars_on_road):
            idx = (self.start_ptr + i) % self.max_cars
            # first car is in front of the light so here we need to check which car is behind the light
            # TODO: THIS LOGIC IS DEFINITELY MESSED UP and NEEDS FURTHER INVESTIGATION. THE bool there i think needs to updated each loop or something
            # if not first_car_behind_light:

            # calculate two distances
            dis_to_car = 0
            dis_to_light = 0

            # find the distance to the car, adjusting for lane direction
            if self.identifier < 6 and self.identifier > 1:
                dis_to_car = self.cars[idx].lane_pos - self.cars[(idx-1) % self.max_cars].lane_pos
            else:
                dis_to_car = self.cars[(idx-1) % self.max_cars].lane_pos - self.cars[idx].lane_pos

            # find the distance to the light. if the light is green there is no limit distance
            if self.TL.get_state() == TL_Event.GREEN:
                dis_to_light = dis_to_car
            else: 
                # the light is yellow or red
                # first check whether the car is behind the light or not
                # if the car is in front of the light, then dis_to_light should be ignored
                # and of course, adjust for car direction
                if self.identifier < 6 and self.identifier > 1: 
                    if self.cars[idx].lane_pos < self.stop_line_pos:
                        dis_to_light = dis_to_car
                    else:
                        # the car is behind the stop line and the light is red/yellow
                        dis_to_light =  self.cars[idx].lane_pos - self.stop_line_pos
                        if self.TL.get_state() == TL_Event.YELLOW and dis_to_light < g.car_dis_thres_yellow and self.cars[idx].vel > g.car_dis_thres_yellow:
                            dis_to_light = dis_to_car
                else: 
                    if self.cars[idx].lane_pos > self.stop_line_pos:
                        dis_to_light = dis_to_car
                    else:
                        dis_to_light = self.stop_line_pos - self.cars[idx].lane_pos
                        if dis_to_light < 25 and self.TL.get_state() == TL_Event.YELLOW:
                            dis_to_light = dis_to_car
                

                # if self.identifier < 6 and self.identifier > 1:
                #     dis_to_light =  self.cars[idx].lane_pos - self.stop_line_pos
                # else:    
                #     dis_to_light = self.stop_line_pos - self.cars[idx].lane_pos

            self.cars[idx].update_distances(min(dis_to_car, dis_to_light))
        

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
            # print(f'lead cars dis: {self.cars[self.start_ptr].distance_to_nearest_car} ptr = {self.start_ptr}' )
            # print(f'lead car {self.cars[self.start_ptr].distance_to_nearest_car}, lead car pos {self.cars[self.start_ptr].lane_pos} ,following car {self.cars[self.start_ptr+1].distance_to_nearest_car} and ptr {self.start_ptr} 2nd car pos {self.cars[self.start_ptr+1].lane_pos}')
            # print(f'4th car dis {self.cars[4].distance_to_nearest_car}, lane pos {self.cars[4].lane_pos} vel {self.cars[4].vel}, stop line pos: {self.stop_line_pos} lead_veh_vel{self.cars[4].lead_veh_vel}')
            # print(f' 3rd car {self.cars[2].distance_to_nearest_car}')  

        self.TL_state_prev = self.TL.get_state()

    def update_lead_veh_vel(self):
        for i in range(1, self.cars_on_road):
            idx = (self.start_ptr + i) % self.max_cars
            self.cars[idx].set_lead_vehicle_pos(self.cars[(idx-1) % self.max_cars].vel)

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
            self.lanes[i] = Lane(i, g.max_cars ,g.max_cars_on_road,
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
            lane.update_lead_veh_vel()

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
        self.lanes[0].set_TL_reference(TLs[2])
        self.lanes[1].set_TL_reference(TLs[2])
        self.lanes[2].set_TL_reference(TLs[0])
        self.lanes[3].set_TL_reference(TLs[0])
        self.lanes[4].set_TL_reference(TLs[3])
        self.lanes[5].set_TL_reference(TLs[3])
        self.lanes[6].set_TL_reference(TLs[1])
        self.lanes[7].set_TL_reference(TLs[1])

    def generate_events(self, use_random = False, total_duration = -1):

        time = 0

        def increment(val):
            nonlocal time
            time += val
            return time
        
        # use manually generated entries
        if not use_random:
            Event(increment(10), EventType.C_EVENT, C_Event.ADD_CAR, lane = 3)
            Event(increment(15), EventType.C_EVENT, C_Event.ADD_CAR, lane = 3)
            Event(increment(20), EventType.C_EVENT, C_Event.ADD_CAR, lane = 3)
            Event(increment(10), EventType.C_EVENT, C_Event.ADD_CAR, lane = 3)
            Event(increment(10), EventType.C_EVENT, C_Event.ADD_CAR, lane = 3)
            Event(increment(20), EventType.C_EVENT, C_Event.ADD_CAR, lane = 3)
            Event(increment(20), EventType.C_EVENT, C_Event.ADD_CAR, lane = 3)
            Event(increment(15), EventType.C_EVENT, C_Event.ADD_CAR, lane = 3)
            Event(increment(10), EventType.C_EVENT, C_Event.ADD_CAR, lane = 3)
            Event(increment(10), EventType.C_EVENT, C_Event.ADD_CAR, lane = 3)
        else:
            for i in range(0,8):
                time = 0
                for j in range(0,15):
                    Event(increment(random.randint(10,23)), EventType.C_EVENT, C_Event.ADD_CAR, lane = i)



                # Event(time + random.randint(0,15), EventType.C_EVENT, C_Event.ADD_CAR, lane= 3) 
                # Event(time + random.randint(0,15), EventType.C_EVENT, C_Event.ADD_CAR, lane= 1) 
                # Event(time + random.randint(0,15), EventType.C_EVENT, C_Event.ADD_CAR, lane= 0) 
                # Event(time + random.randint(0,15), EventType.C_EVENT, C_Event.ADD_CAR, lane= 2) 
                # Event(time + random.randint(0,15), EventType.C_EVENT, C_Event.ADD_CAR, lane= 7) 
                # increment(20)
                # Event(time, EventType.C_EVENT, C_Event.ADD_CAR, lane = -1)
                # Event(time + random.randint(5,15), EventType.C_EVENT, C_Event.ADD_CAR, lane= 2) 
                # Event(time + random.randint(5,15), EventType.C_EVENT, C_Event.ADD_CAR, lane= 5) 
                # Event(time + random.randint(5,15), EventType.C_EVENT, C_Event.ADD_CAR, lane= 6) 
                # Event(time + random.randint(5,15), EventType.C_EVENT, C_Event.ADD_CAR, lane= 3) 
                # Event(time + random.randint(5,15), EventType.C_EVENT, C_Event.ADD_CAR, lane= 4)
                # increment(15)
                # Event(time, EventType.C_EVENT, C_Event.ADD_CAR, lane = -1)
                # for i in range(0,7):
                #     Event(time + random.randint(7,20), EventType.C_EVENT, C_Event.ADD_CAR, lane= i) 
                # increment(25)
                # Event(time, EventType.C_EVENT, C_Event.ADD_CAR, lane = -1)
                # Event(time + random.randint(5,15), EventType.C_EVENT, C_Event.ADD_CAR, lane= 1)
                # Event(time + random.randint(5,15), EventType.C_EVENT, C_Event.ADD_CAR, lane= 4)
                # increment(30)


    def handle_event(self, event : Event):
        if event.action == C_Event.ADD_CAR:
            self.add_car(event.lane)


    

        



