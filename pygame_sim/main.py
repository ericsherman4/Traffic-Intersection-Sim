import pygame
import math
from config import g
from car import Car
from sys import exit


pygame.init()

pygame.display.set_caption('Echolocation')

# Display 0 is my main monitor display
screen = pygame.display.set_mode((g.display_x,g.display_y), 
                pygame.SCALED, vsync = 1, display=g.display_id)
width = screen.get_width()
height = screen.get_height()

# Time stuff
clock = pygame.time.Clock()
time = 0
clock_font = pygame.font.Font('font/Pixeltype.ttf',50)
clock_surface = clock_font.render('Waiting for start', False, 'Yellow')


# Background
bg = pygame.Surface((g.display_x, g.display_y))
bg.fill('gray45')

# Configure keys
# https://www.pygame.org/docs/ref/key.html
pygame.key.set_repeat(100)

# Car
car = Car(g.display_x >> 1, g.display_y >> 1)
move_up = False
move_down = False
move_right = False
move_left = False

# line intersections
# Calculate all of the line equations from the config
line_eq = list()

# list of lists where the sub list is [m,b]
for i in range(0, len(g.wall_coords)):
    rise = g.wall_coords[(i+1) % len(g.wall_coords)][1] - g.wall_coords[i][1]
    run = g.wall_coords[(i+1) % len(g.wall_coords)][0] - g.wall_coords[i][0]
    slope = rise/run
    b = -slope * g.wall_coords[i][0] + g.wall_coords[i][1]
    line_eq.append([slope, b])

# Button to hide border
hide_btn_txt = clock_font.render('Hide', False, 'Yellow')

# Button to incr line
plus_btn = clock_font.render('+', False, 'Yellow')
minus_btn = clock_font.render('-', False, 'Yellow')

# cursor tracker
mouse = (0,0)

while True:

    # check game events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                pygame.quit()
                exit()
            elif event.key == pygame.K_w:
                move_up = True
            elif event.key == pygame.K_s:
                move_down = True
            elif event.key == pygame.K_a:
                move_right = True
            elif event.key == pygame.K_d:
                move_left = True
            elif event.key == pygame.K_SPACE:
                print("reset")
                g.num_lines = 20
                car.reset()
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_w:
                move_up = False
            elif event.key == pygame.K_s:
                move_down = False
            elif event.key == pygame.K_a:
                move_right = False
            elif event.key == pygame.K_d:
                move_left = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if (width-100) <= mouse[0] <= (width-100+80) and 30 <= mouse[1] <= (30+40):
                g.display_wall = not g.display_wall
            elif (width-100) <= mouse[0] <= (width-100+30) and 80 <= mouse[1] <= (80+30):
                g.num_lines += 5
            elif (width-50) <= mouse[0] <= (width-50+30) and 80 <= mouse[1] <= (80+30):
                g.num_lines -= 5
            

    # place background
    screen.blit(bg,(0,0))

    # draw buttons
    pygame.draw.rect(screen,'black', [width-100, 30, 80, 40])
    screen.blit(hide_btn_txt, (width-90, 40))
    pygame.draw.rect(screen, 'black', [width-100, 80, 30, 30])
    screen.blit(plus_btn, (width-93, 82))
    pygame.draw.rect(screen, 'black', [width-50, 80, 30, 30])
    screen.blit(minus_btn, (width-43, 87))

    mouse = pygame.mouse.get_pos()

    # place walls
    if g.display_wall: 
        pygame.draw.lines(screen, 'Yellow', True, g.wall_coords, g.wall_thickness)
    

    car_lines = list()
    car_lines_pos = list()

    # print("----------------")
    angle = 0
    if g.num_lines != 0:
        angle = 360/g.num_lines
    for i in range(0, g.num_lines):
        new_ang = angle*i
        final_pos = pygame.Vector2(g.length, 0)
        final_pos = final_pos.rotate(-car.heading + new_ang) + car.pos   
        # print(f"{new_ang}, {final_pos}, {-car.heading + new_ang}")
        pygame.draw.line(screen, 'Black', car.pos, final_pos, width = 3)

        # find the lines
        denomin = (final_pos.x - car.pos.x)
        if denomin == 0:
            denomin = 0.0001
        slope = (final_pos.y - car.pos.y) / denomin
        b = -slope*car.pos.x + car.pos.y

        car_lines.append([slope,b])
        car_lines_pos.append(final_pos)

    # now look for any line intersections
    i=0
    for line in line_eq:
        
        # line is [m,b], we'll see line is eq 2 and the car line is eq 1
        j=0
        for car_line in car_lines:
            denom = car_line[0] - line[0]
            if denom == 0:
                denom = 0.0001
            int_x = (line[1] - car_line[1])/ denom
            int_y = line[0]* int_x + line[1]
            #check if the intersection is within the x range of the line
            min_val = min(g.wall_coords[i][0],g.wall_coords[(i+1)%len(g.wall_coords)][0])
            max_val = max(g.wall_coords[i][0],g.wall_coords[(i+1)%len(g.wall_coords)][0])
            min_val_2 = min(car.pos.x, car_lines_pos[j].x)
            max_val_2 = max(car.pos.x, car_lines_pos[j].x)
            if int_x <= max_val and int_x >= min_val:
                if int_x >= min_val_2 and int_x <= max_val_2:
                    pygame.draw.circle(screen, 'Red', (int_x,int_y), 10, 0)
            j+=1
        i+=1

    # Update the time
    time = pygame.time.get_ticks()/1000
    clock_surface = clock_font.render(str(time), False, 'Yellow')
    screen.blit(clock_surface,(g.display_x-100, g.display_y-50))

    # update car
    car.update(time, [move_up, move_down, move_right, move_left])

    # place car
    car.display(screen)

    # update everything
    pygame.display.update()

    # rate limiter
    clock.tick(60) # equiv to rate in vpython, loop should not run faster than 60 times per sec



