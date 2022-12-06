import pygame
from config import g
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

     

    # place background
    screen.blit(bg,(0,0))

    # Update the time
    time = pygame.time.get_ticks()/1000
    clock_surface = clock_font.render(str(time), False, 'Yellow')
    screen.blit(clock_surface,(g.display_x-100, g.display_y-50))





    


    # update everything
    pygame.display.update()

    # rate limiter
    clock.tick(60) # equiv to rate in vpython, loop should not run faster than 60 times per sec

