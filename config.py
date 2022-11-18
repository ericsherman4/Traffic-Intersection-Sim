from vpython import color, vector

class g:
    #env
    size = 600
    roadwidth = 40
    yellow_line_width = 1
    yellow_line_spacing_c2c = 2 #c2c = center to center
    white_line_width = 1.5
    dashed_line_length= 7
    animate_loading = False

    #traffic light
    tl_height = 10
    tl_width = 4
    tl_length = tl_width
    light_radius = (tl_width - tl_width/6)/2

    # traffic light timing (ms)
    time_green = 10000
    time_red = time_green
    time_yellow = 4000
    time_red_overlap = 3000 

    # car
    car_width = 8
    car_length = 18
    car_height = 8
    car_colors= [color.red, color.yellow, color.green, 
                color.orange, color.white, color.blue, 
                color.cyan, color.purple, color.magenta,
                vector(1,0.7,0.2)]

    # car manager
    max_cars = 15
    max_cars_on_road = 8
