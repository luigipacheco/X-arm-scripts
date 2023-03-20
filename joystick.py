__author__ = "Luis Pacheco"
__copyright__ = "Copyright 2023, Luis Pacheco"
__contributors__ = ""
__license__ = "GPL"
__version__ = "0.0.1"
__maintainer__ = "Luis Pacheco"
__email__ = "luigi@luigipacheco.com"
__status__ = "Alpha"
"""
Pygame Joystick control for U-factory  X-arm
"""
import pygame
from xarm.wrapper import XArmAPI
import time

pygame.init()
pygame.joystick.init()

# Initialize xArm
arm = XArmAPI("192.168.1.217")
arm.connect()

# Get the first joystick
joystick = pygame.joystick.Joystick(0)
joystick.init()

step = 5

while True:
    pygame.event.get()

    # Get joystick values
    axis_x = joystick.get_axis(0)
    axis_y = joystick.get_axis(1)
    button_1 = joystick.get_button(0)
    button_2 = joystick.get_button(1)
    button_3 = joystick.get_button(2)

    # Jog the xArm
    if button_1:   #jog on XY plane
        arm.set_mode(1)
        arm.set_state(0)
        print("xy")
        pos = list(arm.get_position())
        print(pos)
        pos[1][0] -= axis_y * step  # Convert joystick position to xArm position (assuming 1:10 scale)
        pos[1][1] -= axis_x * step  # Convert joystick position to xArm position (assuming 1:10 scale)
        mvpose = [pos[1][0], pos[1][1], pos[1][2], pos[1][3], pos[1][4], pos[1][5]]
        ret = arm.set_servo_cartesian(mvpose, speed=100, mvacc=2000)
        time.sleep(0.01)

    if button_2: #jog on Roll and Pitch
        arm.set_mode(1)
        arm.set_state(0)
        print("roll pitch")
        pos = list(arm.get_position())
        print(pos)
        pos[1][3] += axis_x * step/10  # Convert joystick position to xArm position (assuming 1:10 scale)
        pos[1][4] -= axis_y * step/10  # Convert joystick position to xArm position (assuming 1:10 scale)
        mvpose = [pos[1][0], pos[1][1], pos[1][2], pos[1][3], pos[1][4], pos[1][5]]
        ret = arm.set_servo_cartesian(mvpose, speed=100, mvacc=2000)
    if button_3:
        print("reset")
        arm.motion_enable(enable=True)
        arm.set_mode(0)
        arm.set_state(state=0)
        arm.reset(wait=True)
        arm.set_position(*[200, 0, 200, 180, 0, 0], wait=True)
        time.sleep(1)
    # Wait for a short period before checking again
    pygame.time.wait(10)# Write your code here :-)
