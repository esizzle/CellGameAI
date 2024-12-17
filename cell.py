import pygame
import pymunk
import math
from particle import Particle
import random

from physics_particle import PhysicsParticle


class Cell(PhysicsParticle):
    def __init__(self, position: tuple, r: int = 255, g: int = 255, b: int = 255, mass: int = 20, size: int = 10, charge: int = 0, density: float = 1, is_player: bool = False):
        super().__init__(mass,charge,density,position)
        self.r = r
        self.g = g
        self.b = b
        self.size = size
        self.CELL_START_MASS = mass
        self.age = 0
        self.max_age = 5
        self.speed = 1
        self.is_player = is_player
        if self.is_player:
            self.max_age = 100

        # pymunk
        moment = pymunk.moment_for_circle(self.mass, 0, self.size)
        self.create_body(moment)
        self.create_circle(self.size)

    # draw cell onto screen
    def draw_cell(self,screen):
        pygame.draw.circle(screen, (self.r, self.g, self.b), (self.body.position[0], self.body.position[1]), 10,1)

    def draw_split_cell(self, screen):
        animate_split = 0
        for i in range(self.size+1):
            pygame.draw.circle(screen, (self.r, self.g, self.b), (self.body.position[0]-animate_split+10, self.body.position[1]), 10, 1)
            pygame.draw.circle(screen, (self.r, self.g, self.b), (self.body.position[0]+animate_split-10, self.body.position[1]), 10, 1)
            animate_split += 1

    # change cell mass
    def calculate_mass(self, mass):
        self.mass += mass
        if self.mass %2:
            self.size += 1

    # change cell colour
    def calculate_colour(self,mass, r,g,b):
        # get average of colours with respect to masses
        self.r = ((self.r * self.mass) + (r * mass))//(self.mass + mass)
        self.g = ((self.g * self.mass) + (g * mass))//(self.mass + mass)
        self.b = ((self.b * self.mass) + (b * mass))//(self.mass + mass)

        # maintain brightness
        rgb = [self.r,self.g,self.b]
        brightest = max(rgb)
        self.r = (self.r * 255)// brightest
        self.g = (self.g * 255)// brightest
        self.b = (self.b * 255)// brightest


        # if r,g,b become negative bind them to zero
        if self.r < 0:
            self.r = 0

        if self.g < 0:
            self.g = 0

        if self.b < 0:
            self.b = 0

    def consume(self, mass, r,g,b):
        self.calculate_mass(mass)
        self.calculate_colour(mass, r,g,b)

    def split(self,cells,space):
        if self.mass >= 2 * self.CELL_START_MASS:
            self.mass = self.CELL_START_MASS
            self.size = 10
            theta = random.randint(0,self.mass) * 2 * math.pi / self.mass
            cell_x = self.body.position[0] + self.size+10
            cell_y = self.body.position[1]
            new_cell = Cell((cell_x,cell_y),self.r,self.g,self.b,self.mass,self.size)
            cells.append(new_cell)
            new_cell.add_to_space(space)
            new_cell.set_collision_type(len(cells))




    def death(self,particles):
        if self.age >= self.max_age:
            for i in range(self.mass):
                # create a new cell
                theta = i*2*math.pi/self.mass
                particle_x = self.body.position[0] + math.cos(theta)*self.size*4/3
                particle_y = self.body.position[1] + math.sin(theta)*self.size*4/3
                # get new color value
                color = random.randint(1, 3)
                if color == 1:
                    particle = Particle((particle_x, particle_y), 255, 0, 0)
                    self.calculate_colour(1, 0, 255, 255)
                elif color == 2:
                    particle = Particle((particle_x, particle_y), 0, 255, 0)
                    self.calculate_colour(1, 255, 0, 255)
                else:
                    particle = Particle((particle_x, particle_y), 0, 0, 255)
                    self.calculate_colour(1, 255, 255, 0)
                particles.append(particle)



