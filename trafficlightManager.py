from trafficlight import TrafficLight
import numpy as np
from config import g
from vpython import vector
from event import Event, EventType, TL_Event
from math import ceil

class TrafficLightManager:

    def __init__(self):

        # Create 4 traffic lights
        self.lights = np.empty(4, dtype=TrafficLight)
        
        temp_pos = g.roadwidth/2
        self.lights[0] = TrafficLight(vector(temp_pos,20,-temp_pos/2),0)
        self.lights[1] = TrafficLight(vector(-temp_pos/2,20,-temp_pos),90)
        self.lights[2] = TrafficLight(vector(-temp_pos,20,temp_pos/2),180)
        self.lights[3] = TrafficLight(vector(temp_pos/2,20,temp_pos),270)

        # traffic lights 0 and 2 are together
        # traffic lights 1 and 3 are together

    def generate_events(self, total_duration):

        # start it off
        self.event_target_all_TL(0, TL_Event.RED)

        time = g.time_red_overlap
        while time < total_duration:
            self.event_target_even_TL(time, TL_Event.GREEN)
            time += g.time_green
            self.event_target_even_TL(time, TL_Event.YELLOW)
            time += g.time_yellow
            self.event_target_even_TL(time, TL_Event.RED)
            time += g.time_red_overlap
            self.event_target_odd_TL(time, TL_Event.GREEN)
            time += g.time_green
            self.event_target_odd_TL(time, TL_Event.YELLOW)
            time += g.time_yellow
            self.event_target_odd_TL(time, TL_Event.RED)
            time += g.time_red_overlap

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

    
            


