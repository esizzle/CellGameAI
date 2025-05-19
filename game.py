import pygame
import pymunk
import random

from pygame import VIDEORESIZE

from interactions import distance
from cell import Cell, Genome
from particle import Particle
from AI import CellAI

class Game:
    def __init__(self, width=1920, height=1080):
        self.font = pygame.font.SysFont("Arcade_Classic", 18)

        # Fixed resolution for rendering
        self.screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
        self.screen_width, self.screen_height = self.screen.get_size()
        print("Screen size:", self.screen_width, self.screen_height)

        self.fullscreen = False
        self.width = width
        self.height = height
        self.world_width = width
        self.world_height = height

        self.surface = pygame.Surface((self.screen_width, self.screen_height))
        self.space = pymunk.Space()

        self.clock = pygame.time.Clock()
        self.run = True

        # Initialize grid
        self.grid_size = 100
        self.grid = {}

        # self.create_walls()

        # create cells (lists) to store information inside grid
        for x in range(0, self.screen_width, self.grid_size):
            for y in range(0, self.screen_height, self.grid_size):
                self.grid[x // self.grid_size, y // self.grid_size] = []

        # Initialize player and game objects
        # self.player_speed = 1
        default_genome = Genome()
        init_chromosome = [default_genome]
        self.player = Cell((self.screen_width / 2, self.screen_height / 2), init_chromosome,is_player = True)
        self.player.add_to_space(self.space)
        self.player.set_collision_type(0)

        self.camera_x = self.player.position[0] - self.screen_width // 2
        self.camera_y = self.player.position[1] - self.screen_height // 2
        self.camera_speed = 2

        self.cells = [self.player]
        self.particles = self.create_particles(5000)
        self.consumed_particles = []
        self.to_remove_cells = set()

        self.update_grid()

        self.prev_time = pygame.time.get_ticks()

        # handle collisions
        self.handler = self.space.add_default_collision_handler()
        self.handler.begin = self.begin_collision
        self.handler.pre_solve = self.pre_collision
        self.handler.post_solve = self.post_collision
        self.handler.separate = self.separate_collision

    def create_particles(self, count):
        particles = []
        for _ in range(count):
            x = random.randint(0, self.screen_width)
            y = random.randint(0, self.screen_height)
            color = random.randint(1, 100)

            if color <= 33:
                particle = Particle((x, y), 255, 0, 0)
            elif 33 < color <= 67:
                particle = Particle((x, y), 0, 255, 0)
            else:
                particle = Particle((x, y), 0, 0, 255)

            particles.append(particle)
        return particles

    def create_walls(self):
        thickness = 1  # Thickness of the wall segments

        # Create 4 segments around the edges of the world
        walls = [
            pymunk.Segment(self.space.static_body, (0, 0), (self.screen_width, 0), thickness),  # Top
            pymunk.Segment(self.space.static_body, (0, self.screen_height), (self.screen_width, self.screen_height),
                           thickness),  # Bottom
            pymunk.Segment(self.space.static_body, (0, 0), (0, self.screen_height), thickness),  # Left
            pymunk.Segment(self.space.static_body, (self.screen_width, 0), (self.screen_width, self.screen_height),
                           thickness),  # Right
        ]

        # Optional: set properties of the walls
        for wall in walls:
            wall.elasticity = 1.0  # Bounciness
            wall.friction = 0.5
            wall.collision_type = 1000  # Arbitrary number for walls if needed

        self.space.add(*walls)

    def handle_wrap_around(self, obj):
        x, y = obj.body.position
        w, h = self.world_width, self.world_height  # Define your world size

        if x - obj.size < 0:
            obj.body.position = (w -obj.size, y)
        elif x + obj.size > w:
            obj.body.position = (0 + obj.size, y)

        if y - obj.size < 0:
            obj.body.position = (x, h - obj.size)
        elif y + obj.size > h:
            obj.body.position = (x, 0 + obj.size)


    def draw_walls(self, surface,  offset=(0, 0)):
        wall_color = (255, 255, 255)
        pygame.draw.line(surface, wall_color, (0 + offset[0], 0 + offset[1]), (self.screen_width + offset[0], 0 + offset[1]), 2)  # Top
        pygame.draw.line(surface, wall_color, (0 + offset[0], self.screen_height + offset[1]), (self.screen_width + offset[0], self.screen_height + offset[1]),
                         1)  # Bottom
        pygame.draw.line(surface, wall_color, (0 + offset[0], 0 + offset[1]), (0 + offset[0], self.screen_height + offset[1]), 2)  # Left
        pygame.draw.line(surface, wall_color, (self.screen_width + offset [0], 0 + offset[1]), (self.screen_width + offset[0], self.screen_height + offset[1]),
                         1)  # Right

    # Create the collision handler (outside the game loop)
    def begin_collision(self, arbiter, space, data):
        # print("Collision occurred!")
        return True  # Return False if you want to ignore the collision

    def pre_collision(self, arbiter, space, data):
        # print("Pre solve")
        return True

    def post_collision(self,arbiter, space, data):
        # print("Post solve")
        pass

    def separate_collision(self, arbiter, space, data):
        # print("Separate")
        pass

    def update_grid(self):
        for key in self.grid:
            self.grid[key] = []

        for particle in self.particles:
            grid_x = int(particle.position[0] // self.grid_size)
            grid_y = int(particle.position[1] // self.grid_size)

            # Clamp grid_x and grid_y to stay within initialized bounds
            grid_x = max(0, min(grid_x, self.screen_width // self.grid_size - 1))
            grid_y = max(0, min(grid_y, self.screen_height // self.grid_size - 1))

            self.grid[grid_x, grid_y].append(particle)

        for cell in self.cells:
            grid_x = int(cell.position[0] // self.grid_size)
            grid_y = int(cell.position[1] // self.grid_size)

            # Clamp grid_x and grid_y to stay within initialized bounds
            grid_x = max(0, min(grid_x, self.screen_width // self.grid_size - 1))
            grid_y = max(0, min(grid_y, self.screen_height // self.grid_size - 1))

            self.grid[grid_x, grid_y].append(cell)

    def update_camera(self):
        self.camera_x = self.player.position[0] - self.screen_width / 2
        self.camera_y = self.player.position[1] - self.screen_height / 2


    # grid_radius = 1 -> 3x3 grid
    # grid_radius = 2 -> 5x5 grid
    # grid_radius = 3 -> 7x7 grid
    def find_objects_within_radius(self, cell: Cell, grid_radius: int):
        grid_x = int(cell.position[0] // self.grid_size)
        grid_y = int(cell.position[1] // self.grid_size)

        # Determine which grid cells to check based on `grid_radius`
        neighboring_cells = [
            (grid_x + dx, grid_y + dy)
            for dx in range(-grid_radius, grid_radius + 1)
            for dy in range(-grid_radius, grid_radius + 1)
        ]

        nearby_objects = []
        for nx, ny in neighboring_cells:
            if (nx, ny) in self.grid:
                nearby_objects.extend(self.grid[(nx, ny)])

        return nearby_objects

    def trigger_explosion(self, cell):
        # can be changed for greater explosion radii
        explosion_radius = 1
        nearby_objects = self.find_objects_within_radius(cell, explosion_radius)

        for obj in nearby_objects:
            if isinstance(obj, Cell) and (obj != cell) and (obj not in self.to_remove_cells):
                obj.death(self.particles)
                obj.age = obj.genome.max_age
                obj.remove_from_space(self.space)
                self.cells.remove(obj)


    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.run = False

            if event.type == VIDEORESIZE:
                if not self.fullscreen:
                    self.fullscreen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_f:
                    self.fullscreen = not self.fullscreen
                    if self.fullscreen:
                        self.screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
                    else:
                        self.screen = pygame.display.set_mode((self.width, self.height))

        keys = pygame.key.get_pressed()
        speed = self.camera_speed * (2 if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT] else 1)

        if keys[pygame.K_a]:
            if self.player.age >= self.player.genome.max_age:
                self.camera_x -= speed
            else:
                self.player.body.velocity = -self.player.genome.speed, self.player.body.velocity[1]
        if keys[pygame.K_d]:
            if self.player.age >= self.player.genome.max_age:
                self.camera_x += speed
            else:
                self.player.body.velocity = self.player.genome.speed, self.player.body.velocity[1]

        if keys[pygame.K_w]:
            if self.player.age >= self.player.genome.max_age:
                self.camera_y -= speed
            else:
                self.player.body.velocity = self.player.body.velocity[0], -self.player.genome.speed

        if keys[pygame.K_s]:
            if self.player.age >= self.player.genome.max_age:
                self.camera_y += speed
            else:
                self.player.body.velocity = self.player.body.velocity[0], self.player.genome.speed

        if self.player.age < self.player.genome.max_age:
            self.update_camera()

    def update(self, delta_time):
        for cell in self.cells:
            cell.age += delta_time

            if cell.age >= cell.genome.max_age:
                if cell.genome.exploding:
                    self.trigger_explosion(cell)
                cell.death(self.particles)
                self.cells.remove(cell)
                cell.remove_from_space(self.space)

                if cell == self.player:
                    #  self.run = False
                    pass
        for cell in self.cells:
            cell.split(self.cells,self.space)
            if cell.is_player:
                self.player = cell


        # only using nearby particles, check if cell is eating a particle
        for cell in self.cells:
            nearby_objects = self.find_objects_within_radius(cell, cell.genome.detection_radius)

            for obj in nearby_objects:
                if isinstance(obj, Particle) and distance(cell, obj) < cell.size:
                    cell.consume_particle(obj.mass, obj.r, obj.g, obj.b)
                    self.consumed_particles.append(obj)

        to_remove = set(self.consumed_particles)
        self.particles = [p for p in self.particles if p not in to_remove]


        # check if cell eat other cells
        for cell in self.cells:
            nearby_objects = self.find_objects_within_radius(cell, cell.genome.detection_radius)
            for obj in nearby_objects:
                if isinstance(obj, Cell) and (obj != cell) and (obj not in self.to_remove_cells):
                    if distance(cell, obj) < cell.size + obj.size:
                        cell.consume_cell(obj, self.cells, self.particles, self.space, self.to_remove_cells)

        # After looping, remove all marked cells
        for dead in self.to_remove_cells:
            dead.age = dead.genome.max_age
            if dead in self.cells:
                self.cells.remove(dead)

        for cell in self.cells:
            cell.update()
            if cell != self.player:
                radius = 100 # temporary for testing
                nearby_objects = self.find_objects_within_radius(cell, cell.genome.detection_radius)

                cell.body.velocity = CellAI(cell.genome.r, cell.genome.g, cell.genome.b).decide(cell, nearby_objects)

        for cell in self.cells:
            self.handle_wrap_around(cell)

        self.update_grid()

    def render(self):
        self.screen.fill((0, 0, 0))

        # Calculate the camera offset
        camera_offset = (-self.camera_x, -self.camera_y)

        # Draw cells with camera offset
        for cell in self.cells:
            cell.draw_cell(self.screen, offset=camera_offset)

        # Draw particles with camera offset
        for particle in self.particles:
            particle.draw_particle(self.screen, offset=camera_offset)

        self.draw_walls(self.screen, offset=camera_offset)

        fps = self.clock.get_fps()
        fps_text = self.font.render(f"FPS: {fps:.2f}", True, pygame.Color("white"))
        self.screen.blit(fps_text, (10, 10))

        pygame.display.flip()

    def run_game_loop(self):
        prev_cell_len = 0
        while self.run:
            delta_time = self.clock.tick(60) / 1000.0
            current_time = pygame.time.get_ticks()
            delta_time = (current_time - self.prev_time) / 1000.0
            self.prev_time = current_time

            self.handle_input()
            self.update(delta_time)
            self.render()
            self.space.step(delta_time)


            if prev_cell_len != len(self.cells):
                print("Amount of cells: ", len(self.cells))
                prev_cell_len = len(self.cells)


        pygame.quit()

if __name__ == "__main__":
    pygame.init()
    game = Game()
    game.run_game_loop()
