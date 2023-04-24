__author__ = "Luis Pacheco , Madeline Gannon"
__contributors__ = ""
__license__ = "GPL"
__version__ = "0.0.1"
__maintainer__ = "Luis Pacheco"
__email__ = "luigi@luigipacheco.com"
__status__ = "Alpha"


import pygame
from xarm.wrapper import XArmAPI
import time
import numpy as np
import pygame_gui
from entities import Agent, pAgent, Player

arm = XArmAPI("192.168.1.217")
arm.connect()
xarm_position = arm.get_position()
xarm_x = xarm_position[1][0]
xarm_y = xarm_position[1][1]
xarm_z = xarm_position[1][2]
print(xarm_x, xarm_y, xarm_z)
x_max, x_min, y_max, y_min, z_max, z_min = 700, 205, 400, -400, 400, 10
code = arm.set_reduced_tcp_boundary([x_max, x_min, y_max, y_min, z_max, z_min])

successes, failures = pygame.init()
print("Initializing pygame: {0} successes and {1} failures.".format(successes, failures))

screen = pygame.display.set_mode((720, 720))
clock = pygame.time.Clock()
FPS = 60
step = 5
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
def draw_boundary_limits(screen, x_min, x_max, y_min, y_max, color=(0, 255, 0)):
    pygame.draw.line(screen, color, (x_min, y_min), (x_min, y_max), 2)  # Left vertical line
    pygame.draw.line(screen, color, (x_max, y_min), (x_max, y_max), 2)  # Right vertical line
    pygame.draw.line(screen, color, (x_min, y_min), (x_max, y_min), 2)  # Top horizontal line
    pygame.draw.line(screen, color, (x_min, y_max), (x_max, y_max), 2)  # Bottom horizontal line

def handle_slider_events(event):
    if hasattr(event, 'user_type'):
        if event.user_type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
            if event.ui_element == kp_slider:
                agent.kp = event.value
                kp_label.set_text(f"KP: {agent.kp:.2f}")
            elif event.ui_element == kd_slider:
                agent.kd = event.value
                kd_label.set_text(f"KD: {agent.kd:.2f}")
            elif event.ui_element == steering_scalar_slider:
                agent.steering_scalar = event.value
                steering_scalar_label.set_text(f"Steering Scalar: {agent.steering_scalar:.2f}")



player = Player(xarm_x,xarm_y,RED)
agent = Agent(0, initial_pos=np.array([xarm_x, xarm_y, 0]))
pagent =pAgent(WHITE)
manager = pygame_gui.UIManager((720, 480))
kp_slider = pygame_gui.elements.UIHorizontalSlider(
    relative_rect=pygame.Rect((10, 10), (200, 20)),
    start_value=1.5,
    value_range=(0.0, 5.0),
    manager=manager,
)

kd_slider = pygame_gui.elements.UIHorizontalSlider(
    relative_rect=pygame.Rect((10, 40), (200, 20)),
    start_value=2.0,
    value_range=(0.0, 5.0),
    manager=manager,
)

steering_scalar_slider = pygame_gui.elements.UIHorizontalSlider(
    relative_rect=pygame.Rect((10, 70), (200, 20)),
    start_value=0.5,
    value_range=(0.0, 2.0),
    manager=manager,
)

kp_label = pygame_gui.elements.UILabel(
    relative_rect=pygame.Rect((220, 10), (100, 20)),
    text="KP: 1.5",
    manager=manager,
)

kd_label = pygame_gui.elements.UILabel(
    relative_rect=pygame.Rect((220, 40), (100, 20)),
    text="KD: 2.0",
    manager=manager,
)

steering_scalar_label = pygame_gui.elements.UILabel(
    relative_rect=pygame.Rect((220, 70), (150, 20)),
    text="Steering: 0.5",
    manager=manager,
)
joystick = pygame.joystick.Joystick(0)
joystick.init()
running = True
while running:
    dt = clock.tick(FPS) / 1000  # Returns milliseconds between each call to 'tick'. The convert time to seconds.
    screen.fill(BLACK)  # Fill the screen with background color.
    draw_boundary_limits(screen, x_min, x_max, y_min, y_max)
    # Get joystick values
    axis_x = joystick.get_axis(0)
    axis_y = joystick.get_axis(1)
    b = joystick.get_button(0)
    a = joystick.get_button(1)
    reset = joystick.get_button(7)
    hat = joystick.get_hat(0)

