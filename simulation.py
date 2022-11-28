from time import perf_counter, perf_counter_ns
from config import g, gtime
from carManager import CarManager
from trafficlightManager import TrafficLightManager
from event import Event, EventType
from env import Axes
from vpython import canvas, vector, distant_light, color, label


class Simulation:

    def __init__(self):
        
        # Create the scene, setup the camera, and create lighting
        # Canvas has a resizable option if wanted
        self.scene = canvas(height = 700, width = 1000)
        self.scene.background = vector(0.25,0.25,0.25)
        self.scene.forward = vector(0.534283, -0.620986, -0.573514)
        self.scene.camera.pos = vector(-43.8146, 41.232, 50.8608)
        self.scene.center = vector(-0.62705, -8.96404, 4.50215)
        self.scene.range = 46.668804816827986

        distant_light(direction=vector(0.4,1,0.7), color=color.gray(0.17))
        self.scene.ambient = color.gray(0.2)
        # scene.lights = []

        # Draw the coordinate axes
        if g.generate_axes:
            Axes()

        self.sim_label = label(pos=vector(0,100,0), text="GENERATING CAR OBJECTS")
        self.performance_label = label(pos=vector(-100,2,100), text="WAITING FOR CLOCK")

        # Create car manager (car manager instantiates the environment)
        self.cmgr = CarManager() 

        self.sim_label.text = "GENERATING TRAFFIC LIGHT"

        # Create traffic light manager and generate events
        self.lmgr = TrafficLightManager()
        self.lmgr.generate_events(gtime.total_time)

        # Give car manager awareness of traffic light states
        self.cmgr.set_TL_references(self.lmgr.get_TL_references())
        self.cmgr.generate_events(g.generate_cars_w_random)

        # Create variables for handling events in the simulation loop
        self.next_event = None
        self.executed_event = True

        # Create time variables
        self.t = 0
        self.loop_start_time = 0
        self.loop_end_time = 0
        self.completion_time_ms = 0

        # Run function cycle count
        self.cycles = 0

    def run(self):

        # Get the start time of the function
        self.loop_start_time = perf_counter()

        self.sim_label.text = str(round(self.t,2))

        self.cmgr.run(self.t)
               
        # Fetch all events at this time, t
        while True:
            # If the event has been executed, get next event if there is one.
            if self.executed_event:
                if Event.q.qsize() != 0:
                    self.next_event = Event.q.get(block=False)
                else:
                    break
                self.executed_event = False 
            # If the event's time stamp is now or has passed
            if self.t >= self.next_event.time:
                # Parse the event type and call the event handler
                if self.next_event.event_type == EventType.TL_EVENT:
                    self.lmgr.handle_event(self.next_event)
                elif self.next_event.event_type ==EventType.C_EVENT:
                    self.cmgr.handle_event(self.next_event)
                
                # Set the event to having been executed
                self.executed_event = True
            else:
                break

        # Increment sim time and cycle time.
        self.t += gtime.delta_t
        self.cycles+=1

        # Capture end time and perform loop analysis
        self.loop_end_time = perf_counter()
        if self.cycles % 15 == 0:
            self.completion_time_ms = round((self.loop_end_time - self.loop_start_time)*1000,2)
            self.performance_label.text = str(f"Computation time: {self.completion_time_ms}ms")

        



        





    
