#!/usr/bin/python3

from djitellopy import Tello
import cv2 as cv
import time
from process_image import process_image
from optical_flow_merged import TelloOpticalFlow
from light_tracking_pid import track_light

tello = Tello()
tello.connect()
tello.streamon()
frame_read = tello.get_frame_read()

battery = tello.get_battery()
print(f"battery: {battery}")

while True:
    # LED detection
    img = frame_read.frame
    img = process_image(img)
    cv.imshow("camera", img)
    led_mask = None # ADD LED DETECTION RESULT

    # Optical flow
    tello_optical_flow = TelloOpticalFlow()
    tello_optical_flow.get_frame()
    px_movements = tello_optical_flow.sparse_optical_flow_lk(led_mask)

    #PID control 
    for m in len(px_movements):
        track_light(px_movements[m])

    # WaitKey 
    key = cv.waitKey(1) & 0xFF
    if key == ord("q"):
        break
    time.sleep(1 / 5)

tello.streamoff()
tello.land()