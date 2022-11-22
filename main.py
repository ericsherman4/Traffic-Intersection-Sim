from config import g
from vpython import *
from env import Env, Axes
from trafficlight import TrafficLight
from car import Car
from carManager import CarManager
import time
from trafficlightManager import TrafficLightManager
from event import Event, EventType, TL_Event


def sim_main():
    scene = canvas(width = 800, height = 500)
    scene.background = vector(0.25,0.25,0.25)
    # scene.autoscale = False
    scene.forward = vector(0.534283, -0.620986, -0.573514)
    scene.camera.pos = vector(-43.8146, 41.232, 50.8608)
    scene.center = vector(-0.62705, -8.96404, 4.50215)
    scene.range = 46.668804816827986

    # Create axes for direction visualization
    Axes()

    L = label(pos=vector(0,2,0), text="waiting to start")
    perf_label = label(pos=vector(-100,2,100), text="waiting for clock")

    cmgr = CarManager() # car manager instantiates the env
    for i in range(0,8):
        cmgr.add_car(i)

    # create time class?
    t = 0
    delta_t = 0.1
    total_time = 100

    start_time = 0
    end_time = 0

    cycles = 0
    dynam_rate = 50
    completion_time_ms = 1

    # create traffic light manager and generate events
    lmgr = TrafficLightManager()
    lmgr.generate_events(total_time)

    # variables for handling events in the sim loop
    next_event = None
    executed_event = True

    while(t < total_time):

        start_time = time.perf_counter()
        cycles+=1

        # limit the rate of the while loop
        # rate(dynam_rate) # input is frequency, loop time is 1/f
        rate(40)


        # L.text = str(t)

        cmgr.run(t)

        # event fetch
        if executed_event:
            next_event = Event.q.get()
            executed_event = False        
        
        #event execute
        if t >= next_event.time:
            if next_event.event_type == EventType.TL_EVENT:
                # print(f'id before is {id(next_event)}')
                lmgr.handle_event(next_event)
            executed_event = True



        # increment sim time
        t += delta_t

        end_time = time.perf_counter()
        if cycles % 50 == 0:
            completion_time_ms = int(end_time*10**3) - int(start_time*10**3)
            perf_label.text = "comp" + str(completion_time_ms) + "\n dynam rate:" + str(dynam_rate) 
            if completion_time_ms != 0:
                dynam_rate = 1000//completion_time_ms











def sim_graphics_test():

    scene = canvas(width = 800, height = 500)
    scene.background = vector(0.25,0.25,0.25)
    print("running")
    box()
    sleep(0.5)

    iada = Car(40,40)

    # for i in range(0,100000):
    #     if i%5000 == 0:
    #         print("running")
    #     vect = vector.random()
    #     thing = Car(vect.x*100, vect.y*100)
    #     del thing




    


        

