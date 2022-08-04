#!/usr/bin/python3

import time
from djitellopy import Tello
from led_detection import detect_leds


def track_light(PX_MOVEMENTS, RADII, tello):
    KP = 1.2
    KI = 1.35
    KD = 0.0001
    L = 3
    PX_TO_MM_FACTOR = 0.0264583     # may be inaccurate, needs tuning/recalculation
    LED_DIAMETER = 3.0  #in centimeters
    CAMERA_FOCAL = 35

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

        error_lr = PX_MOVEMENTS[0]/PX_TO_MM_FACTOR - u_lr
        u_lr, last_time_lr, last_error_lr, ITerm_lr = tello_pid(
            error_lr, last_time_lr, last_error_lr, ITerm_lr)
        
        error_fb = (LED_DIAMETER/RADII[1] * CAMERA_FOCAL) - (
            LED_DIAMETER/RADII[0] * CAMERA_FOCAL) - u_fb
        u_fb, last_time_fb, last_error_fb, ITerm_fb = tello_pid(
            error_fb, last_time_fb, last_error_fb, ITerm_fb)

        error_ud = PX_MOVEMENTS[1]/PX_TO_MM_FACTOR - u_ud
        u_ud, last_time_ud, last_error_ud, ITerm_ud = tello_pid(
            error_ud, last_time_ud, last_error_ud, ITerm_ud)
        
        print("rc_control", u_lr, u_fb, u_ud, 0)
        tello.send_rc_control(u_lr, u_fb, u_ud, 0)


if __name__ == "__main__":
    tello = Tello()
    PX_MOVEMENTS = None
    track_light(PX_MOVEMENTS, tello)