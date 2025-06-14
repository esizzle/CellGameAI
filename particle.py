import pygame

class Particle:
    def __init__(self, position: tuple, r: int, g: int, b: int, mass: int = 1, size: int = 1):
        self.position = position
        self.r = r
        self.g = g
        self.b = b
        self.color = self.get_dominant_color()

        self.mass = mass
        self.size = size

    def draw(self, perceived_color, surface, zoom_factor = 1.0, offset=(0, 0)):
        if self.size * zoom_factor < 1:
            pass
        else:
            x, y = self.position[0]*zoom_factor + offset[0], self.position[1]*zoom_factor + offset[1]
            pygame.draw.circle(surface, perceived_color, (int(x), int(y)), self.size*zoom_factor, width= 1)


    def get_dominant_color(self):
        max_val = max(self.r, self.g, self.b)

        if self.r == max_val:
            return 'r'
        elif self.g == max_val:
            return 'g'
        else:
            return 'b'