#!/usr/bin/env python3

import time
import cv2
import math
from djitellopy import Tello


CAMERA_DIMENSIONS = (960, 720)
CAMERA_CENTER_X = CAMERA_DIMENSIONS[0]/2
CAMERA_CENTER_Y = CAMERA_DIMENSIONS[1]/2
CAMERA_FOCAL = 35
MARKER_PHYSICAL_LENGTH = 123      #in millimeters
SPEED = 10
FOLLOW_DISTANCE = 30


class Marker():
    def __init__(self, marker_id, corners):
        self.marker_id = marker_id
        self.left_up = corners[0]
        self.right_up = corners[1]
        self.right_down = corners[2]
        self.left_down = corners[3]

        self.centriod = self.centriod()
        self.size = self.size()
        self.tello_dist, self.tello_angle = self.tello_pose()

    def centriod(self):
        return ((self.left_up[0] + self.right_up[0] + self.right_down[0] + self.left_down[0]) / 4,
                (self.left_up[1] + self.right_up[1] + self.right_down[1] + self.left_down[1]) / 4)

    def size(self):
        return (abs(self.right_up[0] - self.left_up[0]) + abs(self.right_down[0] - self.left_down[0]) +
                abs(self.left_up[1] - self.left_down[1]) + abs(self.right_up[1] - self.right_down[1])) / 4

    def tello_pose(self):
        dist = int((MARKER_PHYSICAL_LENGTH * CAMERA_FOCAL)/(10 * self.size))

        factor = MARKER_PHYSICAL_LENGTH/(10 * self.size)
        len_x = (self.centriod[0] - CAMERA_CENTER_X) * factor / dist
        len_y = (CAMERA_CENTER_Y - self.centriod[1]) * factor/dist
        if len_x > len_y:
            len_y = len_y/len_x
            len_x = 1
        else:
            len_x = len_x/len_y
            len_y = 1
        
        angle = (round(math.asin(len_x) * 180/math.pi, 2), round(math.asin(len_y) * 180/math.pi, 2))

        return dist, angle

    def tello_follow(self):
        left_right_velocity = 0
        forward_backward_velocity = 0
        up_down_velocity = 0

        if CAMERA_CENTER_X - self.centriod[0] >= SPEED:
            left_right_velocity = SPEED
        elif CAMERA_CENTER_X - self.centriod[0] <= -SPEED:
            left_right_velocity = -SPEED

        if self.tello_dist >= FOLLOW_DISTANCE + SPEED:
            forward_backward_velocity = SPEED
        elif self.tello_dist <= FOLLOW_DISTANCE - SPEED:
            forward_backward_velocity = -SPEED

        if CAMERA_CENTER_Y - self.centriod[1] >= SPEED:
            up_down_velocity = SPEED
        elif CAMERA_CENTER_Y - self.centriod[1] <= -SPEED:
            up_down_velocity = -SPEED

        tello.send_rc_control(left_right_velocity, forward_backward_velocity, up_down_velocity, int(self.tello_angle[0]))

    def print_info(self):
        print("MARKER INFO:")
        print('ID:', self.marker_id)
        print('Corners: ', self.left_up, ', ', self.right_up, ", ", self.right_down, ", ", self.left_down, sep="")
        print('Centroid: ', self.centriod, ', ', "Pixel length: ", self.size, sep="")
        print('TELLO INFO:')
        print("Distance: ", self.tello_dist, "cm, Angle: ", self.tello_angle, '\n', sep="")


def detect_markers(image):
    arucoDict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_ARUCO_ORIGINAL)
    corners, marker_id, rejects = cv2.aruco.detectMarkers(cv2.cvtColor(image, cv2.COLOR_BGR2GRAY), arucoDict)

    if marker_id is not None:
        marker = Marker(marker_id[0][0], corners[0][0])
        marker.print_info()
        marker.tello_follow()


if __name__ == "__main__":
    tello = Tello()
    tello.connect()
    tello.takeoff()
    tello.streamon()
    frame_read = tello.get_frame_read()

    while True:
        image = frame_read.frame
        cv2.imshow("image", image)
        detect_markers(image)
        time.sleep(0.001)