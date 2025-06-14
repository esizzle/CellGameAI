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
        self.size = self.genome.start_mass // 2
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
        self.size = self.mass // 2


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

    def consume_particle(self, mass, r,g,b):
        self.calculate_mass(mass)
        self.calculate_colour(mass, r,g,b)

    def consume_cell(self, other, to_remove_cells):
        if (self.mass > (4 * other.mass/3)) and (other.genome.thickness == 1):
            # self.chromosome.append(other.genome)
            other.dead = True
            other.age = other.genome.max_age + 1
            to_remove_cells.add(other)

        '''elif  (self.mass > (2 * other.mass)) and (other.genome.thickness == 2):
            other.death(particles)
            other.remove_from_space(space)
            # self.chromosome.append(other.genome)
            to_remove_cells.add(other)'''


    def split(self,cells, space):

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

            '''new_mass = new_cell1.genome.start_mass + new_cell2.genome.start_mass

            # effort to maintain mass in the system (matter aint created nor destroyed)
            # 1. make sure mass isnt created
            while new_mass > self.mass:
                cell = random.randint(1,2)
                if cell == 1:
                    new_cell1.genome.start_mass -= 1
                else:
                    new_cell2.genome.start_mass -=1

                new_mass = new_cell1.genome.start_mass + new_cell2.genome.start_mass

            # 2. make sure mass isnt destroyed
            if new_mass < self.mass:
                for i in range(self.mass - new_mass):
                    # create a new cell
                    theta = i * 2 * math.pi / (self.mass - new_mass)
                    particle_x = self.body.position[0] + math.cos(theta) * max(new_cell1.size, new_cell2.size)
                    particle_y = self.body.position[1] + math.sin(theta) * max(new_cell1.size, new_cell2.size)
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

            print("\n")
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
                 mutation_rate: float = 0.1, exploding: bool = False, multi_cell: bool = False, behaviour = {'r': 0.0, 'g': 0.0, 'b': 0.0}, aggression: float = 1, caution: float = 1
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
        self.perception = perception
        self.detection_radius = detection_radius
        self.max_age = max_age
        self.charge = charge
        self.mutation_rate = mutation_rate
        self.exploding = exploding
        self.multi_cell = multi_cell

        # Behavioral
        self.behavior = behaviour
        self.aggression = aggression
        self.caution = caution

    def mutate_gene(self):
        # expect at least one of rgb to be 255
        # defense: +size, +start_mass, +max_mass, +thickness, -speed +detection_radius, +max_age
        if self.r == 255:
            if random.random() < self.mutation_rate:
                self.caution += random.uniform(1.0,5.0)
            if random.random() < self.mutation_rate:
                self.aggression -= random.uniform(1.0,5.0)
                if self.aggression < 0.1:
                    self.aggression = 0.1

            if random.random() < self.mutation_rate:
                self.behavior['r'] = random.uniform(-1.0, 1.0)

            if random.random() < self.mutation_rate:
                self.behavior['g'] = random.uniform(-1.0, 1.0)

            if random.random() < self.mutation_rate:
                self.behavior['b'] = random.uniform(-1.0, 1.0)

            '''if random.random() < self.mutation_rate:
                self.size += random.randint(1,5)
                self.max_mass += random.randint(1,5)
                self.speed -= random.randint(0,10)

                # clamp speed
                if self.speed < 1:
                    self.speed = 1'''
            '''if random.random() < self.mutation_rate:
                self.start_mass += random.randint(5,10)
                self.max_mass = 2*self.start_mass'''

            # thicker membrane // slower movement speed
            if random.random() < self.mutation_rate:
                self.thickness = 2
                self.speed -= random.randint(1,5)
                if self.speed < 1:
                    self.speed = 1

            # faster movement speed // smaller particle
            if random.random() < self.mutation_rate:
                self.speed += random.randint(1,5)
                self.start_mass -= random.randint(1, 5)
                if self.start_mass < 5:
                    self.start_mass = 5
                self.max_mass = 2*self.start_mass
                # self.max_age -= random.randint(1, 5)
                if self.max_age < 5:
                    self.max_age = 5

            # faster movement speed // smaller cell wall
            if random.random() < self.mutation_rate:
                self.speed += random.randint(1,5)
                if self.thickness == 2:
                    self.thickness = 1

            '''if random.random() < self.mutation_rate:
                self.max_age += random.randint(1,5)'''

            if random.random() < self.mutation_rate:
                if not (self.perception["b"] and self.perception["g"]):
                    self.perception["r"] = True

            if random.random() < self.mutation_rate:
                if self.perception["g"]:
                    self.perception["g"] = False

            if random.random() < self.mutation_rate:
                if self.perception["b"]:
                    self.perception["b"] = False


        # offense:
        elif self.g == 255:
            if random.random() < self.mutation_rate:
                self.aggression += random.uniform(1.0,5.0)

            if random.random() < self.mutation_rate:
                self.caution -= random.uniform(1.0,5.0)

            if random.random() < self.mutation_rate:
                self.behavior['r'] = random.uniform(-1.0, 1.0)

            if random.random() < self.mutation_rate:
                self.behavior['g'] = random.uniform(-1.0, 1.0)

            if random.random() < self.mutation_rate:
                self.behavior['b'] = random.uniform(-1.0, 1.0)
            '''if random.random() < self.mutation_rate:
                self.strength = random.randint(1,2)
            if random.random() < self.mutation_rate:
                self.speed += random.randint(10,25)
                self.size -= random.randint(1,5)
                if self.size < 1:
                    self.size = 1'''
            '''if random.random() < self.mutation_rate:
                self.start_mass -= random.randint(1,5)
                self.max_mass = 2 * self.start_mass
                if self.start_mass < 5:
                    self.max_mass = 10
                    self.start_mass = 5
                if self.start_mass < self.size:
                    self.start_mass = self.size
                    self.max_mass = 2 * self.start_mass
            if random.random() < self.mutation_rate:
                self.detection_radius = random.randint(1, 3)
            if random.random() < self.mutation_rate:
                self.mutation_rate += random.uniform(0.01, 0.05)'''
            # increased start size // slower movement speed
            if random.random() < self.mutation_rate:
                self.size += random.randint(1,5)
                self.start_mass += random.randint(5, 10)
                self.max_mass = 2*self.start_mass
                self.speed -= random.randint(1,10)
                # self.max_age += random.randint(1, 5)

                if self.speed < 1:
                    self.speed = 1

            if random.random() < self.mutation_rate:
                self.thickness = 1

            if random.random() < self.mutation_rate:
                if not (self.perception["r"] and self.perception["b"]):
                    self.perception["g"] = True

            if random.random() < self.mutation_rate:
                if self.perception["r"]:
                    self.perception["r"] = False

            if random.random() < self.mutation_rate:
                if self.perception["b"]:
                    self.perception["b"] = False

        # special: charge = +/- 1, mutation_rate = rand(0.1,0.9), multi_cell = true
        else:
            if random.random() < self.mutation_rate:
                self.behavior['r'] = random.uniform(-1.0, 1.0)

            if random.random() < self.mutation_rate:
                self.behavior['g'] = random.uniform(-1.0, 1.0)

            if random.random() < self.mutation_rate:
                self.behavior['b'] = random.uniform(-1.0, 1.0)
            # exploding cells
            if random.random() < self.mutation_rate:
                self.exploding = True

            if random.random() < self.mutation_rate:
                self.thickness = 1

            if random.random() < self.mutation_rate:
                if not (self.perception["r"] and self.perception["g"]):
                    self.perception["b"] = True

            if random.random() < self.mutation_rate:
                if self.perception["r"]:
                    self.perception["r"] = False

            if random.random() < self.mutation_rate:
                if self.perception["g"]:
                    self.perception["g"] = False
            '''if random.random() < self.mutation_rate:
                self.detection_radius -= random.randint(1, 5)
            if random.random() < self.mutation_rate:
                self.thickness = random.choice([1,2])
            if random.random() < self.mutation_rate:
                self.charge = random.choice([-1,0,1])
            if random.random() < self.mutation_rate:
                self.r = 255
                self.g = 255
                self.b = 255
            if random.random() < self.mutation_rate:
                self.multi_cell = True'''

        self.max_age = self.max_mass

    def __str__(self):
        return '''PHYSICAL: color: {self.r}, {self.g}, {self.b}, size: {self.size}, start_mass: {self.start_mass}, max_mass: {self.max_mass}, 
                thickness: {self.thickness}, strength: {self.strength}, speed: {self.speed}, detection_radius: {self.detection_radius}, 
                max_age: {self.max_age}, charge: {self.charge}, mutation_rate: {self.mutation_rate}, multi_cell: {self.multi_cell}
                
                BEHAVIOURAL: aggression: {self.aggression}, caution: {self.caution}'''.format(self=self)

