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
    generate_axes = True

    #traffic light
    tl_height = 10
    tl_width = 4
    tl_length = tl_width
    light_radius = (tl_width - tl_width/6)/2
    show_tl_labels = False

    # traffic light timing (ms)
    time_green = 15
    print("TIME GREEN WAS CHANGED!!!!")
    time_yellow = 8
    time_red_overlap = 3

    # car
    car_width = 8
    car_length = 18
    car_length_div2 = car_length/2
    car_height = 8
    car_colors = [color.gray(0.2), color.gray(0.4), color.gray(0.6), color.blue, color.red, 
                  vector(101,67,33), color.green, color.orange, vector(207,185,151), vector(225,198,153), 
                  color.purple, vector(255,215,0), color.yellow, color.cyan, color.magenta, vector(1,0.7,0.2)]

    # car Personality
    car_max_speed = 8
    car_min_speed = 4
    car_starting_vel_max = car_max_speed
    car_max_decel = 5
    car_max_accel = 5
    car_dis_thres_yellow = 20
    car_vel_thres_yellow = 6

    # Car manager
    max_cars = 3
    max_cars_on_road = 2
    generate_cars_w_random = False

class gtime:
    delta_t = 0.1
    total_time = 400
    sim_rate = 40

