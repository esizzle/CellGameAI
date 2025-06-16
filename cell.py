import pygame
import pymunk
import math
from particle import Particle
import random
import copy

from physics_particle import PhysicsParticle


class Cell(PhysicsParticle):
    def __init__(self, position: tuple, chromosome: list, active_gene: int = 0, is_player: bool = False, has_split: bool = False):
        self.chromosome = chromosome
        self.genome = chromosome[active_gene]
        self.size = self.genome.size
        density = self.size/self.genome.start_mass
        super().__init__(self.genome.start_mass,self.genome.charge,density,position)
        self.age = 0
        self.is_player = is_player
        self.has_split = has_split
        self.dead = False

        self.color = self.get_dominant_color()


        if self.is_player:
            self.max_age = 100000
            self.speed = 300
            pass

        # pymunk
        moment = pymunk.moment_for_circle(self.mass, 0, self.size)
        self.create_body(moment)
        self.create_circle(self.size)

    # draw cell onto screen
    def draw(self, perceived_color, surface, zoom_factor = 1.0, offset=(0, 0)):
        x, y = self.body.position[0]*zoom_factor + offset[0], self.body.position[1]*zoom_factor + offset[1]
        pygame.draw.circle(surface, perceived_color, (int(x), int(y)), self.size*zoom_factor, self.genome.thickness)

    def draw_split_cell(self, screen):
        animate_split = 0
        for i in range(self.genome.size+1):
            pygame.draw.circle(screen, (self.genome.r, self.genome.g, self.genome.b), (self.body.position[0]-animate_split+10, self.body.position[1]), self.genome.size, self.genome.thickness)
            pygame.draw.circle(screen, (self.genome.r, self.genome.g, self.genome.b), (self.body.position[0]+animate_split-10, self.body.position[1]), self.genome.size, self.genome.thickness)
            animate_split += 1

    # change cell mass
    def calculate_mass(self, mass):
        self.mass += mass


    # change cell colour
    def calculate_colour(self,mass, r,g,b):
        # get average of colours with respect to masses
        self.genome.r = ((self.genome.r * self.mass) + (r * mass))//(self.mass + mass)
        self.genome.g = ((self.genome.g * self.mass) + (g * mass))//(self.mass + mass)
        self.genome.b = ((self.genome.b * self.mass) + (b * mass))//(self.mass + mass)

        # maintain brightness
        rgb = [self.genome.r,self.genome.g,self.genome.b]
        brightest = max(rgb)
        self.genome.r = (self.genome.r * 255)// brightest
        self.genome.g = (self.genome.g * 255)// brightest
        self.genome.b = (self.genome.b * 255)// brightest


        # if r,g,b become negative bind them to zero
        if self.genome.r < 0:
            self.genome.r = 0

        if self.genome.g < 0:
            self.genome.g = 0

        if self.genome.b < 0:
            self.genome.b = 0

    def get_dominant_color(self):
        max_val = max(self.genome.r, self.genome.g, self.genome.b)

        if self.genome.r == max_val:
            return 'r'
        elif self.genome.g == max_val:
            return 'g'
        else:
            return 'b'

    def consume_particle(self,obj, consumed_particles):
        if self.genome.p_consumption[obj.color]:
            self.calculate_mass(obj.mass)
            self.calculate_colour(obj.mass, obj.r, obj.g, obj.b)
            consumed_particles.append(obj)

    def consume_cell(self, other, to_remove_cells):
        if (self.size > (other.size * 1.3)) and (other.genome.thickness == 1) and self.genome.c_consumption[other.color] and (other.age > 3):
            # self.chromosome.append(other.genome)
            other.dead = True
            other.age = other.genome.max_age + 1
            to_remove_cells.add(other)
            print(self.color, "cell consumed", other.color, "cell!")

        '''elif  (self.mass > (2 * other.mass)) and (other.genome.thickness == 2):
            other.death(particles)
            other.remove_from_space(space)
            # self.chromosome.append(other.genome)
            to_remove_cells.add(other)'''


    def split(self,cells, grid, grid_size, space):
        grid_x = int(self.position[0]) // grid_size
        grid_y = int(self.position[1]) // grid_size
        x = grid_x * grid_size
        y = grid_y * grid_size

        if self.mass >= self.genome.max_mass:
            new_chrome1 = []
            new_chrome2 = []
            for genome in self.chromosome:
                new_genome1 = copy.deepcopy(genome)
                new_genome2 = copy.deepcopy(genome)

                new_genome1.mutate_gene()
                new_genome2.mutate_gene()

                new_chrome1.append(new_genome1)
                new_chrome2.append(new_genome2)

            active_gene1 = random.randint(0, len(new_chrome1)-1)
            active_gene2 = random.randint(0, len(new_chrome2)-1)
            pos1 = self.body.position[0] - new_chrome1[active_gene1].size, self.body.position[1]
            pos2 = self.body.position[0] + new_chrome2[active_gene2].size, self.body.position[1]

            new_cell1 = Cell(pos1,new_chrome1,active_gene1)
            new_cell2 = Cell(pos2,new_chrome2,active_gene2)

            new_mass = new_cell1.genome.start_mass + new_cell2.genome.start_mass
            '''# effort to maintain mass in the system (matter aint created nor destroyed)

            # 1. make sure mass isnt created
            while new_mass > self.mass:
                cell = random.randint(1,2)
                if cell == 1:
                    new_cell1.genome.start_mass -= 1
                else:
                    new_cell2.genome.start_mass -=1

                new_mass = new_cell1.genome.start_mass + new_cell2.genome.start_mass
            '''
            # 2. make sure mass isnt destroyed
            if new_mass < self.mass:
                count = self.mass - new_mass
                x_bounds = (x, x + grid_size - 1)
                y_bounds = (y, y + grid_size - 1)
                particles = []
                for _ in range(count):
                    x = random.randint(*x_bounds)
                    y = random.randint(*y_bounds)

                    color = random.randint(1, 100)
                    if color <= 50:
                        particle = Particle((x, y), 255, 0, 0)
                    elif 50 < color <= 85:
                        particle = Particle((x, y), 0, 255, 0)
                    else:
                        particle = Particle((x, y), 0, 0, 255)

                    particles.append(particle)
                grid[(grid_x, grid_y)].extend(particles)

            '''print("\n")
            print("Old Cell Mass:", self.mass)
            print("New Cell 1 Mass:", new_cell1.genome.start_mass)
            print("New Cell 1 Max Mass:", new_cell1.genome.max_mass)
            print("New Cell 2 Mass:", new_cell2.genome.start_mass)
            print("New Cell 2 Max Mass:", new_cell2.genome.max_mass)
            print("\n")'''

            if self.is_player:
                new_cell1.is_player = True

            cells.remove(self)
            cells.append(new_cell1)
            new_cell1.add_to_space(space)
            new_cell1.set_collision_type(len(cells) - 1)

            if len(cells) < 400:
                cells.append(new_cell2)
                new_cell2.add_to_space(space)
                new_cell2.set_collision_type(len(cells))

    def death(self,grid, grid_size):
        grid_x = int(self.position[0] // grid_size)
        grid_y = int(self.position[1] // grid_size)
        particles = []
        '''if self.dead:
            print(f"[Warning] Tried to kill already-dead cell: {self}")
            return
        self.dead = True'''
        print(f"{self} died with mass {self.mass}")

        for i in range(self.mass):
            # create a new cell
            theta = i*2*math.pi/self.mass
            particle_x = (self.body.position[0] + math.cos(theta)*self.size)
            particle_y = (self.body.position[1] + math.sin(theta)*self.size)
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
        grid[(grid_x,grid_y)].extend(particles)




class Genome:
    def __init__(self, r: int = 255, g: int = 255, b: int = 255, size: int = 10, start_mass: int = 20, max_mass: int = 40,
                 thickness: int = 1, strength: int = 1, speed: int = 50, perception = {"r": False, "g": False, "b": False}, detection_radius: int = 1, max_age: int = 30, charge: int = 0,
                 mutation_rate: float = 0.1, exploding: bool = False, multi_cell: bool = False, behaviour = {'r': 0.0, 'g': 0.0, 'b': 0.0}, p_consumption = {'r': True, 'g': True, 'b': True}, c_consumption = {'r': True, 'g': True, 'b': True}
                ):

        # Physical
        self.r = r
        self.g = g
        self.b = b
        self.size = size
        self.start_mass = start_mass
        self.max_mass = max_mass
        self.thickness = thickness
        self.strength = strength
        self.speed = speed
        self.detection_radius = detection_radius
        self.max_age = max_age
        self.charge = charge
        self.mutation_rate = mutation_rate
        self.exploding = exploding
        self.multi_cell = multi_cell

        # Behavioral
        self.behavior = behaviour
        self.p_consumption = p_consumption
        self.c_consumption = c_consumption
        self.perception = perception

    def mutate_gene(self):
        # expect at least one of rgb to be 255
        # defense: +size, +start_mass, +max_mass, +thickness, -speed +detection_radius, +max_age
        if self.r == 255:

            # behavioural
            # TODO: flocking
            if random.random() < self.mutation_rate:
                self.behavior['r'] = random.uniform(-1.0, 1.0)

            if random.random() < self.mutation_rate:
                self.behavior['g'] = random.uniform(-1.0, 1.0)

            if random.random() < self.mutation_rate:
                self.behavior['b'] = random.uniform(-1.0, 1.0)

            # physical
            # buffs
            # faster movement speed
            if random.random() < self.mutation_rate:
                self.speed += random.randint(1,5)

            # TODO: increased offspring

            # nerfs
            # smaller size
            if random.random() < self.mutation_rate:
                self.size -= random.randint(1,5)
                if self.size < 5:
                    self.size = 5

            # lose ability to consume red cells
            if random.random() < self.mutation_rate:
                self.c_consumption['r'] = False

            # lose ability to consume green cells
            if random.random() < self.mutation_rate:
                self.c_consumption['g'] = False

            # psychological
            # gain ability to see red
            if random.random() < self.mutation_rate:
                if not (self.perception["b"] and self.perception["g"]):
                    self.perception["r"] = True

            # lose ability to see blue
            if random.random() < self.mutation_rate:
                if self.perception["b"]:
                    self.perception["b"] = False

        # offense:
        elif self.g == 255:
            # behavioural
            # TODO: hunting behaviour
            if random.random() < self.mutation_rate:
                self.behavior['r'] += random.uniform(-1.0, 2.0)

            if random.random() < self.mutation_rate:
                self.behavior['g'] = random.uniform(-1.0, 1.0)

            if random.random() < self.mutation_rate:
                self.behavior['b'] = random.uniform(-1.0, 1.0)

            # physical
            # buffs
            # increased start size
            if random.random() < self.mutation_rate:
                self.size += random.randint(1,5)

            # faster movement speed
            if random.random() < self.mutation_rate:
                self.speed += random.randint(1, 5)

            # gain age
            if random.random() < self.mutation_rate:
                self.max_age += random.randint(1,5)

            # gain ability to eat green particles
            if random.random() < self.mutation_rate:
                self.p_consumption['g'] = True

            # gain ability to eat red cells
            if random.random() < self.mutation_rate:
                self.c_consumption['r'] = True

            # nerfs
            # lose ability to consume red particles
            if random.random() < self.mutation_rate:
                self.p_consumption['r'] = False

            # psychological
            if random.random() < self.mutation_rate:
                if not (self.perception["r"] and self.perception["b"]):
                    self.perception["g"] = True


        # special:
        else:
            if random.random() < self.mutation_rate:
                self.behavior['r'] += random.uniform(-1.0, 1.0)

            if random.random() < self.mutation_rate:
                self.behavior['g'] += random.uniform(-1.0, 1.0)

            if random.random() < self.mutation_rate:
                self.behavior['b'] += random.uniform(-1.0, 1.0)

            # resets
            # regain ability to eat red particles
            if random.random() < self.mutation_rate:
                self.p_consumption['r'] = True

            # regain ability to eat green cells
            if random.random() < self.mutation_rate:
                self.c_consumption['g'] = True

            # lose ability to see red
            if random.random() < self.mutation_rate:
                if self.perception["r"]:
                    self.perception["r"] = False

            # lose ability to see green
            if random.random() < self.mutation_rate:
                if self.perception["g"]:
                    self.perception["g"] = False

            # if not able to see red gain ability to see blue
            if random.random() < self.mutation_rate:
                if not self.perception["r"]:
                    self.perception["b"] = True

            # special abilities
            if random.random() < self.mutation_rate:
                self.exploding = True

            if random.random() < self.mutation_rate:
                self.thickness = 1

            # nerfs
            # lose age
            if random.random() < self.mutation_rate:
                self.max_age -= random.randint(1, 5)
                if self.max_age < 30:
                    self.max_age = 30

            # lose size
            if random.random() < self.mutation_rate:
                self.size -= random.randint(1,5)
                if self.size < 5:
                    self.size = 5


    def __str__(self):
        return '''PHYSICAL: color: {self.r}, {self.g}, {self.b}, size: {self.size}, start_mass: {self.start_mass}, max_mass: {self.max_mass}, 
                thickness: {self.thickness}, strength: {self.strength}, speed: {self.speed}, detection_radius: {self.detection_radius}, 
                max_age: {self.max_age}, charge: {self.charge}, mutation_rate: {self.mutation_rate}, multi_cell: {self.multi_cell}
                
                BEHAVIOURAL: aggression: {self.aggression}, caution: {self.caution}'''.format(self=self)

