import pymunk


# create a class to initialize pymunk parameters

class PhysicsParticle:
    def __init__(self, mass, charge, density, position):
        self.mass = mass
        self.charge = charge
        self.density = density
        self.position = pymunk.Vec2d(position[0], position[1])
        self.body = None
        self.shape = None

    def create_body(self, moment, body_type=pymunk.Body.DYNAMIC):
        self.body = pymunk.Body(self.mass, moment, body_type)
        self.body.position = self.position

    def create_shape(self, vertices):
        self.shape = pymunk.Poly(self.body, vertices)
        # don't forget to change this when necessary
        self.shape.elasticity = 0.50
        self.shape.density = self.density

    # to be used in some cases instead of shape
    def create_circle(self, radius):
        self.shape = pymunk.Circle(self.body, radius)
        self.shape.elasticity = 0.5
        self.shape.friction = 0.9
        self.shape.density = self.density

    def add_to_space(self, space):
        space.add(self.body, self.shape)

    def remove_from_space(self, space):
        space.remove(self.body, self.shape)

    def set_collision_type(self, collision_type):
        """Assign a collision type to the shape for handling collisions."""
        if self.shape:
            self.shape.collision_type = collision_type
        else:
            print("Shape not initialized. Cannot set collision type.")

    def apply_force(self, force, point=(0, 0)):
        # Apply a force to the body at a specific point
        self.body.apply_force_at_local_point(force, point)

    def set_velocity(self, velocity):
        # Set the body's velocity
        self.body.velocity = velocity

    def update(self):
        self.position = self.body.position
