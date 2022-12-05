import numpy as np
from config import g
from env import Env
import random
from event import Event, C_Event, EventType
from lane import Lane


class CarManager:
    
    def __init__(self):

        # Create an array to store the lane objects
        self.num_lanes = 8
        self.lanes = np.empty(self.num_lanes,dtype=Lane)

        # Instantiate the environment
        self.env = Env()

        # Used for generating the lanes, specifies the degree to rotate the car
        # based on what lane it's in
        self.car_rot = [180, 180, 0, 0, 270, 270, 90, 90]
        
        # Generate the lanes
        for i in range(0,self.num_lanes):
            self.lanes[i] = Lane(i, g.max_cars ,g.max_cars_on_road,
                                 self.env.lane_pos_start[i], 
                                 self.env.lane_pos_end[i],
                                 self.env.stop_line_position[i],
                                 self.car_rot[i])

        self.turn_right_map = {0:7, 4:0, 3:4, 7:3}
        self.turn_left_map = {1:5, 5:2, 2:6, 6:1}


    # Run the car manager state machine.
    def run(self, curr_time):

        # Check each lane
        for lane in self.lanes:

            lane.check_bounds()                 # Check location of lane lead car
            lane.update_closest_distance()      # Update nearest obstacle for every car
            lane.update_lead_veh_vel()          # Update lead car vel for all cars
            lane.check_for_turn_events()        # Check for when a car needs to turn

            result = False

            for i in range (0, self.num_lanes):

                if self.lanes[i].turn_event_trigger:
                    self.lanes[i].turn_event_trigger = False

                    # print(f"TRIGGER BY LANE {i}")

                    # i need the car to move and position where to insert it? 
                    if self.lanes[i].turn_event_dir == C_Event.TURN_RIGHT:
                        # print(f"current lane: {i}")
                        # print(f" destination lane: {self.turn_right_map[i]}")
                        idx = self.lanes[self.turn_right_map[i]].get_idx_to_insert()
                        # print(f"insertation index is : {idx}")
                        car_idx_og_lane = self.lanes[i].turn_event_car_idx
                        # print(f"car_idx_og_lane is {car_idx_og_lane}")
                        result = self.lanes[self.turn_right_map[i]].insert(idx, self.lanes[i].cars[car_idx_og_lane])
                        if result:
                            # print("SUCCESSFULLY INSERTED")
                            # print(f"start_ptr {self.lanes[i].start_ptr} and end_ptr{self.lanes[i].end_ptr} and cars on road {self.lanes[i].cars_on_road}")
                            result = self.lanes[i].remove(car_idx_og_lane)
                            if result: 
                                pass
                                # print("REMOVED SUCESSFULLY")
                            else: 
                                print("FAILED TO REMOVE")
                        else:
                            print("FAILED TO INSERT")
                    elif self.lanes[i].turn_event_dir == C_Event.TURN_LEFT:
                        print("not implemented yet!!!!!!!!!!!!!!!!!!!!!!!!!")

            # if lane.identifier == 7:
            #     print(self.lanes[7].cars[0].vehicle.pos)

            # Run all the car state machines
            for car in lane.cars:
                car.run(curr_time)
    
    # Add a car to a lane. If idx is not specified, a random lane is picked.
    def add_car(self, idx = -1 ):
        if idx == -1:
            self.lanes[random.randint(0,self.num_lanes-1)].activate()
        elif idx >= 0 and idx < (self.num_lanes):
            self.lanes[idx].activate()
        else:
            print("INVALID INDEX IN ADD_CAR()")

    # Store all the traffic light references so that each lane can see traffic light state
    def set_TL_references(self, TLs : list):
        self.lanes[0].set_TL_reference(TLs[2])
        self.lanes[1].set_TL_reference(TLs[2])
        self.lanes[2].set_TL_reference(TLs[0])
        self.lanes[3].set_TL_reference(TLs[0])
        self.lanes[4].set_TL_reference(TLs[3])
        self.lanes[5].set_TL_reference(TLs[3])
        self.lanes[6].set_TL_reference(TLs[1])
        self.lanes[7].set_TL_reference(TLs[1])

    # Generate simulation events and place on the global queue.
    def generate_events(self, use_random = False, total_duration = -1):

        print("total_duration not implemented")
        time = 0

        # Define an increment function to allow for more readable code
        def increment_prefix(val):
            nonlocal time
            time += val
            return time
        
        # If use_random is False, use manually generated events, otherwise, use random.
        if not use_random:
            # THERE IS NO ERROR CHECKING. MUST ENSURE A CAR IS ONLY GIVEN ONE TURN COMMAND IN ITS LIFE
            Event(increment_prefix(0), EventType.C_EVENT, C_Event.ADD_CAR, lane = 0)
            Event(increment_prefix(10), EventType.C_EVENT, C_Event.ADD_CAR, lane = 0)
            Event(increment_prefix(1), EventType.C_EVENT, C_Event.TURN_RIGHT, idx=1, lane = 0)
            Event(increment_prefix(15), EventType.C_EVENT, C_Event.ADD_CAR, lane = 0)
            Event(increment_prefix(1), EventType.C_EVENT, C_Event.TURN_RIGHT, idx=2, lane = 0)
            Event(increment_prefix(1), EventType.C_EVENT, C_Event.ADD_CAR, lane = 7)
            Event(increment_prefix(20), EventType.C_EVENT, C_Event.ADD_CAR, lane = 0)
            Event(increment_prefix(1), EventType.C_EVENT, C_Event.TURN_RIGHT, idx=3, lane = 0)
            Event(increment_prefix(15), EventType.C_EVENT, C_Event.ADD_CAR, lane = 7)
            # Event(increment_prefix(10), EventType.C_EVENT, C_Event.ADD_CAR, lane = 7)
            # Event(increment_prefix(10), EventType.C_EVENT, C_Event.ADD_CAR, lane = 7)
            # Event(increment_prefix(20), EventType.C_EVENT, C_Event.ADD_CAR, lane = 0)
            # Event(increment_prefix(20), EventType.C_EVENT, C_Event.ADD_CAR, lane = 0)
            # Event(increment_prefix(15), EventType.C_EVENT, C_Event.ADD_CAR, lane = 0)
            # Event(increment_prefix(10), EventType.C_EVENT, C_Event.ADD_CAR, lane = 0)
            # Event(increment_prefix(10), EventType.C_EVENT, C_Event.ADD_CAR, lane = 0)
        else:
            # Generate for each lane one at a time.

            # TODO: generate probability of about 0.7 or 0.8 for NOT turning.

            for i in range(0,self.num_lanes):
                time = 0
                for j in range(0,15):
                    Event(increment_prefix(random.randint(10,23)), EventType.C_EVENT, C_Event.ADD_CAR, lane = i)

    # Handle a car event
    def handle_event(self, event : Event):
        if event.action == C_Event.ADD_CAR:
            self.add_car(event.lane)
        elif event.action == C_Event.TURN_RIGHT or event.action == C_Event.TURN_LEFT:
            self.handle_turn_event(event.lane, event.idx, event.action)

    def handle_turn_event(self, lane, idx, action):
        if idx == -1:
            self.lanes[lane].handle_turn_event(random.randint(0, self.num_lanes-1), action)
        elif idx >= 0 and idx < (self.num_lanes):
            self.lanes[lane].handle_turn_event(idx, action)
        else:
            print("INVALID INDEX IN HANDLE_TURN_EVENT()")



    

        



