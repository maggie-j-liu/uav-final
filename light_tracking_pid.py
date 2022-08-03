#!/usr/bin/python3

import time
import math
from djitellopy import Tello


def track_light(PX_MOVEMENTS, tello):
    KP = 1.2
    KI = 1.35
    KD = 0.0001
    L = 3
    PX_TO_MM_FACTOR = 0.0264583     # may be inaccurate

    def tello_pid(error, last_time, last_error, ITerm):
        curr_time = time.time()
        dt = curr_time - last_time

        u = 0
        if dt >= 0.1:
            PTerm = error
            ITerm += error * dt
            DTerm = (error - last_error) / dt

            u = (KP * PTerm) + (KI * ITerm) + (KD * DTerm)
            u = int(min(max(u, -100), 100))

            last_time = curr_time
            last_error = error

        return u, last_time, last_error, ITerm

    last_time_lr = time.time()
    last_time_fb = time.time()
    last_time_ud = time.time()
    last_error_lr = 0
    last_error_fb = 0
    last_error_ud = 0
    ITerm_lr = 0
    ITerm_fb = 0
    ITerm_ud = 0
    u_lr = 0
    u_fb = 0
    u_ud = 0

    for i in range(L):
        # while not math.isclose(tello.get_speed_x(), 0) and not math.isclose(tello.get_speed_y(), 0) and not math.isclose(tello.get_speed_z(), 0):
        #     time.sleep(0.2)

        u_lr, last_time_lr, last_error_lr, ITerm_lr = tello_pid(
            PX_MOVEMENTS[0]*PX_TO_MM_FACTOR - u_lr, last_time_lr, last_error_lr, ITerm_lr)
        # u_fb, last_time_fb, last_error_fb, ITerm_fb = tello_pid(
        #     PX_MOVEMENTS[1]*PX_TO_MM_FACTOR - u_fb, last_time_fb, last_error_fb, ITerm_fb)
        # u_ud, last_time_ud, last_error_ud, ITerm_ud = tello_pid(
        #     PX_MOVEMENTS[2]*PX_TO_MM_FACTOR - u_ud, last_time_ud, last_error_ud, ITerm_ud)
        print("rc_control", u_lr, 0, 0, 0)
        # tello.send_rc_control(u_lr, u_fb, u_ud, 0)
