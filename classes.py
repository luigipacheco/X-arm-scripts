__author__ = "Luis Pacheco , Madeline Gannon"
__contributors__ = ""
__license__ = "GPL"
__version__ = "0.0.1"
__maintainer__ = "Luis Pacheco"
__email__ = "luigi@luigipacheco.com"
__status__ = "Alpha"

import pygame
import time
import numpy as np

class Agent:
    """A tracked point that reports when it enters and exits a designated Tracking Zone  (Class copied and adapted from Madeline Gannon) """

    def __init__(
        self,
        id,
        initial_pos=np.array([0, 0, 0]),
        kp=1.5,
        kd=2.0,
        steering_scalar=0.5,
        radius=50,
        color=np.array([1, 1, 0]),
    ) -> None:
        self.id = id
        self.color = color
        self.radius = radius
        self._initial_position = np.array([initial_pos[0], initial_pos[1], 0])

        self._pos_desired = np.array([0, 0, 0])
        self._pos_current = initial_pos
        self._vel_desired = np.array([0, 0, 0])
        self._vel_current = np.array([0, 0, 0])

        self._acceleration = np.array([0, 0, 0])
        self._heading = np.array([0, 0, 0])
        self._vel_projected = np.array([0, 0, 0])
        self.steering_scalar = steering_scalar

        self.kp = kp  # proportional gains (stiffness)
        self.kd = kd  # deriviative gains (damping)
        self.dt = 1 / 60.0

        self._trail = []
        return

    def update(self, target):
        # update the desired position
        self._pos_desired = target

        self._update_desired_velocity()
        self._update_current_velocity()
        self._update_current_position()

        self._trail.append(self._pos_current)
        if len(self._trail) > 50:
            self._trail.pop(0)
        return

    def _update_desired_velocity(self):
        # update the heading direction
        self._heading = self._pos_desired - self._pos_current

        # update the desired velocity
        if self._heading.any():  # check if all zeros, because we don't want to divide by zero
            n = self._heading / np.linalg.norm(self._heading, 2)
        else:
            n = self._heading

        vel_projected = self._pos_current + n

        self._vel_desired = vel_projected - self._pos_current
        return

    def _update_current_velocity(self):
        # move based on the difference in position, and
        # dampen based on the difference in velocity
        acceleration = self.kp * (self._pos_desired - self._pos_current) + self.kd * (
            self._vel_desired - self._vel_current
        )
        # update the current velocity (convert accel from m/s/s to m/s)
        self._vel_current = self._vel_current + acceleration * self.dt
        return

    def _update_current_position(self):
        self._pos_current = self._pos_current + self._vel_current * self.dt * self.steering_scalar
        return

    def draw(self):
        # Draw a box or sphere at the agent

        # Draw the trail of the agent (past points) polyline (list of points)
        return

    def reset(self):
        self._pos_desired = self._initial_position  # np.array([0,0,0])
        self._pos_current = self._initial_position  # np.array([0,0,0])
        self._vel_desired = np.array([0, 0, 0])
        self._vel_current = np.array([0, 0, 0])
        self._acceleration = np.array([0, 0, 0])
        self._heading = np.array([0, 0, 0])
        self._vel_projected = np.array([0, 0, 0])
        self._trail = []
        return

    def to_string(self):
        return

    def set_position(self, pos):
        self._pos_current = pos
    def get_position(self):
        return self._pos_current

class pAgent(pygame.sprite.Sprite):
    def __init__(self,color):
        super().__init__()
        self.image = pygame.Surface((16, 16))
        self.image.fill(color)
        self.rect = self.image.get_rect()  # Get rect of some size as 'image'.
        self.velocity = [0, 0]
        # Define boundaries (same as in agent.py)
        self.x_min = 205
        self.x_max = 700
        self.y_min = -400
        self.y_max = 400

    def update(self,agent):
        # Get the position from the agent
        pos_x, pos_y = agent.get_position()[:2]
        
        # Apply boundary constraints
        pos_x = max(self.x_min, min(self.x_max, pos_x))
        pos_y = max(self.y_min, min(self.y_max, pos_y))
        
        # Update the position
        self.rect.x = pos_x
        self.rect.y = pos_y

class Player(pygame.sprite.Sprite):
    def __init__(self, color,targetx,targety):
        super().__init__()
        self.image = pygame.Surface((32, 32))
        self.image.fill(color)
        self.rect = self.image.get_rect()  # Get rect of some size as 'image'.
        self.velocity = [0, 0]
        self.rect.move_ip(targetx,targety)
        self.x = self.rect.x
        self.y = self.rect.y
        self.color = color
    def change_color(self, color):
        self.image = pygame.Surface((32, 32))
        self.image.fill(color)
        self.color = color

    def update(self):
        self.change_color(self.color)
        self.x += self.velocity[0]
        self.y += self.velocity[1]
        self.rect.x = self.x
        self.rect.y = self.y

