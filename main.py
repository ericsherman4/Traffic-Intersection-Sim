from config import gtime
from vpython import rate
from simulation import Simulation


def sim_main():

    sim = Simulation()

    print_notes()

    while sim.t < gtime.total_time:
        rate(gtime.sim_rate)
        sim.run()


def print_notes():
    print("add dynamic v_set setting? ")
    print("i wonder if setting distance to nearest car to be zero will always fix it?")
    print("do the increment function you did in the traffic light manager. also why does it break if u increase time green?")