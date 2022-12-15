from vpython import box,vector,compound,color,arrow,sleep,label
from config import g
from math import pi
from gui_control import monitor_terminate

class Env:
    def __init__(self):
        road_color = vector(0.2,0.2,0.2)
        box(pos=vector(0,-10,0), height = 20, width = g.size, length = g.size/4, color = color.green)
        box(pos=vector(0,-10,0), height = 20, width = g.size/4, length = g.size, color = color.green)
        box(pos=vector(0,0.3,0), height = 0.2, width = g.roadwidth, length = g.size, color = road_color)
        box(pos=vector(0,0.3,0), height = 0.2, width = g.size, length= g.roadwidth, color = road_color)

        # create road items
        adj = 4 # this for making the lanes stop before the intersection
        yellow_lane_center = (g.size-g.roadwidth)/4 + g.roadwidth/2 + adj
        lane_length = (g.size-g.roadwidth)/2 - adj*2
        stop_line_center = g.roadwidth/2
        stop_line_length = g.roadwidth
        stop_line_position = stop_line_center+g.white_line_width/2+adj*2
        white_lane_start = (g.roadwidth/2 + adj*2) + g.dashed_line_length/2
        white_lane_end = g.size/2

        # generate the lines by instantiating them and then rotating around center y axis
        for i in range(0,4):
            if g.animate_loading:
                sleep(0.2)
            line1 = box(pos = vector(yellow_lane_center,0,g.yellow_line_spacing_c2c >> 1), height = 1, width = g.yellow_line_width, length = lane_length, color=color.yellow, emissive= True)
            line2 = box(pos = vector(yellow_lane_center,0,-g.yellow_line_spacing_c2c >> 1), height = 1, width = g.yellow_line_width, length = lane_length, color=color.yellow, emissive = True)
            line1.rotate(angle=pi/2*i, axis = vector(0,1,0), origin=vector(0,0,0))
            line2.rotate(angle=pi/2*i, axis = vector(0,1,0), origin=vector(0,0,0))
            stop_line = box(pos=vector(stop_line_position,0,0), height= 1.2, width = stop_line_length, length= g.white_line_width, emissive= True)
            stop_line.rotate(angle=pi/2*i, axis = vector(0,1,0), origin=vector(0,0,0))
        
        if g.animate_loading:
            sleep(0.5)
        count = white_lane_start
        pos_of_dashed_line = g.roadwidth/4
        while(count < white_lane_end):
            for i in range(0,4):
                monitor_terminate()
                line1 = box(pos=vector(count, 0, pos_of_dashed_line), height = 1.2, width = 1, length = g.dashed_line_length, color= color.white, emissive = True)
                line2 = box(pos=vector(count, 0, -pos_of_dashed_line), height = 1.2, width = 1, length = g.dashed_line_length, color= color.white, emissive = True)
                line1.rotate(angle=pi/2*i, axis = vector(0,1,0), origin=vector(0,0,0))
                line2.rotate(angle=pi/2*i, axis = vector(0,1,0), origin=vector(0,0,0))
            if g.animate_loading:
                sleep(0.1)
            count+= g.dashed_line_length*2

        lane_identifer = -1
        labelpos_x = white_lane_end - white_lane_end/3
        pos_z = [pos_of_dashed_line + pos_of_dashed_line/2, pos_of_dashed_line - pos_of_dashed_line/2, 
                    -pos_of_dashed_line + pos_of_dashed_line/2, -pos_of_dashed_line - pos_of_dashed_line/2]
        
        if g.generate_lane_identifiers: 
            for i in range(0,4):
                angle=pi/2*i
                for j in range(0,4):
                    # structure to pick different identifiers to account for mirroring when rotating.
                    if i < 2: 
                        lane_identifer+=1
                    elif i == 2: 
                        lane_identifer = 3 - j
                    elif i==3:
                        lane_identifer = 7-j
                    label1 = label(pos=vector(labelpos_x, 0, pos_z[j] ), text=str(lane_identifer))
                    label1.rotate(angle=angle, axis = vector(0,1,0), origin=vector(0,0,0))
                
        # variables that car manager will need
        offset_from_center = g.size/2 - 20
        self.lane_pos_start =  [vector(-offset_from_center,0,pos_z[0]),
                                vector(-offset_from_center,0,pos_z[1]),
                                vector(offset_from_center,0,pos_z[2]),
                                vector(offset_from_center,0,pos_z[3]),
                                vector(pos_z[0],0,offset_from_center),
                                vector(pos_z[1],0,offset_from_center),
                                vector(pos_z[2],0,-offset_from_center),
                                vector(pos_z[3],0,-offset_from_center)]

        self.lane_pos_end = [vector(offset_from_center,0,pos_z[0]),
                             vector(offset_from_center,0,pos_z[1]),
                             vector(-offset_from_center,0,pos_z[2]),
                             vector(-offset_from_center,0,pos_z[3]),
                             vector(pos_z[0],0,-offset_from_center),
                             vector(pos_z[1],0,-offset_from_center),
                             vector(pos_z[2],0,offset_from_center),
                             vector(pos_z[3],0,offset_from_center)]

        self.stop_line_position =  [-stop_line_position,
                                    -stop_line_position,
                                    stop_line_position,
                                    stop_line_position,
                                    stop_line_position,
                                    stop_line_position,
                                    -stop_line_position,
                                    -stop_line_position]

class Axes:
    def __init__(self):
        length = g.size/2+50
        width= 2
        hwidth = 2
        self.yaxis = arrow(pos=vector(0,-length,0), axis=vector(0, length*2,0), shaftwidth=width, color=color.green, headwidth = hwidth) 
        self.xaxis = arrow(pos=vector(-length,0,0), axis=vector(length*2,0,0), shaftwidth=width, color=color.red, headwidth = hwidth)
        self.zaxis = arrow(pos=vector(0,0,-length), axis=vector(0,0,length*2), shaftwidth=width, color=color.blue, headwidth = hwidth)