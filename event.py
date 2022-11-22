
# Used for generating car insertion events if wanted. 
class event:
    pass


# reference code below from the circuit simulator.

####################################
###      event class
#################################### 
# class event:
#     q = queue.PriorityQueue()
    
#     def __init__(self, time, netID, netState):
#         self.netID = netID
#         self.netState = netState
#         self.time = time #also priority, the lower the num, the higher the priority
#         event.q.put(self)
    
#     def __lt__(self, other):
#         return self.time < other.time
    
#     def __gt__(self,other):
#         return self.time > other.time
    
#     def __le__(self,other):
#         return self.time <= other.time
    
#     def __ge__(self,other):
#         return self.time >= other.time  