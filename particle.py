import pygame

class Particle:
    def __init__(self, position: tuple, r: int, g: int, b: int, mass: int = 1, size: int = 1):
        self.position = position
        self.r = r
        self.g = g
        self.b = b

        self.mass = mass
        self.size = size

    def draw_particle(self, surface, offset=(0, 0)):
        x, y = self.position[0] + offset[0], self.position[1] + offset[1]
        pygame.draw.circle(surface, (self.r, self.g, self.b), (int(x), int(y)), self.size)


