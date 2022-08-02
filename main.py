from djitellopy import Tello
import cv2 as cv
import time

tello = Tello()
tello.connect()
tello.streamon()
frame_read = tello.get_frame_read()

battery = tello.get_battery()
print(f"battery: {battery}")

while True:
    img = frame_read.frame
    cv.imshow("camera", img)
    key = cv.waitKey(1) & 0xFF
    if key == ord("q"):
        break
    elif key == ord("s"):
        cv.imwrite(f"images/image-{time.time()}.png", img)
    time.sleep(1 / 5)

tello.streamoff()
