import pygame
import pymunk
import random

from pygame import VIDEORESIZE
from pygame.examples.scroll import zoom_factor

from interactions import distance_squared
from cell import Cell, Genome
from particle import Particle
from AI import CellAI

class Game:
    def __init__(self):
        self.font = pygame.font.SysFont("Arcade_Classic", 18)

        self.SCREEN_WIDTH = 1920
        self.SCREEN_HEIGHT = 1080
        self.fullscreen = False

        # special controls
        self.show_grid = False
        self.show_colors = False
        self.old_perception = {"r": False, "g": False, "b": False}

        # Fixed resolution for rendering
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.RESIZABLE)
        self.surface = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))

        # get monitor screen
        self.screen_width, self.screen_height = self.screen.get_size()
        print("Screen size:", self.screen_width, self.screen_height)

        # camera and zoom
        self.zoom_factor = 1.0
        self.zoom_speed = 0.025

        self.camera_x = 0
        self.camera_y = 0
        self.camera_speed = 5

        # physics space
        self.space = pymunk.Space()

        # initialize chunks and grid
        self.grid_size = 120
        self.chunk_size = 16
        self.num_chunks_x = 4
        self.num_chunks_y = 4

        # chunk and grid properties
        self.num_columns = self.chunk_size * self.num_chunks_x
        self.num_rows = self.chunk_size * self.num_chunks_y

        self.world_width = self.num_columns * self.grid_size
        self.world_height = self.num_rows * self.grid_size

        self.grid = {}
        self.particles = []

        self.init_grid()

        self.chunks = {}
        for chunk_x in range(self.num_chunks_x):
            for chunk_y in range(self.num_chunks_y):
                self.chunks[(chunk_x, chunk_y)] = []

        # Initialize player and game objects
        # self.player_speed = 1
        default_genome = Genome()
        init_chromosome = [default_genome]
        spawn_x = random.randint(0, self.world_width)
        spawn_y = random.randint(0, self.world_height)
        self.player = Cell((spawn_x, spawn_y), init_chromosome,is_player = True)
        self.player.add_to_space(self.space)
        self.player.set_collision_type(0)

        self.cells = [self.player]
        # self.particles = self.create_particles(5000)
        self.consumed_particles = []
        self.to_remove_cells = set()

        self.update_grid()

        self.clock = pygame.time.Clock()
        self.run = True
        self.prev_time = pygame.time.get_ticks()

        # handle collisions
        self.handler = self.space.add_default_collision_handler()
        self.handler.begin = self.begin_collision
        self.handler.pre_solve = self.pre_collision
        self.handler.post_solve = self.post_collision
        self.handler.separate = self.separate_collision

    def create_particles(self, count, x_bounds = None, y_bounds = None):
        particles = []
        for _ in range(count):
            if x_bounds and y_bounds:
                x = random.randint(*x_bounds)
                y = random.randint(*y_bounds)
            else:
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

    def scale(self, pos, offset = (0,0)):
        return pos[0] * self.zoom_factor + offset[0], pos[1] * self.zoom_factor + offset[1]

    def draw_walls(self, surface, offset=(0, 0)):
        wall_color = 255,255,255

        top_left = self.scale((0, 0), offset)
        top_right = self.scale((self.world_width, 0), offset)
        bottom_left = self.scale((0, self.world_height), offset)
        bottom_right = self.scale((self.world_width, self.world_height), offset)

        # Draw the four walls
        pygame.draw.line(surface, wall_color, top_left, top_right, 2)  # Top
        pygame.draw.line(surface, wall_color, bottom_left, bottom_right, 1)  # Bottom
        pygame.draw.line(surface, wall_color, top_left, bottom_left, 2)  # Left
        pygame.draw.line(surface, wall_color, top_right, bottom_right, 1)  # Right

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

    def init_grid(self):
        self.grid = {}

        for x in range(0, self.world_width, self.grid_size):
            for y in range(0, self.world_height, self.grid_size):
                grid_x = x // self.grid_size
                grid_y = y // self.grid_size
                self.grid[(grid_x, grid_y)] = []

                # Spawn 24 particles in this cell using create_particles
                new_particles = self.create_particles(24, (x, x + self.grid_size - 1), (y, y + self.grid_size - 1))
                self.grid[(grid_x, grid_y)].extend(new_particles)
                # print(grid_x, grid_y, new_particles, "\n")
                # self.particles.extend(new_particles)

    def update_grid(self):
        for key in self.grid:
            self.grid[key] = [obj for obj in self.grid[key] if isinstance(obj, Particle)]

        '''for particle in self.particles:
            grid_x = int(particle.position[0] // self.grid_size)
            grid_y = int(particle.position[1] // self.grid_size)

            # Clamp grid_x and grid_y to stay within initialized bounds
            grid_x = max(0, min(grid_x, self.world_width // self.grid_size - 1))
            grid_y = max(0, min(grid_y, self.world_height // self.grid_size - 1))

            self.grid[grid_x, grid_y].append(particle)'''

        for cell in self.cells:
            grid_x = int(cell.position[0] // self.grid_size)
            grid_y = int(cell.position[1] // self.grid_size)

            # Clamp grid_x and grid_y to stay within initialized bounds
            grid_x = max(0, min(grid_x, self.world_width // self.grid_size - 1))
            grid_y = max(0, min(grid_y, self.world_height // self.grid_size - 1))

            self.grid[grid_x, grid_y].append(cell)

    def draw_grid(self, surface, zoom_factor=1.0, offset=(0, 0)):
        color = (50, 50, 50)
        scaled_grid_size = self.grid_size * zoom_factor
        scaled_width = self.world_width * zoom_factor
        scaled_height = self.world_height * zoom_factor

        # Vertical lines
        x = 0
        while x <= scaled_width:
            start_pos = (x + offset[0], 0 + offset[1])
            end_pos = (x + offset[0], scaled_height + offset[1])
            pygame.draw.line(surface, color, start_pos, end_pos)
            x += scaled_grid_size

        # Horizontal lines
        y = 0
        while y <= scaled_height:
            start_pos = (0 + offset[0], y + offset[1])
            end_pos = (scaled_width + offset[0], y + offset[1])
            pygame.draw.line(surface, color, start_pos, end_pos)
            y += scaled_grid_size

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

    def get_objects_in_screen_area(self, obj_type, screen_rect, offset=(0, 0)):
        visible_objects = []

        # Convert screen rect to world-space coordinates using zoom
        left = (screen_rect.left - offset[0]) / self.zoom_factor
        right = (screen_rect.right - offset[0]) / self.zoom_factor
        top = (screen_rect.top - offset[1]) / self.zoom_factor
        bottom = (screen_rect.bottom - offset[1]) / self.zoom_factor

        # Clamp to world bounds if needed
        left = max(0, left)
        top = max(0, top)

        # Determine visible grid cells in world-space
        min_grid_x = int(left // self.grid_size)
        max_grid_x = int(right // self.grid_size)
        min_grid_y = int(top // self.grid_size)
        max_grid_y = int(bottom // self.grid_size)

        for grid_x in range(min_grid_x, max_grid_x + 1):
            for grid_y in range(min_grid_y, max_grid_y + 1):
                if (grid_x, grid_y) in self.grid:
                    for obj in self.grid[(grid_x, grid_y)]:
                        if obj_type == 'particle' and isinstance(obj, Particle):
                            visible_objects.append(obj)
                        elif obj_type == 'cell' and isinstance(obj, Cell):
                            visible_objects.append(obj)
                        # Add more types as needed

        return visible_objects

    def trigger_explosion(self, cell):
        # can be changed for greater explosion radii
        explosion_radius = 1
        nearby_objects = self.find_objects_within_radius(cell, explosion_radius)

        for obj in nearby_objects:
            if isinstance(obj, Cell) and (obj != cell) and (obj not in self.to_remove_cells):
                    self.to_remove_cells.add(obj)

    def simulate_vision(self, color):
        r, g, b = color
        brightness = (r + g + b)//3

        if self.player.genome.perception["r"]:
            if r < brightness:
                r = brightness
            vis_r = r
        else:
            vis_r = 0

        if self.player.genome.perception["g"]:
            if g < brightness:
                g = brightness
            vis_g = g
        else:
            vis_g = 0

        if self.player.genome.perception["b"]:
            if b < brightness:
                b = brightness
            vis_b = b
        else:
            vis_b = 0

        rp = vis_r if vis_r != 0 else brightness
        gp = vis_g if vis_g != 0 else brightness
        bp = vis_b if vis_b != 0 else brightness

        perceived_color = rp, gp, bp
        return perceived_color

    def update_camera(self):
        self.camera_x = (self.player.position[0] * self.zoom_factor) - self.screen_width / 2
        self.camera_y = (self.player.position[1] * self.zoom_factor) - self.screen_height / 2

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
                        self.screen_width, self.screen_height = self.screen.get_size()
                    else:
                        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
                        self.screen_width, self.screen_height = self.screen.get_size()

                if event.key == pygame.K_k:
                    self.player.age = self.player.genome.max_age + 1

                if event.key == pygame.K_g:
                    self.show_grid = not self.show_grid

                if event.key == pygame.K_c:
                    if self.player.age >= self.player.genome.max_age:
                        self.show_colors = not self.show_colors
                        if self.show_colors:
                            self.old_perception = self.player.genome.perception
                            self.player.genome.perception = {"r": True, "g": True, "b": True}
                        else:
                            self.player.genome.perception = self.old_perception

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                world_x = (mouse_x + self.camera_x) / self.zoom_factor
                world_y = (mouse_y + self.camera_y) / self.zoom_factor

                if event.button == 4:  # Scroll up to zoom in
                    if self.player.age >= self.player.genome.max_age:
                        self.zoom_factor += self.zoom_speed
                elif event.button == 5:  # Scroll down to zoom out
                    if self.player.age >= self.player.genome.max_age:
                        self.zoom_factor = max(self.zoom_factor - self.zoom_speed, 0.01)
                else:
                    pass

                # Recalculate camera offset to keep world_x/y under the cursor fixed
                self.camera_x = -mouse_x + world_x * self.zoom_factor
                self.camera_y = -mouse_y + world_y * self.zoom_factor

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
            cell.update()
            cell.age += delta_time
            nearby_objects = self.find_objects_within_radius(cell, cell.genome.detection_radius)

            for obj in nearby_objects:
                # if particle check consumed by cell
                if isinstance(obj, Particle) and distance_squared(cell, obj) < (cell.size ** 2):
                    if obj in self.consumed_particles:
                        pass
                    else:
                        cell.consume_particle(obj.mass, obj.r, obj.g, obj.b)
                        self.consumed_particles.append(obj)

                # if cell check consumed by cell
                if isinstance(obj, Cell) and (obj != cell) and (not obj.dead):
                    if distance_squared(cell, obj) < ((cell.size + obj.size)**2):
                            cell.consume_cell(obj, self.to_remove_cells)

            # check if cell can split
            cell.split(self.cells, self.space)
            if cell.is_player:
                self.player = cell
                self.zoom_factor = 50/cell.genome.size

            # make npc cells decide where to go next
            if cell != self.player:
                cell.body.velocity = CellAI(cell.genome.r, cell.genome.g, cell.genome.b).decide(cell, nearby_objects)

            self.handle_wrap_around(cell)

            if cell.age >= cell.genome.max_age:
                if cell.genome.exploding:
                    self.trigger_explosion(cell)
                if cell not in self.to_remove_cells:
                    self.to_remove_cells.add(cell)

                if cell == self.player:
                    #  self.run = False
                    pass

        for p in self.consumed_particles[:]:  # Iterate over a copy
            grid_x = int(p.position[0] // self.grid_size)
            grid_y = int(p.position[1] // self.grid_size)

            if (grid_x, grid_y) in self.grid:
                try:
                    self.grid[grid_x, grid_y].remove(p)
                except ValueError:
                    print(f"[Warning] Tried to remove particle from grid ({grid_x},{grid_y}) but it wasn't found.")

            self.consumed_particles.remove(p)

        # After looping, remove all marked cells
        for dead in self.to_remove_cells:
            dead.age = dead.genome.max_age
            # dead.death(self.grid, self.grid_size)
            grid_x = int(dead.position[0]) // self.grid_size
            grid_y = int(dead.position[1]) // self.grid_size
            x = grid_x * self.grid_size
            y = grid_y * self.grid_size

            # Spawn 24 particles in this cell using create_particles
            new_particles = self.create_particles(dead.mass, (x, x + self.grid_size - 1), (y, y + self.grid_size - 1))
            self.grid[(grid_x, grid_y)].extend(new_particles)
            dead.remove_from_space(self.space)
            if dead in self.cells:
                self.cells.remove(dead)

        self.to_remove_cells.clear()
        self.update_grid()

    def render(self):
        self.screen.fill((0, 0, 0))

        # Calculate the camera offset
        camera_offset = (-self.camera_x, -self.camera_y)

        # Draw cells with camera offsetsAWa
        for cell in self.cells:
            self.render_if_visible(cell, self.screen, camera_offset, self.screen_width, self.screen_height)
            #cell.draw(self.screen, offset=camera_offset)

        # Draw particles with camera offset
        if self.zoom_factor < 1:
            pass
        else:
            visible_particles = self.get_objects_in_screen_area('particle', screen_rect= self.screen.get_rect(), offset= camera_offset)
            for particle in visible_particles:
                self.render_if_visible(particle, self.screen, camera_offset, self.screen_width, self.screen_height)
            # particle.draw_particle(self.screen, offset=camera_offset)

        self.draw_walls(self.screen, offset=camera_offset)

        if self.show_grid:
            self.draw_grid(self.screen, self.zoom_factor, offset=camera_offset)

        fps = self.clock.get_fps()
        fps_text = self.font.render(f"FPS: {fps:.2f}", True, pygame.Color("white"))
        self.screen.blit(fps_text, (10, 10))

        pygame.display.flip()

    def render_if_visible(self, obj, surface, camera_offset, screen_width, screen_height):
        # Assume obj has a `draw(surface, camera_offset)` method
        # and a `.position` or `.body.position` attribute in world space

        # Get object's position
        if hasattr(obj, "body"):  # e.g., a physics object like a Cell
            pos = obj.body.position
            r,g,b = obj.genome.r, obj.genome.g, obj.genome.b
        elif hasattr(obj, "position"):  # e.g., a particle or wall
            pos = obj.position
            r,g,b = obj.r, obj.g, obj.b
        else:
            return  # Can't render if position isn't known

        # Compute screen-relative position
        screen_x = pos[0]*self.zoom_factor + camera_offset[0]
        screen_y = pos[1]*self.zoom_factor + camera_offset[1]

        # Check if object is within visible screen bounds (+buffer optional)
        buffer = 50  # To avoid pop-in if needed
        if (-buffer <= screen_x <= screen_width + buffer) and (-buffer <= screen_y <= screen_height + buffer):
            # TODO optimize perceived color
            perceived_color = self.simulate_vision((r,g,b))
            obj.draw(perceived_color, surface, self.zoom_factor, camera_offset)

    def run_game_loop(self):
        prev_cell_len = 0
        prev_particle_len = 5000
        prev_total_cell_mass = 0
        prev_total_mass = 0
        prev_zoom_factor = 0
        while self.run:
            delta_time = self.clock.tick(60) / 1000.0
            current_time = pygame.time.get_ticks()
            delta_time = (current_time - self.prev_time) / 1000.0
            self.prev_time = current_time

            self.handle_input()
            self.update(delta_time)
            self.render()
            self.space.step(delta_time)

            '''if self.zoom_factor != prev_zoom_factor:
                print("Zoom level:", self.zoom_factor)
                prev_zoom_factor = self.zoom_factor'''

            '''if prev_cell_len != len(self.cells):
                print("Amount of cells: ", len(self.cells))
                prev_cell_len = len(self.cells)'''

            # check if any grid cells are referencing the same list

            '''if prev_particle_len != len(self.particles):
                print("Amount of particles:", len(self.particles))
                prev_particle_len = len(self.particles)

            total_cell_mass = 0
            for cell in self.cells:
                total_cell_mass += cell.mass

            if prev_total_cell_mass != total_cell_mass:
                print("Total cell mass:", total_cell_mass)

            total_mass = total_cell_mass + len(self.particles)
            print("Total Mass:", total_mass)
            print("\n")'''




        pygame.quit()

if __name__ == "__main__":
    pygame.init()
    game = Game()
    game.run_game_loop()
