import cv2
import numpy as np
from djitellopy import Tello
import time
from led_detection import detect_leds


class TelloOpticalFlow:
    def __init__(self):
        self.tello = Tello()
        self.tello.connect()
        self.tello.streamon()
        self.tello.takeoff()
        self.frame_read = self.tello.get_frame_read()

        self.frame = None
        self.px_movements = []

        self.feature_params = dict(
            maxCorners=15, qualityLevel=0.01, minDistance=2, blockSize=7)
        self.lk_params = dict(winSize=(15, 15), maxLevel=2, criteria=(
            cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))

    def get_frame(self):
        try:
            self.frame = self.frame_read.frame
            return self.frame
        except Exception as e:
            print(e)

    def sparse_optical_flow_lk(self):
        frame0 = self.get_frame()

        led_mask, radius0 = detect_leds(np.copy(self.frame))
        # convert img_mask, which is a numpy array, to an array where 
        # the value is 0 if the pixel is black and 1 if the pixel is white
        led_mask = led_mask[:, :, 0]
        led_mask = led_mask // 255
        frame0_gray = cv2.cvtColor(frame0, cv2.COLOR_BGR2GRAY)
        corners0 = cv2.goodFeaturesToTrack(
            frame0_gray, mask=led_mask, **self.feature_params)

        while True:
            self.get_frame()
            cv2.imshow("Frame", self.frame)
            key = cv2.waitKey(1)
            if key == ord('q'):
                break

            led_mask, radius1 = detect_leds(np.copy(self.frame))
            # convert img_mask, which is a numpy array, to an array where 
            # the value is 0 if the pixel is black and 1 if the pixel is white
            led_mask = led_mask[:, :, 0]
            led_mask = led_mask / 255

            frame_gray = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
            corners1, state, errors = cv2.calcOpticalFlowPyrLK(
                frame0_gray, frame_gray, corners0, None, **self.lk_params)

            if corners1 is None:
                corners0 = cv2.goodFeaturesToTrack(
                    frame0_gray, mask=led_mask, **self.feature_params)
                corners1, state, errors = cv2.calcOpticalFlowPyrLK(
                    frame0_gray, frame_gray, corners0, None, **self.lk_params)

            found_current = corners1[state == 1]
            found_prev = corners0[state == 1]

            changes = found_current - found_prev
            if changes.shape[0] != 0:
                avg_change = np.sum(changes, axis=0) / changes.shape[0]
                avg_change = np.insert(avg_change, 1, [radius0, radius1])
                self.px_movements.append(avg_change)

            frame0_gray = frame_gray.copy()
            corners0 = np.reshape(found_current, (-1, 1, 2))
            radius0 = radius1

        return self.px_movements


if __name__ == "__main__":
    driver = TelloOpticalFlow()
    driver.sparse_optical_flow_lk(None)
