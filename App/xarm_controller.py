from xarm.wrapper import XArmAPI
import time

class XArmController:
    def __init__(self, ip):
        self.arm = XArmAPI(ip)
        self.arm.connect()
        self.arm.motion_enable(enable=True)
        self.arm.set_mode(0)
        self.arm.set_state(0)

    def jog_xy_plane(self, axis_x, axis_y, step):
        current_pose = self.arm.get_position()
        new_pose = [current_pose[0] + axis_x * step, current_pose[1] + axis_y * step, current_pose[2]]
        self.arm.set_position(*new_pose, speed=100, wait=True)

    def jog_roll_pitch(self, axis_x, axis_y, step):
        current_angles = self.arm.get_servo_angle()
        new_angles = [current_angles[0], current_angles[1] + axis_x * step, current_angles[2] + axis_y * step, current_angles[3], current_angles[4], current_angles[5]]
        self.arm.set_servo_angle(angle=new_angles, speed=50, wait=True)

    def reset_robot(self):
        self.arm.reset(wait=True)
