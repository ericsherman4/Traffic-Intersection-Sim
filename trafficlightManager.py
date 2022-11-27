from trafficlight import TrafficLight
import numpy as np
from config import g
from vpython import vector, label
from event import Event, EventType, TL_Event
from math import ceil

class TrafficLightManager:

    def __init__(self):

        # Create 4 traffic lights
        self.lights = np.empty(4, dtype=TrafficLight)
        
        temp_pos = g.roadwidth/2
        positions = [vector(temp_pos,30,-temp_pos/2),
                     vector(-temp_pos/2,30,-temp_pos),
                     vector(-temp_pos,30,temp_pos/2),
                     vector(temp_pos/2,30,temp_pos)]
    


        for i in range(0,4):
            self.lights[i] = TrafficLight(positions[i],90*i)
            if g.show_tl_labels:
                label(pos = positions[i], text=str(i))

        # traffic lights 0 and 2 are together
        # traffic lights 1 and 3 are together

    def generate_events(self, total_duration):

        time = 0

        def increment_postfix(val):
            nonlocal time
            temp = time
            time += val
            return temp

        # start it off
        self.event_target_all_TL(time, TL_Event.RED)

        increment_postfix(g.time_red_overlap)
        while time < total_duration:
            self.event_target_even_TL(increment_postfix(g.time_green), TL_Event.GREEN)
            self.event_target_even_TL(increment_postfix(g.time_yellow), TL_Event.YELLOW)
            self.event_target_even_TL(increment_postfix(g.time_red_overlap), TL_Event.RED)
            self.event_target_odd_TL(increment_postfix(g.time_green), TL_Event.GREEN)
            self.event_target_odd_TL(increment_postfix(g.time_yellow), TL_Event.YELLOW)
            self.event_target_odd_TL(increment_postfix(g.time_red_overlap), TL_Event.RED)

    def event_target_all_TL(self, curr_time, action):
        for i in range(0,4):
            Event(curr_time, EventType.TL_EVENT, action, i)

    def event_target_even_TL(self, curr_time, action):
        Event(curr_time, EventType.TL_EVENT, action, 0)
        Event(curr_time, EventType.TL_EVENT, action, 2)

    def event_target_odd_TL(self, curr_time, action):
        Event(curr_time, EventType.TL_EVENT, action, 1)
        Event(curr_time, EventType.TL_EVENT, action, 3)

    def handle_event(self, event: Event):
        # print(f'id after is {id(event)}')
        self.lights[event.idx].handle_event(event)

    def get_TL_references(self):
        return [self.lights[0], self.lights[1], self.lights[2], self.lights[3]]

    
            


