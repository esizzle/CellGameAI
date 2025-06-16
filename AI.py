import random
from interactions import distance_squared
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

    def decide(self, cell: Cell, objects: list):
        target_particle = None
        distance_particle = {}
        distances = []
        particles = []
        other_cells = []

        for item in objects:
            if isinstance(item, Particle):
                particles.append(item)
            elif isinstance(item, Cell):
                other_cells.append(item)

        # Evaluate particles
        for particle in particles:
            # Prefer particles of matching color (based on RGB channel matching)
            if particle.color == cell.color:
                dist = distance_squared(cell, particle)* 0.5
            elif not cell.genome.p_consumption[particle.color]:
                # ignore this particle
                continue
            else:
                dist = distance_squared(cell, particle)

            distance_particle[dist] = particle
            distances.append(dist)

        # Social force based on behavior toward other cells
        social_force_x, social_force_y = 0, 0
        for other in other_cells:
            if other == cell:
                continue

            dx = other.position[0] - cell.position[0]
            dy = other.position[1] - cell.position[1]
            dist_sq = dx ** 2 + dy ** 2

            if dist_sq == 0 or dist_sq > (cell.genome.size * 10) ** 2:
                continue  # Ignore far away cells

            dist = dist_sq ** 0.5
            direction_x = dx / dist
            direction_y = dy / dist

            # Get behavior force (positive = attraction, negative = repulsion)
            behavior_force = cell.genome.behavior.get(other.color, 0)

            # Weight by inverse distance for smoother force curve
            force_strength = behavior_force / dist_sq

            social_force_x += direction_x * force_strength
            social_force_y += direction_y * force_strength

        # Find closest matching particle
        if distances:
            min_dist = min(distances)
            target_particle = distance_particle[min_dist]

        # Initialize movement vector
        move_x, move_y = 0, 0

        # Move toward target particle
        if target_particle:
            move_x += (target_particle.position[0] - cell.position[0])
            move_y += (target_particle.position[1] - cell.position[1])
        else:
            move_x, move_y = cell.body.velocity

        # Add social interaction forces (scaled by caution)
        move_x += social_force_x
        move_y += social_force_y

        # Normalize
        magnitude = (move_x ** 2 + move_y ** 2) ** 0.5
        if magnitude > 0:
            move_x /= magnitude
            move_y /= magnitude

        # Scale by speed
        move_x *= cell.genome.speed
        move_y *= cell.genome.speed

        return move_x, move_y

