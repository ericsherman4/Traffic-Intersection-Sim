from config import g, gtime
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

    distant_light(direction=vector(0.4,1,0.7), color=color.gray(0.17))
    # scene.lights = []
    scene.ambient = color.gray(0.2)

    # scene.lights = []

    # Create axes for direction visualization
    # Axes()

    L = label(pos=vector(0,100,0), text="generating cars objects")
    perf_label = label(pos=vector(-100,2,100), text="waiting for clock")

    cmgr = CarManager() # car manager instantiates the env
    L.text = "adding cars and generating traffic lights"

    # create time class?
    t = 0
    delta_t = gtime.delta_t
    total_time = 400

    start_time = 0
    end_time = 0

    cycles = 0
    dynam_rate = 50
    completion_time_ms = 1

    # create traffic light manager and generate events
    lmgr = TrafficLightManager()
    lmgr.generate_events(total_time)

    # give carmanager awareness of traffic lights
    cmgr.set_TL_references(lmgr.get_TL_references())
    cmgr.generate_events(True)

    # variables for handling events in the sim loop
    next_event = None
    executed_event = True

    print("make sure to fix max vel they are not random")
    print("ADD A THING WHERE THE RUN YELLOW IS BASED ON DISTANCE TO LIGHT AND ALSO THE SPEED!")
    print("add dynamic v_set setting? ")

    while(t < total_time):

        start_time = time.perf_counter()
        cycles+=1

        # limit the rate of the while loop
        # rate(dynam_rate) # input is frequency, loop time is 1/f
        rate(40)


        L.text = str(round(t,2))

        cmgr.run(t)
               
        while True:
            if executed_event:
                if Event.q.qsize() != 0:
                    next_event = Event.q.get(block=False)
                else:
                    break
                executed_event = False 
            if t >= next_event.time:
                if next_event.event_type == EventType.TL_EVENT:
                    lmgr.handle_event(next_event)
                    # print("ran event handlers")
                    
                elif next_event.event_type ==EventType.C_EVENT:
                    cmgr.handle_event(next_event)
                executed_event = True
            else:
                break


        # increment sim time
        t += delta_t

        end_time = time.perf_counter()
        if cycles % 50 == 0:
            completion_time_ms = int(end_time*10**3) - int(start_time*10**3)
            perf_label.text = "comp" + str(completion_time_ms) + "\n dynam rate:" + str(dynam_rate) 
            if completion_time_ms != 0:
                dynam_rate = 1000//completion_time_ms

