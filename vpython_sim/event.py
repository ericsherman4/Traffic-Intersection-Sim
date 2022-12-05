from queue import PriorityQueue

# Used for generating car insertion or other action events if needed
# Also used for coordinating actions on the traffic light

class EventType:
    TL_EVENT, C_EVENT = range(2)

class C_Event:
    ADD_CAR, TURN_RIGHT, TURN_LEFT = range(3)

class TL_Event:
    RED, GREEN, YELLOW, HALTED = range(4)
    
# Consider separating into two different classes for each event type and then 
# delete the event type class

class Event:
    q = PriorityQueue() # sim event queue
    total_events = 0

    def __init__(self, curr_time, event_type, action, idx = -1, lane = -1):
        # Event details
        self.time = curr_time #also priority, the lower the num, the higher the priority
        self.event_type = event_type
        self.action = action

        # Event Target object
        self.idx = idx # used by both car events and traffic light events
        self.lane = lane # used by just car events
        
        # Store on Global Queue
        Event.q.put(self)
        Event.total_events+=1
    
    # Overloaded operators so that the priority queue can sort the events
    def __lt__(self, other):
        return self.time < other.time
    
    def __gt__(self,other):
        return self.time > other.time
    
    def __le__(self,other):
        return self.time <= other.time
    
    def __ge__(self,other):
        return self.time >= other.time  

    # overloaded print function
    def __str__(self):
        print("overriden print function not implemented")

