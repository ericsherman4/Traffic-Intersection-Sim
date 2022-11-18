from config import g
from vpython import *
from env import Env, Axes
from trafficlight import TrafficLight
from cars import Car
from carManager import CarManager


def sim_main():
    scene = canvas(width = 800, height = 500)
    scene.background = vector(0.25,0.25,0.25)
    # scene.autoscale = False
    scene.forward = vector(0.534283, -0.620986, -0.573514)
    scene.camera.pos = vector(-43.8146, 41.232, 50.8608)
    scene.center = vector(-0.62705, -8.96404, 4.50215)
    scene.range = 46.668804816827986

    Axes()
    Env()
    light1 = TrafficLight(vector(0,20,0), 360-135)

    L = label(pos=vector(0,2,0), text="waiting to start")

    # timing will be in ms to avoid annoying floating point errors 
    t = 0
    delta_t = 500

    while(t < 0):
        # limit the rate of the while loop
        rate(8) # input is frequency, loop time is 1/f

        L.text = str(t)

        # run the traffic light state machine
        light1.run(t)

        if t < 5000:
            light1.disable()
        elif t == 5000:
            light1.enable()

        if t == 27500:
            light1.disable()

        if t == 50000:
            light1.enable()


        # increment sim time
        t += delta_t

    # count = 50
    # for i in range(0,10):
    #     Car(count,g.roadwidth/4 + g.roadwidth/8)
    #     count+=50

    Car(vector(-200, 0, g.roadwidth/4 +g.roadwidth/8), True)

    CarManager()







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




    


        

