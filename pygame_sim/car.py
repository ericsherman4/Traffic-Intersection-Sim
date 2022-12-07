import pygame
import math
from config import g


class dir:
    UP, DOWN, RIGHT, LEFT = range(4)

class Car:
    def __init__(self, x_pos, y_pos):
        self.image_path = 'graphics/orange_car_2.png'
        self.surface = pygame.image.load(self.image_path)#.convert_alpha()
        # self.surface = pygame.transform.rotate(self.surface, 90)
        # self.surface = pygame.transform.rotate(self.surface, 90)
        self.pos = pygame.Vector2((x_pos, y_pos))
        self.vel = pygame.Vector2()
        self.heading = 0
        self.time = 0

    def reset(self):
        self.vel.x = 0
        self.vel.y = 0
        self.pos.x = g.display_x >> 1 
        self.pos.y = g.display_y >> 1
        self.heading = 0

    def update(self, time, flags : list):
        # struct of flags (up,down, right , left)
        if flags[dir.RIGHT] and flags[dir.LEFT]:
            pass
        elif flags[dir.RIGHT]:
            # count clockwise
            self.heading +=g.heading_incr
        elif flags[dir.LEFT]:
            # clockwise
            self.heading -= g.heading_incr

        x_incr = math.cos(self.heading/180*math.pi)*g.car_acc
        y_incr = math.sin(self.heading/180*math.pi)*g.car_acc

        # print(f"{self.heading}, {x_incr}, {y_incr}")

        if flags[dir.UP]:
            self.vel.x += x_incr
            self.vel.y -= y_incr #y is inverted in the game coordinates sys

        if flags[dir.DOWN]:
            self.vel.x -= x_incr
            self.vel.y += y_incr

        if not flags[dir.UP] and not flags[dir.DOWN]:
            friction = (g.car_acc + 3)
            if self.vel.x > 0:
                self.vel.x -= friction
            elif self.vel.x < 0:
                self.vel.x += friction
            if self.vel.y > 0:
                self.vel.y -= friction
            elif self.vel.y < 0:
                self.vel.y += friction

        self.move_vel(time)

        self.time = time

    def move_vel(self,time):
        self.pos = self.pos + self.vel * (time - self.time)
        




    def display(self, screen : pygame.display):
        final_car = pygame.transform.rotate(self.surface, self.heading)
        rect = final_car.get_rect(center=(self.pos.x, self.pos.y))
        screen.blit(final_car, rect)



        






    # self.posx = self.posx + self.velx * (time -  self.time)
    # self.posy = self.posy + self.vely * (time - self.time)
    # self.time = time

