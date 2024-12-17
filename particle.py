import pygame

class Particle:
    def __init__(self, position: tuple, r: int, g: int, b: int, mass: int = 1, size: int = 1):
        self.position = position
        self.r = r
        self.g = g
        self.b = b

        self.mass = mass
        self.size = size

    def draw_particle(self, screen):
        pygame.draw.circle(screen, (self.r, self.g, self.b), self.position, self.size)


