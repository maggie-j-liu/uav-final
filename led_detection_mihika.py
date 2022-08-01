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
p = PID()

def PIDfunc(tello, tag, p):
    center = (480, 360)
    centroid = tag.getCentroid()
    e_t = math.sqrt((center[0]-centroid[0])**2 + (center[1]-centroid[1])**2)
    if(centroid[0]<center[0]):
        e_t = e_t*-1
    new_yaw = p.update(e_t)
    tello.send_rc_control(0, 0, 0, new_yaw)

while True:
    img = frame_read.frame
    cv2.imshow('tello camera', img)
    arucoDict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_5X5_100)
    corners, ids, rejects = cv2.aruco.detectMarkers(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), arucoDict)
    detection = cv2.aruco.drawDetectedMarkers(img, corners, borderColor=(255, 0, 0))
    if(len(corners)>0):
        corners = np.asarray(corners)
        ids = np.asarray(ids)
        tag = Marker(ids[0][0], corners[0][0][0], corners[0][0][1], corners[0][0][2], corners[0][0][3], frame_read)
        PIDfunc(tello, img, tag, p)
        print('yes \n')
        cv2.imwrite('detection_two_tags_DICT_5x5_100.png', detection)
    key = cv2.waitKey(1) & 0xff
    if key == ord('q'):
        break

tello.streamoff()
tello.end()
