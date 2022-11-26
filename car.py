from vpython import vector,box, arrow, color, compound, rotate,sleep, local_light
from config import g,gtime
import random
from math import pi
from pid import PID,PID_Modified


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
        self.offset = g.car_height >> 1
        # the x z plane is actually the surface of the map, but treating it as x y since its more natural. so y position is being passed in to z parameter for vector
        self.body = box(pos = vector(pos.x, self.offset, pos.z), width = g.car_width, height = g.car_height, length = g.car_length, 
                           color= g.car_colors[random.randint(0,len(g.car_colors)-1)], emissive= True)
        # self.lights = local_light(pos=vector(pos.x, self.offset, pos.z), color=color.gray(0.4))
        self.dir = arrow(pos = vector(pos.x, self.offset,pos.z), axis = vector(-g.car_width-8,0,0), color = color.red)
        self.center = arrow(pos = vector(pos.x, 0 , pos.z), axis = vector(0, 15, 0), color = color.white, emissive = True)

        # Create compound object and rotate it so its properly orientated in the lane
        self.vehicle = compound([self.body, self.dir], origin = self.body.pos)
        self.vehicle.rotate(angle= rot_deg/180*pi, axis=vector(0,1,0), origin=self.body.pos)

        # define vehicle properties
        self.vel = random.uniform(0,g.car_starting_vel-2) # potentially pass then in later as a different thing or make it random
        self.vel_max = random.uniform(g.car_min_speed, g.car_max_speed)
        self.acc = 0
        self.lead_veh_vel = 0
        self.time = 0
        self.lane_pos = None

        # determine vehicle direction and set lane_pos
        self.set_direction_flags(rot_deg)


        # initialize states
        self.pr_state = C_States.WAITING
        self.nx_state = C_States.WAITING

        # variables for vehicle and env state
        self.vehicle.visible = visible
        self.center.visible = visible
        # self.lights.visible = visible
        self.distance_to_nearest_car = None
        # self.prev_distance_to_nearest_car = None
        # self.delta_distance = None # difference of distance to nearest car variables between two time steps
        # self.safe_travel_distance = None    # based on cars speed
        self.prev_derror = None

        self.pid = PID_Modified(1.1,0.3,2, gtime.delta_t)
        self.pid.set_limits(-random.uniform(1, g.car_max_decel), random.uniform(0.5, g.car_max_accel))


    def set_direction_flags(self, rot_deg):
        # determine direction
        self.xaxis_plus = False
        self.zaxis_plus = False
        self.xaxis_minus = False
        self.zaxis_minus = False

        if rot_deg == 0:
            self.xaxis_plus = True
            self.lane_pos = self.vehicle.pos.x #- g.car_length_div2
        elif rot_deg == 180:
            self.xaxis_minus = True
            self.lane_pos = self.vehicle.pos.x #+ g.car_length_div2
        elif rot_deg == 270:
            self.zaxis_plus = True
            self.lane_pos = self.vehicle.pos.z #- g.car_length_div2
        elif rot_deg == 90:
            self.zaxis_minus = True
            self.lane_pos = self.vehicle.pos.z #+ g.car_length_div2

    def set_lead_vehicle_pos(self, val):
        self.lead_veh_vel = val

    def reset_pos(self, pos):
        self.vehicle.pos = vector(pos.x, self.offset, pos.z)

    def visible(self):
        self.vehicle.visible = True
        self.center.visible = True
        # self.lights.visible = True

    def invisible(self):
        self.vehicle.visible = False
        self.center.visible = False
        # self.lights.visible = False

    def update_distances(self,val):
        # self.prev_distance_to_nearest_car = self.distance_to_nearest_car
        self.distance_to_nearest_car = val

        # if self.distance_to_nearest_car == None or val == None:
            # self.delta_distance = None
        # elif self.prev_distance_to_nearest_car == None:
            # self.delta_distance = None
        # else:
            # self.delta_distance = abs(self.distance_to_nearest_car \
                # - self.prev_distance_to_nearest_car)

        # print(self.distance_to_nearest_car)

    def run(self, curr_time):

        # Update next state
        self.pr_state = self.nx_state

        # maybe break this out into an update state variable
        # no veloicty, safe travel distnace = 4
        # each increase in 5 vel from there, means plus 1.5 in safe travel distance
        # self.safe_travel_distance = self.vel*4 + 4
        

        # Car State Machine
        # WAITING, ACCEL, DECEL, STOPPED, DESPAWNING, CONSTANT_VEL, YIELDING, TURN_LEFT, TURN_RIGHT = range(9)
        if self.pr_state == C_States.WAITING:
            if self.vehicle.visible:
                self.nx_state = C_States.ACCEL

        elif self.pr_state == C_States.ACCEL:

            if not self.vehicle.visible:
                self.nx_state = C_States.DESPAWNING
                return

            # d_actual = self.distance_to_nearest_car
            t_ideal = 1.5
            d_ideal = (t_ideal) * self.vel  + 10 # t_ideal is the desired time gap
            # d_error = d_ideal - d_actual
            
            # velocity error is also used
            # so I need to take derivative of d_error
            # v_error = (d_error - self.prev_derror) * (curr_time - self.time)

            follow_distance = 50
            v_set = g.car_max_speed
            a = 0

            if self.vel == 0:
                self.lead_veh_vel = 0

            if self.distance_to_nearest_car == None:
                a = self.pid.update(g.size*2, g.size*2, v_set, self.vel)
                
            elif self.vel > v_set or (self.vel <= v_set and self.distance_to_nearest_car > follow_distance):
                # d_error = 0
                # v_error = v_set - self.vel
                a = self.pid.update(self.distance_to_nearest_car, self.distance_to_nearest_car, v_set, self.vel)
            elif self.lead_veh_vel > v_set: #TODO: THIS IS TEMP, g.car_max_speed is target velocity which im assuming is the cars in fronts vel, NEEDS TO BE CHANGED!
                # d_error = d_ideal - d_actual
                # v_error = g.car_max_speed - self.vel
                a = self.pid.update(d_ideal, self.distance_to_nearest_car, self.lead_veh_vel, self.vel)
            else:
                # d_error = d_ideal - d_actual
                # v_error = g.car_max_speed - self.vel 
                a = self.pid.update(d_ideal, self.distance_to_nearest_car, self.lead_veh_vel, self.vel)

            
            self.accel_move(curr_time, a)
            # print(f'acc: {a}, vel: {self.vel}')







        # elif self.pr_state == C_States.ACCEL:
        #     # Check if the car was despawned
        #     if not self.vehicle.visible:
        #         self.nx_state = C_States.DESPAWNING
        #         return

        #     # some logic here for checking traffic light or cars in front
        #     if self.distance_to_nearest_car != None:
        #         if self.safe_travel_distance < self.distance_to_nearest_car:
        #             self.nx_state = C_States.DECEL


        #     if self.vel < g.car_max_speed:
        #         self.accel_move(curr_time,g.car_accel)
        #         self.nx_state = C_States.ACCEL
        #     else:
        #         self.nx_state = C_States.CONSTANT_VEL


        # elif self.pr_state == C_States.CONSTANT_VEL:
        #     # Check if the car was despawned
        #     if not self.vehicle.visible:
        #         self.nx_state = C_States.DESPAWNING
        #         return 

        #     # perform velocity move
        #     self.vel_move(curr_time)

        #     # determine next state
        #     if self.distance_to_nearest_car != None:
        #         # print(f'{self.safe_travel_distance} and {self.distance_to_nearest_car}')
        #         if self.safe_travel_distance > self.distance_to_nearest_car:
        #             self.nx_state = C_States.DECEL
        #     else:
        #         self.nx_state = C_States.CONSTANT_VEL    

            
            

        # elif self.pr_state == C_States.DECEL:
        #     # map will return a positive value, need to negate to get negative acceleration
        #     # print("entered state decel")
        #     if self.delta_distance == None:
        #         self.nx_state = C_States.ACCEL
        #         return

        #     a = self.map(self.delta_distance*2.5, 0, self.safe_travel_distance/4, 0, g.car_max_decel)
        #     self.accel_move(curr_time, -a)
        #     print(f'{self.delta_distance*2}, 0, {self.safe_travel_distance/4}, 0, {g.car_max_decel} and accel is: {a} and new v is {self.vel}')

        #     if(self.vel <= 0.1):
        #         self.vel = 0
        #         self.nx_state = C_States.STOPPED
            

        elif self.pr_state == C_States.DESPAWNING:
            # dont know if anything is needed here
            # might get rid of this state
            self.nx_state = C_States.WAITING

        # elif self.pr_state == C_States.STOPPED:
        #     print("in stopped state")
        

        # update internal time
        self.time = curr_time
            
    def vel_move(self, curr_time):
        if self.xaxis_plus:
            self.vehicle.pos.x = self.vehicle.pos.x - self.vel*(curr_time - self.time)
            self.lane_pos = self.vehicle.pos.x #- g.car_length_div2
            self.center.pos.x = self.lane_pos
            # self.lights.pos.x = self.lane_pos
        elif self.xaxis_minus:
            self.vehicle.pos.x = self.vehicle.pos.x + self.vel*(curr_time - self.time)
            self.lane_pos = self.vehicle.pos.x #+ g.car_length_div2
            self.center.pos.x = self.lane_pos
            # self.lights.pos.x = self.lane_pos
        elif self.zaxis_plus:
            self.vehicle.pos.z = self.vehicle.pos.z - self.vel*(curr_time - self.time)
            self.lane_pos = self.vehicle.pos.z #- g.car_length_div2
            self.center.pos.z = self.lane_pos
            # self.lights.pos.z = self.lane_pos
        elif self.zaxis_minus:
            self.vehicle.pos.z = self.vehicle.pos.z + self.vel*(curr_time - self.time)
            self.lane_pos = self.vehicle.pos.z #+ g.car_length_div2
            self.center.pos.z = self.lane_pos
            # self.lights.pos.z = self.lane_pos


    def accel_move(self, curr_time, a):
        self.vel = self.vel + a*(curr_time - self.time)
        
        # if self.vel > g.car_max_speed:
        #     self.vel = g.car_max_speed
        if self.vel > self.vel_max:
            self.vel = self.vel_max
        elif self.vel < 0:
            self.vel = 0
        self.vel_move(curr_time)

    # unused
    def map(self,val, min_range1, max_range1, min_range2, max_range2):
        if (max_range1 - min_range1) == 0 or val == None:
            return 0
        
        if val > max_range1:
            val = max_range1
        if val < min_range1:
            val = min_range1

        # Borrowed from https://www.arduino.cc/reference/en/language/functions/math/map/ and translated to python
        return (val - min_range1)*(max_range2 - min_range2) / (max_range1 - min_range1) + min_range2


        


            

    

