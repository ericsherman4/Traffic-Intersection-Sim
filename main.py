from config import g
from vpython import *
from env import env
from trafficlight import trafficlight

# def sim_main():

# probably best to keep all as globals for now so that 
# you can access variables in jupyter for easy debugging
scene = canvas(width = 800, height = 500)
scene.background = vector(0.25,0.25,0.25)
scene.autoscale = False
scene.forward = vector(0.534283, -0.620986, -0.573514)
scene.camera.pos = vector(-43.8146, 41.232, 50.8608)
scene.center = vector(-0.62705, -8.96404, 4.50215)
scene.range = 46.668804816827986


sim = env()
light1 = trafficlight(vector(0,10,0), 0)
# sleep(2)
light1.test()