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

print(line_eq)
print("verified the first and the last equation")




while True:
    # check for player input
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

    # place background
    screen.blit(bg,(0,0))

    # place walls
    pygame.draw.lines(screen, 'Yellow', True, g.wall_coords, g.wall_thickness)

    
    
    final_pos = pygame.Vector2(2000,0)
    #vectors rotate in the opposite direction of other rotate calls so invert heading
    final_pos = final_pos.rotate(-car.heading) + car.pos

    # print(f"{car.heading}, {car.pos}, {final_pos}")
    pygame.draw.line(screen, 'White', car.pos, final_pos, width= 3)


    # find line intersections
    # whats the equation of the line coming from the car? 
    denomin = (final_pos.x - car.pos.x)
    if denomin == 0:
        denomin = 0.0001
    slope = (final_pos.y - car.pos.y) / denomin
    b = -slope*car.pos.x + car.pos.y

    # now look for any line intersections
    i=0
    for line in line_eq:
        # line is [m,b], we'll see line is eq 2 and the car line is eq 1
        denom = slope - line[0]
        if denom == 0:
            denom = 0.0001
        int_x = (line[1] - b)/ denom
        int_y = line[0]* int_x + line[1]
        #check if the intersection is within the x range of the line
        min_val = min(g.wall_coords[i][0],g.wall_coords[(i+1)%len(g.wall_coords)][0])
        max_val = max(g.wall_coords[i][0],g.wall_coords[(i+1)%len(g.wall_coords)][0])
        min_val_2 = min(car.pos.x, final_pos.x)
        max_val_2 = max(car.pos.x, final_pos.x)
        if int_x <= max_val and int_x >= min_val:
            if int_x >= min_val_2 and int_x <= max_val_2:
                pygame.draw.circle(screen, 'Red', (int_x,int_y), 10, 0)
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



