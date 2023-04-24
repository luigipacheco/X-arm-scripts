__author__ = "Luis Pacheco , Madeline Gannon"
__contributors__ = ""
__license__ = "GPL"
__version__ = "0.0.1"
__maintainer__ = "Luis Pacheco"
__email__ = "luigi@luigipacheco.com"
__status__ = "Alpha"


import pygame
import pygame_gui
from xarm_controller import XArmController
from ui import draw_boundary_limits, handle_slider_events, UIElements

pygame.init()
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()
manager = pygame_gui.UIManager((800, 600))

agent = XArmController("192.168.1.217")  # Replace "192.168.1.100" with your xArm device's IP address.

ui_elements = UIElements(manager, agent)

running = True
while running:
    time_delta = clock.tick(60) / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.USEREVENT:
            handle_slider_events(event, ui_elements)

        manager.process_events(event)

    manager.update(time_delta)

    screen.fill((0, 0, 0))
    draw_boundary_limits(screen, 0, 800, 0, 600)
    agent.draw(screen)
    manager.draw_ui(screen)

    pygame.display.update()

pygame.quit()
