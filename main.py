from config import g
from vpython import *
from env import Env, Axes
from trafficlight import TrafficLight
from car import Car
from carManager import CarManager
import time


def sim_main():
    scene = canvas(width = 800, height = 500)
    scene.background = vector(0.25,0.25,0.25)
    # scene.autoscale = False
    scene.forward = vector(0.534283, -0.620986, -0.573514)
    scene.camera.pos = vector(-43.8146, 41.232, 50.8608)
    scene.center = vector(-0.62705, -8.96404, 4.50215)
    scene.range = 46.668804816827986

    Axes()
    # Env()
    light1 = TrafficLight(vector(0,20,0), 360-135)

    L = label(pos=vector(0,2,0), text="waiting to start")
    perf_label = label(pos=vector(-100,2,100), text="waiting for clock")

    mgr = CarManager() # car manager instantiates the env
    for i in range(0,8):
        mgr.add_car(i)

    t = 0
    delta_t = 0.1

    start_time = 0
    end_time = 0

    cycles = 0
    dynam_rate = 50
    completion_time_ms = 1

    while(t < 60):

        start_time = time.perf_counter()
        cycles+=1

        # limit the rate of the while loop
        # rate(dynam_rate) # input is frequency, loop time is 1/f
        rate(40)

        # L.text = str(t)

        # run the traffic light state machine
        light1.run(t)

        if t < 5:
            light1.disable()
        elif int(t) == 5:
            light1.enable()

        mgr.run(t)


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




    


        

