from queue import PriorityQueue

# Used for generating car insertion or other action events if needed
# Also used for coordinating actions on the traffic light

class EventType:
    TL_EVENT, C_EVENT = range(2)

class C_Event:
    pass

class TL_Event:
    NO_POWER, RED, GREEN, YELLOW, HALTED = range(5)
    
# Consider separating into two different classes for each event type and then 
# delete the event type class

class Event:
    q = PriorityQueue() # sim event queue
    
    def __init__(self, curr_time, event_type, action, idx, lane : -1):
        # Event details
        self.time = curr_time #also priority, the lower the num, the higher the priority
        self.event_type = event_type
        self.action = action

        # Event Target object
        self.idx = idx # used by both car events and traffic light events
        self.lane = lane # used by just car events
        
        # Store on Global Queue
        Event.q.put(self)
    
    # Overloaded operators so that the priority queue can sort the events
    def __lt__(self, other):
        return self.time < other.time
    
    def __gt__(self,other):
        return self.time > other.time
    
    def __le__(self,other):
        return self.time <= other.time
    
    def __ge__(self,other):
        return self.time >= other.time  

