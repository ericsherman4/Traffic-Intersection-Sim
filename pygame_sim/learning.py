import pygame
from sys import exit

pygame.init()

screen = pygame.display.set_mode((800,400), pygame.SCALED, vsync = 1)


pygame.display.set_caption('Traffic Light Sim')
# you could also change the icon

# print info about the the game instance (drivers / hw)
obj = pygame.display.Info()
print(obj)

clock = pygame.time.Clock()

test_surface = pygame.Surface((100,200))
# list of colors https://github.com/pygame/pygame/blob/main/src_py/colordict.py
test_surface.fill('Red')

test_font = pygame.font.Font('font/Pixeltype.ttf', 50)
text_surface = test_font.render('test text', False, 'Yellow')

car = pygame.image.load('graphics/orange_car_2.png')

# time = 0
# delta_t = 1/60
prev_time = 0

while True:
    # check for player input
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

    # erase the previous time
    text_surface = test_font.render(str(round(prev_time,2)), False, 'Black')
    screen.blit(text_surface, (400,200))

    # update the time
    prev_time = pygame.time.get_ticks()/1000
    text_surface = test_font.render(str(round(prev_time,2)), False, 'Yellow')
        
    #blit = block image transfer
    screen.blit(test_surface,(0,0))
    screen.blit(car,(200,200))
    screen.blit(text_surface, (400,200))






    # update everything
    pygame.display.update()

    # rate limiter
    clock.tick(60) # equiv to rate in vpython, loop should not run faster than 60 times per sec