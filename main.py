#!/usr/bin/python3

from djitellopy import Tello
import cv2 as cv
import time
from process_image import process_image
from optical_flow import TelloOpticalFlow
from light_tracking_pid import track_light

tello_optical_flow = TelloOpticalFlow()
tello = tello_optical_flow.tello
battery = tello.get_battery()
print(f"battery: {battery}")

while True:
    # Optical flow
    output = tello_optical_flow.sparse_optical_flow_lk()

    # PID control
    if output:
        px_movements, radii = output
        track_light(px_movements, radii, tello)

    # WaitKey
    key = cv.waitKey(1) & 0xFF
    if key == ord("q"):
        break
    time.sleep(1 / 3)

tello.streamoff()
# tello.land()
