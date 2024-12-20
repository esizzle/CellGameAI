import random
from interactions import distance
from cell import Cell
from particle import Particle

# input cell and parameters, and output movement
class CellAI:
    def __init__(self,r: int,g: int,b: int):
        self.r = r
        self.g = g
        self.b = b

    # take cell colour and uses it to return preference
    def calculate_preference(self):
        preference = ''
        if self.r == 255:
            preference = self.r

        elif self.g == 255:
            preference = self.g

        else:
            preference = self.b

        return preference

    def decide(self,cell: Cell,objects: list):
        # based on food preference decide which particle to go to
        # particle colour will only have 255 in one of the values with the other init to 0
        # cell will only have one color value be 255, hence we find which ones are equal
        target_particle = None
        distance_particle = {}
        distances = []
        particles = []
        other_cells = []
        for item in objects:
            if type(item) == Particle:
                particles.append(item)
            elif type(item) == Cell:
                other_cells.append(item)

        for particle in particles:
            if particle.r == self.r:
                dist = distance(cell, particle) * 0.5

            elif particle.g == self.g:
                dist = distance(cell, particle) * 0.5

            elif particle.b == self.b:
                dist = distance(cell, particle) * 0.5

            else:
                dist = distance(cell, particle)

            distance_particle[dist] = particle
            distances.append(dist)

            # Rule 2: Avoid larger cells (threats)
        safe_direction = [0, 0]
        for other in other_cells:
            if other != cell and other.genome.size > cell.genome.size * 1.2:  # Only consider larger cells
                d = distance(cell, other)
                if d < cell.genome.size * 3:  # If too close, move away
                    safe_direction[0] -= (other.position[0] - cell.position[0]) / d
                    safe_direction[1] -= (other.position[1] - cell.position[1]) / d

        if distances:
            min_dist = min(distances)
            target_particle = distance_particle[min_dist]

        # move towards particle
        move_x, move_y = 0,0
        if target_particle:
            move_x += cell.genome.aggression * (target_particle.position[0] - cell.position[0])
            move_y += cell.genome.aggression * (target_particle.position[1] - cell.position[1])

        else:
            move_x, move_y = cell.body.velocity

            # Move away from threats (scaled by caution)
        move_x += cell.genome.caution * safe_direction[0]
        move_y += cell.genome.caution * safe_direction[1]

        # Normalize movement
        magnitude = (move_x**2 + move_y**2) ** 0.5
        if magnitude > 0:
            move_x /= magnitude
            move_y /= magnitude

        # scale speed
        move_x *= cell.genome.speed
        move_y *= cell.genome.speed

        return move_x, move_y
