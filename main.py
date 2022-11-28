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
    print("OPTIMIZE CAR MANAGER, SO MANY THINGS ARE USING THE SAME FOR LOOP BUT ITS ALL SEPARATE FUNCTIONS")
    print("ALSO OPTIMIZE BY JUST HAVING A BEHIND LIGHT FLAG, THAT WAY YOU DONT HAVE TO CHECK EVERYTIME")
    print("add dynamic v_set setting? ")
    print("i wonder if setting distance to nearest car to be zero will always fix it?")
    print("do the increment function you did in the traffic light manager. also why does it break if u increase time green?")