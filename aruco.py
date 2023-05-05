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
Description: Aruco movement for xarm
"""

import time
import numpy as np
import cv2
import cv2.aruco as aruco
import glob
import math
import pygame
from xarm.wrapper import XArmAPI
import pygame_gui
from classes import Agent
from classes import pAgent
from classes import Player
from oneefilter import OneEuroFilter
from oneefilter import LowPassFilter



arm = XArmAPI("192.168.1.217")
arm.connect()
xarm_position = arm.get_position()
xarm_x = xarm_position[1][0]
xarm_y = xarm_position[1][1]
xarm_z = xarm_position[1][2]
xarm_a = xarm_position[1][3]
xarm_b = xarm_position[1][4]
xarm_c = xarm_position[1][5]
print(xarm_x, xarm_y, xarm_z)
x_max, x_min, y_max, y_min, z_max, z_min = 600, 205, 300, -300, 600, 100
code = arm.set_reduced_tcp_boundary([x_max, x_min, y_max, y_min, z_max, z_min])

#initialize the variables that will eventually be sent to the robot
robot_x =xarm_x
robot_y =xarm_y
robot_z =xarm_z
robot_rx=xarm_a
robot_ry=xarm_b
robot_rz=xarm_c
aruco_rx = 0
aruco_ry = 0
aruco_rz = 0
filtered_rx = xarm_a
filtered_ry = xarm_b
filtered_rz = xarm_c

successes, failures = pygame.init()
print("Initializing pygame: {0} successes and {1} failures.".format(successes, failures))

screen = pygame.display.set_mode((800, 800))
pygame_w, pygame_h = pygame.display.get_surface().get_size()
clock = pygame.time.Clock()
FPS = 60
step = 5
BLACK = (0, 0, 0)
GRAY = (150, 150, 150)
WHITE = (255, 255, 255)
RED = (255, 0, 0)

config = {
        'freq': 120,       # Hz
        'mincutoff': .2,  # FIXME
        'beta': 0.01,       # FIXME
        'dcutoff': 1.0     # this one should be ok
        }
configz = {
        'freq': 120,       # Hz
        'mincutoff': .1,  # FIXME
        'beta': 0.005,       # FIXME
        'dcutoff': 1.0     # this one should be ok
        }
filter_rx=OneEuroFilter(**config)
filter_ry=OneEuroFilter(**config)
filter_rz=OneEuroFilter(**configz)

def nmap(x,in_min,in_max,out_min,out_max, clamp=False):
    out_x = (x-in_min) * (out_max - out_min) / (in_max - in_min) + out_min
    if clamp:
        if out_x > out_max:
            out_x = out_max
        elif out_x < out_min:
            out_x = out_min
    return(out_x)
def screen_to_normal(x,y, width, height):
    # w, h = pygame.display.get_surface().get_size()
    n_x = x/ (width*1.0)
    n_y = y/ (height*1.0)
    return(n_x,n_y)



def draw_boundary_limits(screen, x_min, x_max, y_min, y_max, color=(0, 255, 0)):
    pygame.draw.line(screen, color, (x_min, y_min+pygame_w/2), (x_min, y_max+pygame_w/2), 2)  # Left vertical line
    pygame.draw.line(screen, color, (x_max, y_min+pygame_w/2), (x_max, y_max+pygame_w/2), 2)  # Right vertical line
    pygame.draw.line(screen, color, (x_min, y_min+pygame_h/2), (x_max, y_min+pygame_h/2), 2)  # Top horizontal line
    pygame.draw.line(screen, color, (x_min, y_max+pygame_h/2), (x_max, y_max+pygame_h/2), 2)  # Bottom horizontal line




p_inix = nmap(xarm_x,x_min,x_max,0,pygame_w)
p_iniy = nmap(xarm_y,y_min,y_max,0,pygame_h)
player = Player(GRAY,p_inix,p_iniy)
# player.x = p_inix
# player.y = p_iniy
agent = Agent(0, initial_pos=np.array([p_inix, p_iniy, xarm_z]))
pagent =pAgent(WHITE)
manager = pygame_gui.UIManager((720, 480))

play_on = False
use_pos = False
use_rot = False

toggle_play = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect((10, 100), (150, 30)),
    text="Play: OFF",
    manager=manager,
)

toggle_pos = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect((10, 140), (150, 30)),
    text=" Pos: OFF",
    manager=manager,
)

toggle_rot = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect((10, 180), (150, 30)),
    text=" Rot: OFF",
    manager=manager,
)
def handle_slider_events(event):
    global play_on, use_pos, use_rot
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
        elif event.user_type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == toggle_play:
                play_on = not play_on
                toggle_play.set_text(f" Play: {'ON' if play_on else 'OFF'}")
            elif event.ui_element == toggle_pos:
                use_pos = not use_pos
                toggle_pos.set_text(f" Pos: {'ON' if use_pos else 'OFF'}")
            elif event.ui_element == toggle_rot:
                use_rot = not use_rot
                toggle_rot.set_text(f" Rot: {'ON' if use_rot else 'OFF'}")
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
    value_range=(0.0, 5.0),
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

cap = cv2.VideoCapture(0)
ocv_w= cap.get(3)  # float `width`
ocv_h = cap.get(4)  # float `height`

####---------------------- CALIBRATION ---------------------------
# termination criteria for the iterative algorithm
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

# prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
# checkerboard of size (7 x 6) is used
objp = np.zeros((6*7,3), np.float32)
objp[:,:2] = np.mgrid[0:7,0:6].T.reshape(-1,2)

# arrays to store object points and image points from all the images.
objpoints = [] # 3d point in real world space
imgpoints = [] # 2d points in image plane.

# iterating through all calibration images
# in the folder
images = glob.glob('calib_images/checkerboard/*.jpg')

for fname in images:
    img = cv2.imread(fname)
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

    # find the chess board (calibration pattern) corners
    ret, corners = cv2.findChessboardCorners(gray, (7,6),None)

    # if calibration pattern is found, add object points,
    # image points (after refining them)
    if ret == True:
        objpoints.append(objp)

        # Refine the corners of the detected corners
        corners2 = cv2.cornerSubPix(gray,corners,(11,11),(-1,-1),criteria)
        imgpoints.append(corners2)

        # Draw and display the corners
        img = cv2.drawChessboardCorners(img, (7,6), corners2,ret)


ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1],None,None)

###------------------ ARUCO TRACKER ---------------------------
while (True):
    dt = clock.tick(FPS) / 1000  # Returns milliseconds between each call to 'tick'. The convert time to seconds.
    screen.fill(BLACK)  # Fill the screen with background color.

    ret, frame = cap.read()
    #if ret returns false, there is likely a problem with the webcam/camera.
    #In that case uncomment the below line, which will replace the empty frame 
    #with a test image used in the opencv docs for aruco at https://www.docs.opencv.org/4.5.3/singlemarkersoriginal.jpg
    # frame = cv2.imread('./images/test image.jpg') 

    # operations on the frame
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # set dictionary size depending on the aruco marker selected
    aruco_dict = aruco.Dictionary_get(aruco.DICT_6X6_250)

    # detector parameters can be set here (List of detection parameters[3])
    parameters = aruco.DetectorParameters_create()
    parameters.adaptiveThreshConstant = 10

    # lists of ids and the corners belonging to each id
    corners, ids, rejectedImgPoints = aruco.detectMarkers(gray, aruco_dict, parameters=parameters)

    # font for displaying text (below)
    font = cv2.FONT_HERSHEY_SIMPLEX

    # check if the ids list is not empty
    # if no check is added the code will crash
    if np.all(ids != None):
        player.color=RED 
        # estimate pose of each marker and return the values
        # rvet and tvec-different from camera coefficients
        rvec, tvec ,_ = aruco.estimatePoseSingleMarkers(corners, 0.05, mtx, dist)
        #(rvec-tvec).any() # get rid of that nasty numpy value array error

        for i in range(0, ids.size):
            # draw axis for the aruco markers
            cv2.drawFrameAxes(frame, mtx, dist, rvec[i], tvec[i], 0.05)
        # draw a square around the markers
        aruco.drawDetectedMarkers(frame, corners)

        aruco_x = int((corners[0][0][0][0]+corners[0][0][1][0]+corners[0][0][2][0]+corners[0][0][3][0])/4)  #use central cordinates from aruco
        aruco_y = int((corners[0][0][0][1] + corners[0][0][1][1] + corners[0][0][2][1] + corners[0][0][3][1]) / 4) #use central cordinates from aruco
        aruco_z = tvec[0][0][2]
        #print(aruco_z)

        normalizedxy = screen_to_normal(aruco_x,aruco_y,ocv_w,ocv_h)
        player_z= nmap(aruco_z,0,0.5,z_min,z_max)
        player.x = nmap(normalizedxy[1],0.05,.95,pygame_w,0)
        player.y = nmap(normalizedxy[0],0.05,.95,0,pygame_h)
        # print(player.x, player.y)
        
        #print(aruco_x,",",aruco_y)
        #print(tvec[0][0][0]*1000,",",tvec[0][0][1]*1000,",",tvec[0][0][2]*1000)
        if use_rot:
            aruco_rx = math.degrees(rvec[0][0][0])
            if aruco_rx < 0 :
                aruco_rx = (180+aruco_rx)*-1
            else:
                aruco_rx = 180-aruco_rx         
            aruco_ry = math.degrees(rvec[0][0][1])
            aruco_rz = math.degrees(rvec[0][0][2])
            ts = time.time()
            if aruco_rx > 0 : 
                aruco_rz = aruco_rz*-1

            filtered_rx = filter_rx(aruco_rx,ts)
            filtered_ry = filter_ry(aruco_ry,ts)
            filtered_rz = filter_rz(aruco_rz,ts)

            robot_rx = nmap(filtered_rz,180,-180,0,360,True)
            robot_ry = -filtered_rx
            #robot_rz = filtered_ry

            #filtered_rx = F(robot_ry)
            #filtered_rx = F(robot_rz)
            #print(aruco_rx , filtered_rx)

            screen_msg = f"marker rot: [{round(robot_rx)},{round(robot_ry)},{round(robot_rz)}]"
            cv2.putText(frame, screen_msg, (0,94), font, 1, (255,0,0),2,cv2.LINE_AA)
            # if robot_ry < -1:
            #     robot_ry = nmap(robot_ry,-180,0,335,359,True)
            # else:
            #     robot_ry = nmap(robot_ry,0,180,0,45,True)
            # cv2.putText(frame, "rx: " + str(round(robot_rx)), (0,134), font, 1, (255,255,255),2,cv2.LINE_AA)
        #print(math.degrees(rvec[0][0][1]))
        #print(math.degrees(rvec[0][0][2]))
        # code to show ids of the marker found
        #cv2.putText(frame, "pos: " + str(rvec[0][0][0])+str(rvec[0][0][1])+str(rvec[0][0][2]), (aruco_x,aruco_y), font, 1, (0,255,0),2,cv2.LINE_AA)
        strg = ''
        for i in range(0, ids.size):
            strg += str(ids[i][0])+', '

        cv2.putText(frame, "Id: " + strg, (0,64), font, 1, (0,255,0),2,cv2.LINE_AA)


    else:
        # code to show 'No Ids' when no markers are found
        player.color = GRAY
        cv2.putText(frame, "No Ids", (0,64), font, 1, (0,255,0),2,cv2.LINE_AA)
        #player.x = pygame_w/2
        #player.y = pygame_h/2
   #print(player.color)
    for event in pygame.event.get():
    #     if event.type == pygame.QUIT:
    #         running = False
    #     elif event.type == pygame.KEYDOWN:
    #         if event.key == pygame.K_w:
    #             player.velocity[1] = -200 * dt  # 200 pixels per second
    #         elif event.key == pygame.K_s:
    #             player.velocity[1] = 200 * dt
    #         elif event.key == pygame.K_a:
    #             player.velocity[0] = -200 * dt
    #         elif event.key == pygame.K_d:
    #             player.velocity[0] = 200 * dt
    #     elif event.type == pygame.KEYUP:
    #         if event.key == pygame.K_w or event.key == pygame.K_s:
    #             player.velocity[1] = 0
    #         elif event.key == pygame.K_a or event.key == pygame.K_d:
    #             player.velocity[0] = 0
        handle_slider_events(event)
        manager.process_events(event)

    # display the resulting frame
    if play_on:
        screen.fill((0,0,255))
        player.update()
        player_center_x = player.x + player.rect.width/2  - pagent.rect.width/2
        player_center_y = player.y + player.rect.height/2  - pagent.rect.height/2
        if use_pos:
            agent.update(np.array([player_center_x, player_center_y, player_z]))
            pagent.update(agent)
            pagent_x, pagent_y,robot_z = agent.get_position()[:3]
            robot_x = nmap(pagent_x,0,pygame_w,x_min,x_max,clamp=True)
            robot_y = nmap(pagent_y,0,pygame_h,y_min,y_max,clamp=True)
            robot_z = nmap(robot_z,z_min,z_max,z_min,z_max,clamp=True)
            cv2.putText(frame, str(robot_z), (0,240), font, 1, (255,255,255),2,cv2.LINE_AA)

        arm.set_mode(1)
        arm.set_state(0)
        arm.set_servo_cartesian([robot_x, robot_y, robot_z, robot_rx , robot_ry, robot_rz], speed=5, mvacc=2000)
        #arm.set_servo_cartesian([max(float(x_min),float(pagent_x)), pagent_y, xarm_z, 180, 0, 0], speed=5, mvacc=2000)
        # print(robot_x,robot_y)
        #arm.set_servo_cartesian([max(float(x_min),float(pagent_x)), pagent_y, xarm_z, 180, 0, 0], speed=5, mvacc=2000)
    draw_boundary_limits(screen, x_min, x_max, y_min, y_max)
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

    cv2.imshow('frame',frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
quit()  # Not actually necessary since the script will exit anyway.# Write your code here :-)

