from vpython import vector,box, arrow, color, compound, rotate,sleep, local_light
from config import g,gtime
import random
from math import pi,sqrt
from pid import PID,PID_Modified


class C_States:
    # spawning is 0 and turn_right is 8
    WAITING, ACCEL, STOPPED, DESPAWNING, CONSTANT_VEL, YIELDING, TURN_LEFT, TURN_RIGHT = range(8)
        

###################################
###### Car Class
###################################

# acceleration profile of a car
# https://www.researchgate.net/figure/Acceleration-profile-of-a-car-according-to-ax_fig5_339600840

# how to make car look nice
# https://groups.google.com/g/vpython-users/c/T3SzNheUOAg

class Car:
    
    def __init__(self, pos :vector, rot_deg, lane, visible):
        random.seed()
        
        # The y position passed in pos vector is ignored and instead offset is used  
        self.offset = g.car_height >> 1

        # Create the car
        # the x z plane is actually the surface of the map, but treating it as x y since its more natural. so y position is being passed in to z parameter for vector
        self.body = box(pos = vector(pos.x, self.offset, pos.z), width = g.car_width, height = g.car_height, length = g.car_length, 
                           color= g.car_colors[random.randint(0,len(g.car_colors)-1)])#, emissive= True)
        # self.lights = local_light(pos=vector(pos.x, self.offset, pos.z), color=color.gray(0.4))
        self.dir = arrow(pos = vector(pos.x, self.offset,pos.z), axis = vector(-g.car_width-8,0,0), color = color.red)
        self.center = arrow(pos = vector(pos.x, 0 , pos.z), axis = vector(0, 15, 0), color = color.white, emissive = True)
        self.error_arrow = arrow(pos = vector(pos.x, 40, pos.z), axis = vector(0,-20,0), color = color.black, shaft_width = 50, head_width = 65)

        self.objects_to_update = [self.center, self.error_arrow]

        # Create compound object and rotate it so its properly orientated in the lane
        self.vehicle = compound([self.body, self.dir], origin = self.body.pos)
        self.vehicle.rotate(angle= rot_deg/180*pi, axis=vector(0,1,0), origin=self.body.pos)

        # Define vehicle kinematics
        self.vel = random.uniform(0,g.car_starting_vel_max)
        self.vel_max = random.uniform(g.car_min_speed, g.car_max_speed)
        self.a = 0
        self.lead_veh_vel = 0
        self.time = 0
        self.lane_pos = None
        self.turn_radius = 13

        # variables for holding the lane direction
        # this is so the car knows what direction to move based on its spawn orientation
        self.xaxis_plus = False
        self.zaxis_plus = False
        self.xaxis_minus = False
        self.zaxis_minus = False

        # determine vehicle direction and set lane_pos
        self.rotation = rot_deg
        self.set_direction_flags(self.rotation)

        # initialize states
        self.pr_state = C_States.WAITING
        self.nx_state = C_States.WAITING

        # variables for vehicle and env state
        self.vehicle.visible = visible
        for obj in self.objects_to_update:
            obj.visible = visible
        self.distance_to_nearest_obj = None
        self.pending_right_turn = False
        self.pending_left_turn = False
        self.execute_event_now = False
        self.lane_identifer = lane

        # setup the PID
        self.pid = PID_Modified(1.1,0.3,2, gtime.delta_t)
        self.pid.set_limits(-random.uniform(1, g.car_max_decel), random.uniform(0.5, g.car_max_accel))

        # TEMP
        self.x = 0
        self.y = 0
        self.abs_ang = 0
        self.rel_ang = 0



    # based on the spawn orientation, determine the the direction that the car is facing.
    # with the spawn direction known, initialize lane position
    def set_direction_flags(self, rot_deg):
        if rot_deg == -90:
            rot_deg = 270
        elif rot_deg == 360:
            rot_deg = 0
        # determine direction
        if rot_deg == 0:
            self.xaxis_plus = True
            self.xaxis_minus = False
            self.zaxis_plus = False
            self.zaxis_minus = False
            self.lane_pos = self.vehicle.pos.x #- g.car_length_div2
        elif rot_deg == 180:
            self.xaxis_plus = False
            self.xaxis_minus = True
            self.zaxis_plus = False
            self.zaxis_minus = False
            self.lane_pos = self.vehicle.pos.x #+ g.car_length_div2
        elif rot_deg == 270:
            self.xaxis_plus = False
            self.xaxis_minus = False
            self.zaxis_plus = True
            self.zaxis_minus = False
            self.lane_pos = self.vehicle.pos.z #- g.car_length_div2
        elif rot_deg == 90:
            self.xaxis_plus = False
            self.xaxis_minus = False
            self.zaxis_plus = False
            self.zaxis_minus = True
            self.lane_pos = self.vehicle.pos.z #+ g.car_length_div2
        
        self.rotation = rot_deg

    # update the position of the car in front if there is one
    # set to zero if there is no car in front.
    def set_lead_vehicle_pos(self, val):
        self.lead_veh_vel = val

    def set_turn_radius(self,val):
        self.turn_radius = val

    # reset the car
    def reset(self, pos):
        self.vehicle.pos = vector(pos.x, self.offset, pos.z)
        self.a = 0
        self.vel = random.uniform(0,g.car_starting_vel_max)
        self.lead_veh_vel = 0
        if self.xaxis_plus or self.xaxis_minus:
            self.lane_pos = self.vehicle.pos.x
        elif self.zaxis_plus or self.zaxis_minus:
            self.lane_pos = self.vehicle.pos.z
        self.distance_to_nearest_obj = None

        # reset the PID
        self.pid.reset()

        # reset the error pointer
        self.error_arrow.visible = False

        # reset all the flags
        self.pending_right_turn = False
        self.pending_left_turn = False
        self.execute_event_now = False

        # reset the state machine
        self.pr_state = C_States.WAITING
        self.nx_state = C_States.WAITING

    # set the car and other objects to be visible
    def visible(self):
        self.vehicle.visible = True
        self.center.visible = True
        # error object should not be visible
        # for obj in self.objects_to_update:
        #     obj.visible = True
        
    # set the car and other objects to be invisible.
    def invisible(self):
        self.vehicle.visible = False
        for obj in self.objects_to_update:
            obj.visible = False

    # update the cars distance to the nearest object (whether the traffic light or another car)
    def update_distances(self,val):
        if val != None and val < 0:
            print(f"ERROR DETECTED: NEAREST OBJ DISTANCE IS NEGATIVE")
            self.error_arrow.visible = True
        self.distance_to_nearest_obj = val

        
    # Run the car's state machine
    def run(self, curr_time):

        # Update next state
        self.pr_state = self.nx_state

        # Car State Machine
        # WAITING, ACCEL, DECEL, STOPPED, CONSTANT_VEL, YIELDING, TURN_LEFT, TURN_RIGHT = range(8)
        if self.pr_state == C_States.WAITING:

            # Determine next state
            if self.vehicle.visible:
                print("leaving waiting state going to accel")
                self.nx_state = C_States.ACCEL

        elif self.pr_state == C_States.ACCEL:

            # Determine next state
            if not self.vehicle.visible:
                self.nx_state = C_States.DESPAWNING
                return
            elif self.pending_left_turn and self.execute_event_now:
                self.nx_state = C_States.TURN_LEFT
                # self.execute_event_now = False # Lane needs to control this because car doesnt have access to the env variables it needs to be able to determine this otherwise
            elif self.pending_right_turn and self.execute_event_now:
                self.nx_state = C_States.TURN_RIGHT
                print("leaving accel state")
                # self.execute_event_now = False


            # determine ideal distances and target velocities
            t_ideal = 1.5
            d_ideal = (t_ideal) * self.vel  + 10 # t_ideal is the desired time gap

            follow_distance = 50
            v_set = g.car_max_speed

            # if the velocity is zero ignore the lead vel velocity.
            # this is prevent the the velocity error from accumulating too high while at the red light.
            if self.vel == 0:
                self.lead_veh_vel = 0

            # if their is no car in front, then pass size of the map in
            # TODO: investigate if this is actually what we want done
            if self.distance_to_nearest_obj == None:
                self.a = self.pid.update(g.size*2, g.size*2, v_set, self.vel)                
            elif self.vel > v_set or (self.vel <= v_set and self.distance_to_nearest_obj > follow_distance):
                # d_error = 0, no distance error so pass distance_to_nearest_obj twice so the target - meas = 0
                # v_error = v_set - self.vel
                self.a = self.pid.update(self.distance_to_nearest_obj, self.distance_to_nearest_obj, v_set, self.vel)
            elif self.lead_veh_vel > v_set:
                # d_error = d_ideal - d_actual #d_actual is the distance to the nears car
                # v_error = g.car_max_speed - self.vel
                self.a = self.pid.update(d_ideal, self.distance_to_nearest_obj, self.lead_veh_vel, self.vel)
            else:
                # d_error = d_ideal - d_actual
                # v_error = g.car_max_speed - self.vel 
                self.a = self.pid.update(d_ideal, self.distance_to_nearest_obj, self.lead_veh_vel, self.vel)


            self.accel_move(curr_time)

        elif self.pr_state == C_States.TURN_RIGHT:

            # somehow need a way to know when we are done turing
            # y = sqrt(r - (x-h)^2) + k
            # y will be whatever direction is straight? 
            # x will be whatever direction turn is 

            # the center pos is constant, its the intersection of the two stop lines.
            
            # generate a general path with with 0,0 as the center

            self.x += 0.5 #TODO: might want to put at end since it never runs with self.x = 0
            if self.x < self.turn_radius:
                self.y = sqrt(self.turn_radius**2 - self.x**2)
            # arrow(pos = vector(self.x, 0, self.y), axis = vector(0,20,0), color= color.red)
            # arrow(pos = vector(self.x_minus, 0, self.y_minus), axis = vector(0,20,0))
            # arrow(pos = vector(self.x, 0, -self.y), axis = vector(0,20,0), color =color.yellow)
            # arrow(pos = vector(-self.x, 0, self.y), axis = vector(0,20,0), color = color.green)
            # arrow(pos = vector(-self.x, 0, -self.y), axis = vector(0,20,0), color = color.orange)
            # bob = arrow(pos = vector(self.x,10,-self.y), axis = vector(8,0,0), color = color.white)
            complete = False
            ang = 0
            if self.x < self.turn_radius:
                ang = self.x / sqrt(self.turn_radius**2 - self.x**2)
                if ang  > pi/2:
                    ang = pi/2
                    complete = True
                    


        
            # bob.rotate(angle = -ang, axis = vector(0,1,0), origin = vector(self.x, bob.pos.y, -self.y))

            

            self.vehicle.pos.x = self.x - 28
            self.vehicle.pos.z = -self.y + 28
            
            self.rel_ang = -(ang - self.abs_ang) #TODO: figure out why this requires a minus sign here

            self.vehicle.rotate(angle = self.rel_ang, axis = vector(0,1,0), origin = self.vehicle.pos)

            self.abs_ang = ang #TODO: probably because youre not storing -ang here? 

            # print(f'abs: {self.abs_ang} rel: {self.rel_ang}')


            if complete:
                self.pending_right_turn = False
                self.execute_event_now = False
                
                # TODO: switch the lane identifer
                # TODO: switch the flags
                print("leaving turn state")
                self.nx_state = C_States.ACCEL



            


            # self.vehicle.make_trail = True
            # # calling z y
            # center = [-28,28]    
            # arrow(pos = vector(center[0], 0, center[1]), axis = vector(0,20,0))

            # self.vehicle.pos.x = self.vehicle.pos.x - 0.5*(curr_time - self.time)
            # self.vehicle.pos.z = sqrt(self.turn_radius**2 - (self.vehicle.pos.x - center[0])**2) + center[1]
            # temp_calc = self.vehicle.pos.x - center[0]
            # deg_to_rotate = (temp_calc) / sqrt(self.turn_radius**2 - (temp_calc**2))
            # self.vehicle.rotate(angle=deg_to_rotate/180*pi, axis =  vector(0,1,0), origin =  self.vehicle.pos)

        elif self.pr_state == C_States.TURN_LEFT:
            pass

            

        elif self.pr_state == C_States.DESPAWNING:
            # dont know if anything is needed here
            # might get rid of this state
            self.nx_state = C_States.WAITING

        elif self.pr_state == C_States.STOPPED:
            pass
        
        # End car state machine

        # update internal time
        self.time = curr_time
            
    # perform a velocity move
    def vel_move(self, curr_time):
        if self.xaxis_plus:
            self.vehicle.pos.x = self.vehicle.pos.x - self.vel*(curr_time - self.time)
            self.lane_pos = self.vehicle.pos.x #- g.car_length_div2
            for obj in self.objects_to_update:
                obj.pos.x = self.lane_pos
        elif self.xaxis_minus:
            self.vehicle.pos.x = self.vehicle.pos.x + self.vel*(curr_time - self.time)
            self.lane_pos = self.vehicle.pos.x #+ g.car_length_div2
            for obj in self.objects_to_update:
                obj.pos.x = self.lane_pos
        elif self.zaxis_plus:
            self.vehicle.pos.z = self.vehicle.pos.z - self.vel*(curr_time - self.time)
            self.lane_pos = self.vehicle.pos.z #- g.car_length_div2
            for obj in self.objects_to_update:
                obj.pos.z = self.lane_pos
        elif self.zaxis_minus:
            self.vehicle.pos.z = self.vehicle.pos.z + self.vel*(curr_time - self.time)
            self.lane_pos = self.vehicle.pos.z #+ g.car_length_div2
            for obj in self.objects_to_update:
                obj.pos.z = self.lane_pos

    # perform an acceleration move
    def accel_move(self, curr_time):
        # update velocity using acceleration
        self.vel = self.vel + self.a*(curr_time - self.time)
        
        # perform velocity limit checks
        if self.vel > self.vel_max:
            self.vel = self.vel_max
        elif self.vel < 0:
            self.vel = 0

        # call velocity move
        self.vel_move(curr_time)
