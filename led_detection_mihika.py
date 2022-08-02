import time, cv2
from djitellopy import Tello
import math
import numpy as np

tello = Tello()

tello.connect()

tello.takeoff()

tello.streamon()
frame_read = tello.get_frame_read()
#tello.send_rc_control(0, 0, 0, 0)

while True:
    img = frame_read.frame
    cv2.imshow('tello camera', img)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    

tello.streamoff()
tello.end()
