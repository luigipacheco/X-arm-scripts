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

screen = pygame.display.set_mode((900, 900))
pygame_w, pygame_h = pygame.display.get_surface().get_size()
clock = pygame.time.Clock()
FPS = 60
step = 5
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)

def nmap(x,in_min,in_max,out_min,out_max):
    out_x = (x-in_min) * (out_max - out_min) / (in_max - in_min) + out_min
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



player = Player(RED,xarm_x,xarm_y)
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
    draw_boundary_limits(screen, x_min, x_max, y_min, y_max)

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

        # estimate pose of each marker and return the values
        # rvet and tvec-different from camera coefficients
        rvec, tvec ,_ = aruco.estimatePoseSingleMarkers(corners, 0.05, mtx, dist)
        #(rvec-tvec).any() # get rid of that nasty numpy value array error

        for i in range(0, ids.size):
            # draw axis for the aruco markers
            cv2.drawFrameAxes(frame, mtx, dist, rvec[i], tvec[i], 0.05)
        # draw a square around the markers
        aruco.drawDetectedMarkers(frame, corners)

        avgx = int((corners[0][0][0][0]+corners[0][0][1][0]+corners[0][0][2][0]+corners[0][0][3][0])/4)  #use central cordinates from aruco
        avgy = int((corners[0][0][0][1] + corners[0][0][1][1] + corners[0][0][2][1] + corners[0][0][3][1]) / 4) #use central cordinates from aruco

        normalizedxy = screen_to_normal(avgx,avgy,ocv_w,ocv_h)
        player.x = nmap(normalizedxy[0],0.05,.95,pygame_w,0)
        player.y = nmap(normalizedxy[1],0.05,.95,0,pygame_h)
        print(player.x, player.y)
        
        #print(avgx,",",avgy)
        #print(tvec[0][0][0]*1000,",",tvec[0][0][1]*1000,",",tvec[0][0][2]*1000)
        #print(math.degrees(rvec[0][0][0]),",",math.degrees(rvec[0][0][1]),",",math.degrees(rvec[0][0][2]))
        # code to show ids of the marker found
        #cv2.putText(frame, "pos: " + str(rvec[0][0][0])+str(rvec[0][0][1])+str(rvec[0][0][2]), (avgx,avgy), font, 1, (0,255,0),2,cv2.LINE_AA)
        strg = ''
        for i in range(0, ids.size):
            strg += str(ids[i][0])+', '

        cv2.putText(frame, "Id: " + strg, (0,64), font, 1, (0,255,0),2,cv2.LINE_AA)


    else:
        # code to show 'No Ids' when no markers are found
        cv2.putText(frame, "No Ids", (0,64), font, 1, (0,255,0),2,cv2.LINE_AA)
        player.x = pygame_w/2
        player.y = pygame_h/2
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

    player.update()
    player_center_x = player.x + player.rect.width/2  - pagent.rect.width/2
    player_center_y = player.y + player.rect.height/2  - pagent.rect.height/2

    agent.update(np.array([player_center_x, player_center_y, 0]))
    pagent.update(agent)

    pagent_x, pagent_y = agent.get_position()[:2]
    arm.set_mode(1)
    arm.set_state(0)
    #arm.set_servo_cartesian([max(float(x_min),float(pagent_x)), pagent_y, xarm_z, 180, 0, 0], speed=5, mvacc=2000)
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

