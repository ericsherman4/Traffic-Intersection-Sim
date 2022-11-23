from vpython import *
from config import g
from math import pi
import copy
import time
from event import EventType, Event, TL_Event


class TrafficLight:
    
    def __init__(self, pos, rotation_deg):
        # create yellow enclosure of the traffic light
        self.frame = box(pos = pos, height = g.tl_height, width = g.tl_width, length = g.tl_length, color= color.yellow)
        
        # make the lights (cylinders)
        # this position will be the center of the frame object (box)
        offset_height = g.tl_height/6
        light_length = 1.3  # length of the cylinder that sticks out from the yellow frame 
                            # this is only the length from the yellow frame to end of cylinder
        temp_pos = copy.deepcopy(self.frame.pos)
        temp_pos.y += g.tl_height/2-offset_height
        self.top = cylinder(pos = temp_pos, color= color.black, axis = vector(g.tl_width/2+light_length,0,0), radius = g.light_radius)
        temp_pos.y -= offset_height*2
        self.mid = cylinder(pos = temp_pos, color= color.black, axis = vector(g.tl_width/2+light_length,0,0), radius = g.light_radius)
        temp_pos.y -= offset_height*2
        self.bot = cylinder(pos = temp_pos, color= color.black, axis = vector(g.tl_width/2+light_length,0,0), radius = g.light_radius)
        
        # Set the lights to glow
        # https://www.glowscript.org/docs/VPythonDocs/lights.html
        self.mid.emissive = self.top.emissive = self.bot.emissive = True

        #calculate center abs pos for the traffic light (for rotations)
        self.center_pos = pos + vector(light_length/2,0,0)

        # Apply rotation
        self.rotation = 0
        self.rotate(rotation_deg)
        
        # Other member variables
        self.pr_state = TL_Event.HALTED
        self.nx_state = TL_Event.HALTED
        
    def translate(self, newpos : vector):
        # find distance from new vs old pos
        diff = newpos-self.frame.pos
        diff_vector = mag(diff)*norm(diff)

        # complete the offsets
        self.frame.pos = newpos
        self.top.pos += diff_vector
        self.mid.pos += diff_vector
        self.bot.pos += diff_vector

        # update center_pos
        self.center_pos += diff_vector

    def rotate(self, abs_deg):
        # find difference in abs_deg from current
        diff_deg = abs_deg - self.rotation

        # apply rotation
        angle_rad = diff_deg/180*pi
        y_axis = vector(0,1,0)
        self.frame.rotate(angle=angle_rad, axis=y_axis, origin=self.center_pos)
        self.top.rotate(angle=angle_rad, axis=y_axis, origin=self.center_pos)
        self.mid.rotate(angle=angle_rad, axis=y_axis, origin=self.center_pos)
        self.bot.rotate(angle=angle_rad, axis=y_axis, origin=self.center_pos)

        # update rotation
        self.rotation = abs_deg

    def handle_event(self, event : Event):
        # print(f'id inside the TL class is {id(event)}')
        self.nx_state = event.action
        # print(f'time is {event.time} and nx_action is {event.action}')
        self.run()

    def run(self):

        # Update next state
        self.pr_state = self.nx_state

        # TL Event State Machine
        if self.pr_state == TL_Event.GREEN:
            self.top.color = color.black
            self.bot.color = color.green

        elif self.pr_state == TL_Event.YELLOW:
            self.bot.color = color.black
            self.mid.color = color.yellow

        elif self.pr_state == TL_Event.RED:
            self.mid.color = color.black
            self.top.color = color.red

        elif self.pr_state == TL_Event.HALTED:
            # dead state
            pass

    def get_state(self):
        return self.pr_state
