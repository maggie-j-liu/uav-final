#!/usr/bin/python3

from djitellopy import Tello
import cv2 as cv
import time
from led_detection import detect_leds
from process_image import process_image
from optical_flow import TelloOpticalFlow
from light_tracking_pid import track_light
from track_led import LedTracker

# tello_optical_flow = TelloOpticalFlow()
# tello = tello_optical_flow.tello

tello = Tello()
tello.connect()

battery = tello.get_battery()
print(f"battery: {battery}")

tello.streamon()
tello.send_rc_control(0, 0, 0, 0)
tello.takeoff()
frame_read = tello.get_frame_read()

led_tracker = LedTracker()
stopped = True

while True:
    img = frame_read.frame
    leds = detect_leds(img)

    if len(leds):
        # TODO: filter here to find correct LED
        led = leds[0]
        rc_control = led_tracker.update(*led, img)
        if rc_control is not None:
            tello.send_rc_control(*rc_control)
            stopped = False
    elif not stopped:
        tello.send_rc_control(0, 0, 0, 0)
        stopped = True
    # Optical flow
    # output = tello_optical_flow.sparse_optical_flow_lk()

    # PID control
    # if output:
    #     px_movements, radii = output
    #     track_light(px_movements, radii, tello)
    # else:
    #     tello.send_rc_control(0, 0, 0, 0)

    # WaitKey
    key = cv.waitKey(1) & 0xFF
    if key == ord("q"):
        break
    time.sleep(1 / 5)

tello.streamoff()
tello.land()
