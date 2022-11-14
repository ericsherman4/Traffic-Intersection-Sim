from vpython import box,vector,compound,color
from config import g

class env:
    def __init__(self):
        road_color = vector(0.2,0.2,0.2)
        field = box(pos=vector(0,0,0), height = 0.2, width = g.size, length = g.size, color = color.green)
        road1 = box(pos=vector(0,0.3,0), height = 0.2, width = g.roadwidth, length = g.size, color = road_color)
        road2 = box(pos=vector(0,0.3,0), height = 0.2, width = g.size, length= g.roadwidth, color = road_color)
        self.scene = compound([field, road1, road2])