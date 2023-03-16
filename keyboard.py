#!/usr/bin/env python3
__author__ = "Luis Pacheco"
__copyright__ = "Copyright 2023, Luis Pacheco"
__contributors__ = ""
__license__ = "GPL"
__version__ = "0.0.1"
__maintainer__ = "Luis Pacheco"
__email__ = "luigi@luigipacheco.com"
__status__ = "Alpha"

"""
Description: Keyboard/ Joystick Jog for xarm
"""

import os
import sys
import time

sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))
from pynput.keyboard import Key, Listener
from xarm.wrapper import XArmAPI

if len(sys.argv) >= 2:
    ip = sys.argv[1]
else:
    try:
        from configparser import ConfigParser
        parser = ConfigParser()
        parser.read('../robot.conf')
        ip = parser.get('xArm', 'ip')
    except:
        ip = input('Please input the xArm ip address:')
        if not ip:
            print('input error, exit')
            sys.exit(1)
########################################################


arm = XArmAPI(ip)
arm.motion_enable(enable=True)
arm.set_mode(0)
arm.set_state(state=0)

arm.reset(wait=True)

arm.set_position(*[200, 0, 200, 180, 0, 0], wait=True)

arm.set_mode(1)
arm.set_state(0)
time.sleep(0.1)

step = 5
astep = 1
speed = 200
aspeed = 100

def show(key):
    currentPos = arm.get_position()
    x=currentPos[1][0]
    y=currentPos[1][1]
    a=currentPos[1][3]
    b=currentPos[1][4]
    print(currentPos)
    if key == Key.up:
        x=x+step
        print("up")
        print(x)
        mvpose = [x, y, 200, a, b, 0]
        ret = arm.set_servo_cartesian(mvpose, speed=speed, mvacc=2000)
        #print('set_servo_cartesian, ret={}'.format(ret))
        time.sleep(0.01)
    if key == Key.down:
        x=x-step
        print("up")
        print(x)
        mvpose = [x, y, 200, a, b, 0]
        ret = arm.set_servo_cartesian(mvpose, speed=speed, mvacc=2000)
        #print('set_servo_cartesian, ret={}'.format(ret))
        time.sleep(0.01)
    if key == Key.left:
        y=y+step
        print("left")
        print(y)
        mvpose = [x, y, 200, a, b, 0]
        ret = arm.set_servo_cartesian(mvpose, speed=speed, mvacc=2000)
        #print('set_servo_cartesian, ret={}'.format(ret))
        time.sleep(0.01)
    if key == Key.right:
        y=y-step
        print("right")
        print(y)
        mvpose = [x, y, 200, a, b, 0]
        ret = arm.set_servo_cartesian(mvpose, speed=speed, mvacc=2000)
        #print('set_servo_cartesian, ret={}'.format(ret))
        time.sleep(0.01)
    try:
        if key.char == "w":
            a=a-astep
            print("roll-")

            mvpose = [x, y, 200, a, b, 0]
            ret = arm.set_servo_cartesian(mvpose, speed=aspeed, mvacc=2000)
            #print('set_servo_cartesian, ret={}'.format(ret))
            time.sleep(0.01)
    except AttributeError:
        print('special key {0} pressed'.format(key))
    try:
        if key.char == "s":
            a=a+astep
            print("roll+")
            mvpose = [x, y, 200, a, b, 0]
            ret = arm.set_servo_cartesian(mvpose, speed=aspeed, mvacc=2000)
            #print('set_servo_cartesian, ret={}'.format(ret))
            time.sleep(0.01)
    except AttributeError:
        print('special key {0} pressed'.format(key))

    try:
        if key.char == "a":
            b=b-astep
            print("roll-")

            mvpose = [x, y, 200, a, b, 0]
            ret = arm.set_servo_cartesian(mvpose, speed=aspeed, mvacc=2000)
            #print('set_servo_cartesian, ret={}'.format(ret))
            time.sleep(0.01)
    except AttributeError:
        print('special key {0} pressed'.format(key))
    try:
        if key.char == "d":
            b=b+astep
            print("roll+")
            mvpose = [x, y, 200, a, b, 0]
            ret = arm.set_servo_cartesian(mvpose, speed=aspeed, mvacc=2000)
            #print('set_servo_cartesian, ret={}'.format(ret))
            time.sleep(0.01)
    except AttributeError:
        print('special key {0} pressed'.format(key))


    # by pressing 'delete' button
    # you can terminate the loop
    if key == Key.delete:
        return False

# Collect all event until released
with Listener(on_press = show) as listener:
    listener.join()

arm.disconnect()# Write your code here :-)
