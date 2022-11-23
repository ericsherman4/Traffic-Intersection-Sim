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
    generate_lane_identifiers = True

    #traffic light
    tl_height = 10
    tl_width = 4
    tl_length = tl_width
    light_radius = (tl_width - tl_width/6)/2

    # traffic light timing (ms)
    time_green = 20
    #time_red = time_green # this is no longer used by the new implementation
    time_yellow = 8
    time_red_overlap = 5 

    # car
    car_width = 8
    car_length = 18
    car_height = 8
    car_colors= [color.red, color.yellow, color.green, 
                color.orange, color.white, color.blue, 
                color.cyan, color.purple, color.magenta,
                vector(1,0.7,0.2)]

    # car personality
    # for now, we will do all cars have constant velocity but think later 
    # on should add jerk and also each car should have a different acceleration profiles
    car_accel = 1
    car_max_speed = 6
    car_starting_vel = 2
    car_max_decel = 5

    # car manager
    max_cars = 3
    max_cars_on_road = 3

