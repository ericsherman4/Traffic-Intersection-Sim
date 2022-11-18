from vpython import vector,box, arrow, color
from config import g
import random


class C_States:
    # spawning is 0 and turn_right is 8
    SPAWNING, ACCEL, DECEL, STOPPED, DESPAWNING, CONSTANT_VEL, YIELDING, TURN_LEFT, TURN_RIGHT = range(9)
        

###################################
###### Car Class
###################################

# acceleration profile of a car
# https://www.researchgate.net/figure/Acceleration-profile-of-a-car-according-to-ax_fig5_339600840

# how to make car look nice
# https://groups.google.com/g/vpython-users/c/T3SzNheUOAg

class Car:
    # the y position passed in for pos is ignored  
    def __init__(self, pos :vector, visible):
        offset = g.car_height >> 1
        # the x z plane is actually the surface of the map, but treating it as x y since its more natural. so y position is being passed in to z parameter for vector
        self.vehicle = box(pos = vector(pos.x, offset,pos.y), width = g.car_width, height = g.car_height, length = g.car_length, 
                           color= g.car_colors[random.randint(0,len(g.car_colors)-1)])
        self.dir = arrow(pos = vector(pos.x, offset,pos.y), axis = vector(-g.car_width-8,0,0), color = color.red)

        # self.pr_sate = self.nx_state = C_States.SPAWNING
        self.pr_sate = self.nx_state = C_States.CONSTANT_VEL
        self.vehicle.visible = visible

        # print(C_States.SPAWNING, C_States.TURN_RIGHT)


    # def __del__(self):
        # https://www.glowscript.org/docs/VPythonDocs/delete.html
        # Note vpython objects cannot be deleted from memory 
        # (and still rendered, even if you call del on the object)
        # print("I have been deleted!")
        # self.vehicle.visible= False

    # cool idea, arrow is a velocity arrow that shrinks and grows based on the velocity? 

    def visible(self):
        self.vehicle.visible = True

    def invisible(self):
        self.vehicle.visible = False

    def run(self):
        
        if self.pr_state == C_States.SPAWNING:
            # idk what logic should go here
            pass

    

