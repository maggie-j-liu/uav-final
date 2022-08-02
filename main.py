#!/usr/bin/python3

from djitellopy import Tello
import cv2 as cv
import time
from process_image import process_image
from optical_flow_yuru import TelloOpticalFlow

tello = Tello()
tello.connect()
tello.streamon()
frame_read = tello.get_frame_read()

battery = tello.get_battery()
print(f"battery: {battery}")

while True:
    img = frame_read.frame
    img = process_image(img)
    cv.imshow("camera", img)

    led_mask = None # ADD LED DETECTION RESULT

    tello_optical_flow = TelloOpticalFlow()
    tello_optical_flow.get_frame()
    tello_optical_flow.sparse_optical_flow_lk(led_mask)     # also run PID and follow light for each change

    key = cv.waitKey(1) & 0xFF
    if key == ord("q"):
        break
    time.sleep(1 / 5)

tello.streamoff()