#    if b:   #jog on XY plane
#        arm.set_mode(1)
#        arm.set_state(0)
#        print("xy")
#        pos = list(arm.get_position())
#        print(pos)
#        pos[1][0] -= axis_y * step
#        pos[1][1] -= axis_x * step
#       mvpose = [pos[1][0], pos[1][1], pos[1][2], pos[1][3], pos[1][4], pos[1][5]]
#        ret = arm.set_servo_cartesian(mvpose, speed=100, mvacc=2000)
#        time.sleep(0.01)
    if b:   #jog on XY plane
        player.velocity[0] = axis_x * 200 * dt
        player.velocity[1] = axis_y * 200 * dt

    if a: #jog on Roll and Pitch
        arm.set_mode(1)
        arm.set_state(0)
        print("roll pitch")
        pos = list(arm.get_position())
        print(pos)
        pos[1][3] += axis_x * step/10
        pos[1][4] -= axis_y * step/10
        mvpose = [pos[1][0], pos[1][1], pos[1][2], pos[1][3], pos[1][4], pos[1][5]]
        ret = arm.set_servo_cartesian(mvpose, speed=100, mvacc=2000)
    #reset the robot
    if reset:
        print("reset")
        arm.motion_enable(enable=True)
        arm.set_mode(0)
        arm.set_state(state=0)
        arm.reset(wait=True)
        arm.set_position(*[200, 0, 200, 180, 0, 0], wait=True)
        time.sleep(1)
    # move Z
    if hat[1]>0:
        print("up")
        arm.set_mode(1)
        arm.set_state(0)
        pos = list(arm.get_position())
        print(pos)
        pos[1][2] += step*0.5
        mvpose = [pos[1][0], pos[1][1], pos[1][2], pos[1][3], pos[1][4], pos[1][5]]
        ret = arm.set_servo_cartesian(mvpose, speed=100, mvacc=2000)
        time.sleep(0.01)
    if hat[1]<0:
        print("up")
        arm.set_mode(1)
        arm.set_state(0)
        pos = list(arm.get_position())
        print(pos)
        pos[1][2] -= step*0.5
        mvpose = [pos[1][0], pos[1][1], pos[1][2], pos[1][3], pos[1][4], pos[1][5]]
        ret = arm.set_servo_cartesian(mvpose, speed=100, mvacc=2000)
        time.sleep(0.01)

    #jaw
    if hat[0]>0:
        print("jaw+")
        arm.set_mode(1)
        arm.set_state(0)
        pos = list(arm.get_position())
        print(pos)
        pos[1][5] += step*0.1
        mvpose = [pos[1][0], pos[1][1], pos[1][2], pos[1][3], pos[1][4], pos[1][5]]
        ret = arm.set_servo_cartesian(mvpose, speed=100, mvacc=2000)
        time.sleep(0.01)
    if hat[0]<0:
        print("jaw-")
        arm.set_mode(1)
        arm.set_state(0)
        pos = list(arm.get_position())
        print(pos)
        pos[1][5] -= step*0.1
        mvpose = [pos[1][0], pos[1][1], pos[1][2], pos[1][3], pos[1][4], pos[1][5]]
        ret = arm.set_servo_cartesian(mvpose, speed=100, mvacc=2000)
        time.sleep(0.01)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                player.velocity[1] = -200 * dt  # 200 pixels per second
            elif event.key == pygame.K_s:
                player.velocity[1] = 200 * dt
            elif event.key == pygame.K_a:
                player.velocity[0] = -200 * dt
            elif event.key == pygame.K_d:
                player.velocity[0] = 200 * dt
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_w or event.key == pygame.K_s:
                player.velocity[1] = 0
            elif event.key == pygame.K_a or event.key == pygame.K_d:
                player.velocity[0] = 0
        handle_slider_events(event)
        manager.process_events(event)

    player.update()
    player_center_x = player.x + player.rect.width/2  - pagent.rect.width/2
    player_center_y = player.y + player.rect.height/2  - pagent.rect.height/2

    agent.update(np.array([player_center_x, player_center_y, 0]))
    pagent.update(agent)

    pagent_x, pagent_y = agent.get_position()[:2]
    arm.set_mode(1)
    arm.set_state(0)
    arm.set_servo_cartesian([max(float(x_min),float(pagent_x)), pagent_y, xarm_z, 180, 0, 0], speed=5, mvacc=2000)
    agent.kp = kp_slider.get_current_value()
    agent.kd = kd_slider.get_current_value()
    agent.steering_scalar = steering_scalar_slider.get_current_value()

    kp_label.set_text(f"KP: {agent.kp:.2f}")
    kd_label.set_text(f"KD: {agent.kd:.2f}")
    steering_scalar_label.set_text(f"Steering: {agent.steering_scalar:.2f}")

    manager.update(dt)
    manager.draw_ui(screen)

    screen.blit(player.image, player.rect)
    screen.blit(pagent.image, pagent.rect)
    pygame.display.update()  # Or pygame.display.flip()

print("Exited the game loop. Game will quit...")
quit()  # Not actually necessary since the script will exit anyway.# Write your code here :-)
