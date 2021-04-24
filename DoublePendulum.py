import pygame
from pygame.locals import *
import math

g_constant = 1.5

# // TODO  Make trail system more efficient


class Pendulum:
    # Theta is the pendulum's angle of rotation with respect to the origin.
    # Length is the length of the pendulum
    # Mass is the mass of the pendulum
    # Acceleration is the second derivative of theta
    # Velocity is the first derivative of theta
    # The endpoint of a pendulum is it's bottom circle.
    # Trail_points are a collection of past endpoints(explained more later)
    def __init__(self, origin, theta, length, mass, acceleration = 0.1, velocity = 0.1):
        self.origin = origin
        self.theta = theta
        self.length = length
        self.mass = mass
        self.endpoint = [length * math.sin(theta) + self.origin[0], length * math.cos(theta) + self.origin[1]]
        self.trail_points = []
        self.acceleration = acceleration
        self.velocity = velocity

    def update_forces(self):
        # Because computers are fast, they update multiple times every second.
        # To adjust for this we scale down the acceleration and velocity numbers.
        # The speed at which a while loop updates may vary on your computer,
        # so feel free to mess around with these numbers.
        self.velocity += self.acceleration/100
        self.theta += self.velocity/100

    # Currently the trail system is inefficient. This is because we redraw everything on the screen every loop.
    # Because of this, the current trail system adds to a list of past endpoints with every loop.
    # Trail_length defines the max number of endpoints(or trail_points in this case) that will be redrawn.
    # When the number of trail_points exceeds this number, the first endpoint in the list is deleted.
    def draw(self, surface, line_color = [0, 0, 0], line_width = 5, dot_color = [0, 0, 0], radius = 10, trail = True,
             trail_radius = 3, trail_color = [0,0,0], trail_length = 200):
        if trail:
            if len(self.trail_points) > trail_length: self.trail_points.remove(self.trail_points[0])
            for point in self.trail_points:
                pygame.draw.circle(surface, trail_color, (int(point[0]), int(point[1])), trail_radius)

        self.endpoint = [self.length * math.sin(self.theta) + self.origin[0],
                         self.length * math.cos(self.theta) + self.origin[1]]
        pygame.draw.line(surface, line_color, self.origin, (int(self.endpoint[0]), int(self.endpoint[1])), line_width)
        pygame.draw.circle(surface, dot_color, (int(self.endpoint[0]), int(self.endpoint[1])), radius)


initial_pendulum = Pendulum([320, 300], 7 * math.pi/6, 150, 10)
final_pendulum = Pendulum([int(initial_pendulum.endpoint[0]), int(initial_pendulum.endpoint[1])], 0, 150, 8)

# This function utilizes an equation that calculates the accelerations for each pendulum.
# The one I used can be found here: https://www.myphysicslab.com/pendulum/double-pendulum-en.html
def update_double_pendulum_acceleration(initial_pendulum, final_pendulum):

    num1 = (-g_constant * (2 * initial_pendulum.mass * final_pendulum.mass) * math.sin(initial_pendulum.theta))
    num2 = final_pendulum.mass * g_constant * math.sin(initial_pendulum.theta - (2 * final_pendulum.theta))
    num3 = 2 * math.sin(initial_pendulum.theta - final_pendulum.theta) * final_pendulum.mass
    num4 = ((final_pendulum.velocity ** 2) * final_pendulum.length) + ((initial_pendulum.velocity ** 2) *
                                                                       initial_pendulum.length *
                                                                       math.cos(initial_pendulum.theta -
                                                                                final_pendulum.theta))
    denom = initial_pendulum.length * ((2 * initial_pendulum.mass + final_pendulum.mass -
                                        (final_pendulum.mass * math.cos(2 * initial_pendulum.theta -
                                                                        2 * final_pendulum.theta))))

    initial_pendulum.acceleration = (num1 - num2 - (num3 * num4)) / denom

    num1 = 2 * math.sin(initial_pendulum.theta - final_pendulum.theta)
    num2 = (initial_pendulum.velocity ** 2) * initial_pendulum.length * (initial_pendulum.mass + final_pendulum.mass)
    num3 = g_constant * (initial_pendulum.mass + final_pendulum.mass) * math.cos(initial_pendulum.theta)
    num4 = (final_pendulum.velocity ** 2) * final_pendulum.length * final_pendulum.mass * math.cos(
        initial_pendulum.theta -
        final_pendulum.theta)

    denom = final_pendulum.length * ((2 * initial_pendulum.mass + final_pendulum.mass -
                                      (final_pendulum.mass * math.cos(2 * initial_pendulum.theta -
                                                                      2 * final_pendulum.theta))))
    final_pendulum.acceleration = (num1 * (num2 + num3 + num4)) / denom


class App:
    def __init__(self):
        self._running = True
        self._display_surf = None
        self.size = self.weight, self.height = 640, 800
        self.background_color = (255, 255, 255)
        self.loop_iterations = 0
        self.add_force_event = pygame.USEREVENT + 1
        pygame.time.set_timer(self.add_force_event, 1000)


    def on_init(self):
        pygame.init()
        self._display_surf = pygame.display.set_mode(self.size, pygame.HWSURFACE | pygame.DOUBLEBUF)
        self._display_surf.fill(self.background_color)
        initial_pendulum.draw(self._display_surf)
        final_pendulum.draw(self._display_surf)
        pygame.display.update()
        self._running = True

    def on_event(self, event):
        if event.type == pygame.QUIT:
            self._running = False

    # The trail stall variable is a way of spacing out trail_points.
    # For example: a trail_stall variable of 5 will make it so the trail_points list only appends an endpoint
    # every 5 loops. The smaller the number, the closer spaced; the larger the number, the farther spaced.
    def on_loop(self, trail_stall = 5):
        self._display_surf.fill(self.background_color)
        if self.loop_iterations == trail_stall:
            initial_pendulum.trail_points.append(initial_pendulum.endpoint)
            final_pendulum.trail_points.append(final_pendulum.endpoint)
            self.loop_iterations = 0

        update_double_pendulum_acceleration(initial_pendulum, final_pendulum)
        final_pendulum.update_forces()
        initial_pendulum.update_forces()
        initial_pendulum.draw(self._display_surf)
        final_pendulum.origin = [int(initial_pendulum.endpoint[0]), int(initial_pendulum.endpoint[1])]
        final_pendulum.draw(self._display_surf)
        pygame.display.update()
        self.loop_iterations += 1

    def on_cleanup(self):
        pygame.quit()

    def on_execute(self):
        if self.on_init() == False:
            self._running = False

        while self._running:
            for event in pygame.event.get():
                self.on_event(event)
            self.on_loop()
        self.on_cleanup()


if __name__ == "__main__":
    theApp = App()
    theApp.on_execute()






