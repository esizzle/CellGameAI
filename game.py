import pygame
import random
from interactions import distance
from cell import Cell
from particle import Particle
from AI import CellAI

class Game:
    def __init__(self, width=800, height=400):
        self.screen_width = width
        self.screen_height = height
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        self.surface = pygame.Surface((self.screen_width, self.screen_height))

        self.clock = pygame.time.Clock()
        self.run = True

        # Initialize grid
        self.grid_size = 100
        self.grid = {}

        # create cells (lists) to store information inside grid
        for x in range(0, self.screen_width, self.grid_size):
            for y in range(0, self.screen_height, self.grid_size):
                self.grid[x // self.grid_size, y // self.grid_size] = []

        # Initialize player and game objects
        self.player_speed = 3
        self.player = Cell((self.screen_width / 2, self.screen_height / 2), is_player = True)
        self.cells = [self.player]
        self.split_cells = [self.player]
        self.particles = self.create_particles(100)
        self.consumed_particles = []
        self.update_grid()

        self.prev_time = pygame.time.get_ticks()

    def create_particles(self, count):
        particles = []
        for _ in range(count):
            x = random.randint(0, self.screen_width)
            y = random.randint(0, self.screen_height)
            color = random.randint(1, 3)

            if color == 1:
                particle = Particle((x, y), 255, 0, 0)
            elif color == 2:
                particle = Particle((x, y), 0, 255, 0)
            else:
                particle = Particle((x, y), 0, 0, 255)

            particles.append(particle)
        return particles

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

    def find_particles_within_radius(self, cell: Cell, radius):
        grid_x = int(cell.position[0] // self.grid_size)
        grid_y = int(cell.position[1] // self.grid_size)

        # Determine which grid cells to check
        neighboring_cells = [
            (grid_x + dx, grid_y + dy)
            for dx in [-1, 0 ,1]
            for dy in [-1, 0 ,1]
        ]

        nearby_particles = []
        for nx, ny in neighboring_cells:
            if (nx, ny) in self.grid:
                for particle in self.grid[(nx, ny)]:
                    if distance(cell, particle)<= radius:
                        nearby_particles.append(particle)


        return nearby_particles

    def handle_input(self):
        keys = pygame.key.get_pressed()
        player_x, player_y = self.player.position

        if keys[pygame.K_a]:
            player_x -= self.player_speed
        if keys[pygame.K_d]:
            player_x += self.player_speed
        if keys[pygame.K_w]:
            player_y -= self.player_speed
        if keys[pygame.K_s]:
            player_y += self.player_speed

        self.player.position = (player_x, player_y)

    def update(self, delta_time):
        for cell in self.cells:
            cell.age += delta_time

            if cell.age >= cell.max_age:
                cell.death(self.particles)
                self.cells.remove(cell)
                self.update_grid()

                if cell == self.player:
                    if self.cells:
                        self.player = self.split_cells[0]
                        self.player.position = self.player.position
                    else:
                        self.run = False

        for cell in self.cells:
            cell.split(self.cells)
            if cell == self.player:
                self.split_cells[0] = self.cells[-1]

        for particle in self.particles[:]:
            for cell in self.cells:
                if distance(cell, particle) < cell.size:
                    cell.consume(particle.mass, particle.r, particle.g, particle.b)
                    self.consumed_particles.append(particle)
                    self.update_grid()

        self.particles = [p for p in self.particles if p not in self.consumed_particles]

        for cell in self.cells:
            if cell != self.player:
                radius = 100 # temporary for testing
                nearby_particles = self.find_particles_within_radius(cell, radius)

                move_x, move_y = CellAI(cell.r, cell.g, cell.b).decide(cell,nearby_particles)

                cell.position = (cell.position[0]+ move_x, cell.position[1] + move_y)

    def render(self):
        self.screen.fill((0, 0, 0))
        self.surface.fill((0, 0, 0))

        for cell in self.cells:
            cell.draw_cell(self.screen)
        for particle in self.particles:
            particle.draw_particle(self.screen)

        pygame.display.flip()

    def run_game_loop(self):
        while self.run:
            delta_time = self.clock.tick(60) / 1000.0
            current_time = pygame.time.get_ticks()
            delta_time = (current_time - self.prev_time) / 1000.0
            self.prev_time = current_time

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.run = False

            self.handle_input()
            self.update(delta_time)
            self.render()

        pygame.quit()

if __name__ == "__main__":
    pygame.init()
    game = Game()
    game.run_game_loop()
