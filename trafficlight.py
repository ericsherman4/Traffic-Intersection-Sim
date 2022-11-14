from vpython import *
from config import g
import copy
import time

class trafficlight:
    
    def __init__(self, pos, rotation):
        # yellow enclosure of the traffic light
        self.frame = box(pos = pos, height = g.tl_height, width = g.tl_width, length = g.tl_length, color= color.yellow)
        temp_pos = copy.deepcopy(self.frame.pos)
        temp_pos.y += g.tl_height/2-g.tl_height/6
        self.top = cylinder(pos = temp_pos, color= color.orange, axis = vector(g.tl_width/2+1.3,0,0), radius = g.light_radius)
        temp_pos.y -= g.tl_height/6*2
        self.mid = cylinder(pos = temp_pos, color= color.orange, axis = vector(g.tl_width/2+1.3,0,0), radius = g.light_radius)
        temp_pos.y -= g.tl_height/6*2
        self.bot = cylinder(pos = temp_pos, color= color.orange, axis = vector(g.tl_width/2+1.3,0,0), radius = g.light_radius)
        
        # set them all to emit light
        self.mid.emissive = True
        self.top.emissive = True
        self.bot.emissive = True
        
        #https://www.glowscript.org/docs/VPythonDocs/lights.html
        #https://www.glowscript.org/docs/VPythonDocs/extrusion.html
        
    
    def test(self):
        self.mid.color = vector(1,0,0)
        sleep(2)
        self.mid.color = vector(0,1,0)
        sleep(2)
        self.mid.color = vector(1,1,0)
        sleep(2)
        self.mid.emissive= False
        sleep(2)
        self.mid.color = vector(0,0,0)
        sleep(2)