from vpython import vector,box, arrow, color, compound, rotate,sleep
from config import g
import random
from math import pi


class C_States:
    # spawning is 0 and turn_right is 8
    WAITING, ACCEL, DECEL, STOPPED, DESPAWNING, CONSTANT_VEL, YIELDING, TURN_LEFT, TURN_RIGHT = range(9)
        

###################################
###### Car Class
###################################

# acceleration profile of a car
# https://www.researchgate.net/figure/Acceleration-profile-of-a-car-according-to-ax_fig5_339600840

# how to make car look nice
# https://groups.google.com/g/vpython-users/c/T3SzNheUOAg

class Car:
    # the y position passed in for pos is ignored  
    def __init__(self, pos :vector, rot_deg, visible):
        offset = g.car_height >> 1
        # the x z plane is actually the surface of the map, but treating it as x y since its more natural. so y position is being passed in to z parameter for vector
        self.body = box(pos = vector(pos.x, offset, pos.z), width = g.car_width, height = g.car_height, length = g.car_length, 
                           color= g.car_colors[random.randint(0,len(g.car_colors)-1)])
        self.dir = arrow(pos = vector(pos.x, offset,pos.z), axis = vector(-g.car_width-8,0,0), color = color.red)

        self.body.rotate(angle=rot_deg/180*pi, axis = vector(0,1,0), origin=self.body.pos)
        self.dir.rotate(angle=rot_deg/180*pi, axis = vector(0,1,0), origin=self.body.pos)
        self.vehicle = compound([self.body, self.dir], origin = self.body.pos)
        # self.vehicle.rotate(angle= rot_deg/180*pi, axis=vector(0,20,0), origin=self.body.pos)
        # self.vehicle.axis= rotate(self.vehicle.axis, angle = pi, axis=vector(0,1,0))
        self.vehicle.visible = visible

        # define vehicle properties
        self.vel = g.car_starting_vel # potentially pass then in later as a different thing or make it random
        self.acc = g.car_accel
        self.time = 0

        # determine vehicle direction
        self.set_direction_flags(rot_deg)

        # initialize states
        self.pr_state = C_States.ACCEL
        self.nx_state = C_States.ACCEL

        # print(C_States.SPAWNING, C_States.TURN_RIGHT)

    # cool idea, arrow is a velocity arrow that shrinks and grows based on the velocity? 

    def set_direction_flags(self, rot_deg):
        # determine direction
        self.xaxis_plus = False
        self.zaxis_plus = False
        self.xaxis_minus = False
        self.zaxis_minus = False

        if rot_deg == 0:
            self.xaxis_plus = True
        elif rot_deg == 180:
            self.xaxis_minus = True
        elif rot_deg == 270:
            self.zaxis_plus = True
        elif rot_deg == 90:
            self.zaxis_minus = True


    def visible(self):
        self.vehicle.visible = True

    def invisible(self):
        self.vehicle.visible = False

    def run(self, curr_time):

        # Update next state
        self.pr_state = self.nx_state

        # Car State Machine
        # WAITING, ACCEL, DECEL, STOPPED, DESPAWNING, CONSTANT_VEL, YIELDING, TURN_LEFT, TURN_RIGHT = range(9)
        if self.pr_state == C_States.WAITING:
            if self.vehicle.visible:
                self.nx_state = C_States.ACCEL

        elif self.pr_state == C_States.ACCEL:
            # Check if the car was despawned
            if not self.vehicle.visible:
                self.nx_state = C_States.DESPAWNING
                return

            # some logic here for checking traffic light or cars in front

            if self.vel < g.car_max_speed:
                self.accel_move(curr_time)
                self.nx_state = C_States.ACCEL
            else:
                self.nx_state = C_States.CONSTANT_VEL


        elif self.pr_state == C_States.CONSTANT_VEL:
            # Check if the car was despawned
            if not self.vehicle.visible:
                self.nx_state = C_States.DESPAWNING
                return 

            self.vel_move(curr_time)
            self.nx_state = C_States.CONSTANT_VEL

        elif self.pr_state == C_States.DESPAWNING:
            # dont know if anything is needed here
            self.nx_state = C_States.WAITING
        

        # update internal time
        self.time = curr_time
            
    def vel_move(self, curr_time):
        if self.xaxis_plus:
            self.vehicle.pos.x = self.vehicle.pos.x - self.vel*(curr_time - self.time)
        elif self.xaxis_minus:
            self.vehicle.pos.x = self.vehicle.pos.x + self.vel*(curr_time - self.time)
        elif self.zaxis_plus:
            self.vehicle.pos.z = self.vehicle.pos.z - self.vel*(curr_time - self.time)
        elif self.zaxis_minus:
            self.vehicle.pos.z = self.vehicle.pos.z + self.vel*(curr_time - self.time)

    def accel_move(self, curr_time):
        self.vel = self.vel + self.acc*(curr_time - self.time)
        self.vel_move(curr_time)


        


            

    

