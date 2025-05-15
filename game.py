import pygame
import pymunk
import random
from interactions import distance
from cell import Cell, Genome
from particle import Particle
from AI import CellAI

class Game:
    def __init__(self, width=800, height=400):
        self.font = pygame.font.SysFont("Arcade_Classic", 18)

        self.screen_width = width
        self.screen_height = height
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        self.fullscreen = False

        self.surface = pygame.Surface((self.screen_width, self.screen_height))
        self.space = pymunk.Space()

        self.clock = pygame.time.Clock()
        self.run = True

        # Initialize grid
        self.grid_size = 100
        self.grid = {}

        self.create_walls()

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

        self.camera_x = self.player.position[0]
        self.camera_y = self.player.position[1]
        self.camera_speed = 2
        self.cells = [self.player]
        self.particles = self.create_particles(1000)
        self.consumed_particles = []
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
        thickness = 10  # Thickness of the wall segments

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
            wall.collision_type = 100  # Arbitrary number for walls if needed

        self.space.add(*walls)

    def draw_walls(self):
        wall_color = (255, 255, 255)
        pygame.draw.line(self.screen, wall_color, (0, 0), (self.screen_width, 0), 2)  # Top
        pygame.draw.line(self.screen, wall_color, (0, self.screen_height), (self.screen_width, self.screen_height),
                         2)  # Bottom
        pygame.draw.line(self.screen, wall_color, (0, 0), (0, self.screen_height), 2)  # Left
        pygame.draw.line(self.screen, wall_color, (self.screen_width, 0), (self.screen_width, self.screen_height),
                         2)  # Right

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

    def find_objects_within_radius(self, cell: Cell, radius):
        grid_x = int(cell.position[0] // self.grid_size)
        grid_y = int(cell.position[1] // self.grid_size)

        # Determine which grid cells to check
        neighboring_cells = [
            (grid_x + dx, grid_y + dy)
            for dx in [-1, 0 ,1]
            for dy in [-1, 0 ,1]
        ]

        nearby_objects = []
        for nx, ny in neighboring_cells:
            if (nx, ny) in self.grid:
                for objects in self.grid[(nx, ny)]:
                    if distance(cell, objects)<= radius:
                        nearby_objects.append(objects)


        return nearby_objects

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.run = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_f:
                    self.fullscreen = not self.fullscreen
                    if self.fullscreen:
                        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                    else:
                        self.screen = pygame.display.set_mode((800, 400))

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


        for particle in self.particles[:]:
            for cell in self.cells:
                if distance(cell, particle) < cell.genome.size:
                    cell.consume_particle(particle.mass, particle.r, particle.g, particle.b)
                    self.consumed_particles.append(particle)

        self.particles = [p for p in self.particles if p not in self.consumed_particles]

        for cell in self.cells:
            for other_cell in self.cells:
                if other_cell != cell:
                    if distance(cell, other_cell) < cell.genome.size+other_cell.genome.size:
                        cell.consume_cell(other_cell,self.cells,self.particles,self.space)



        for cell in self.cells:
            cell.update()
            if cell != self.player:
                radius = 100 # temporary for testing
                nearby_objects = self.find_objects_within_radius(cell, cell.genome.detection_radius)

                cell.body.velocity = CellAI(cell.genome.r, cell.genome.g, cell.genome.b).decide(cell, nearby_objects)

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

        fps = self.clock.get_fps()
        fps_text = self.font.render(f"FPS: {fps:.2f}", True, pygame.Color("white"))
        self.screen.blit(fps_text, (10, 10))

        pygame.display.flip()

    def run_game_loop(self):
        while self.run:
            delta_time = self.clock.tick(60) / 1000.0
            current_time = pygame.time.get_ticks()
            delta_time = (current_time - self.prev_time) / 1000.0
            self.prev_time = current_time

            self.handle_input()
            self.update(delta_time)
            self.render()
            self.space.step(delta_time)

        pygame.quit()

if __name__ == "__main__":
    pygame.init()
    game = Game()
    game.run_game_loop()
