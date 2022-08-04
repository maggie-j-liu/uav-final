import cv2
import numpy as np
from djitellopy import Tello
import time


class TelloOpticalFlow:
    def __init__(self):
        self.drone = Tello()
        self.drone.connect()
        self.drone.streamon()

        print(self.drone.get_battery())

        self.frame = None
        self.px_movements = []
        self.time0 = time.time()

    def get_frame(self):
        try:
            self.frame = self.drone.get_frame_read().frame
            self.frame = np.array(self.frame, dtype='uint8')
            return self.frame
        except Exception as e:
            print(e)

    def sparse_optical_flow_lk(self):
        feature_params = dict(
            maxCorners=15, qualityLevel=0.01, minDistance=2, blockSize=7)
        frame0 = self.get_frame()
        frame0_gray = cv2.cvtColor(frame0, cv2.COLOR_BGR2GRAY)
        corners0 = cv2.goodFeaturesToTrack(
            frame0_gray, mask=None, **feature_params)

        lk_params = dict(winSize=(15, 15), maxLevel=2, criteria=(
            cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))

        while True:
            self.get_frame()
            cv2.imshow("Frame", self.frame)
            key = cv2.waitKey(1)
            if key == ord('q'):
                break

            frame_gray = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
            corners1, state, errors = cv2.calcOpticalFlowPyrLK(
                frame0_gray, frame_gray, corners0, None, **lk_params)

            if corners1 is None:
                corners0 = cv2.goodFeaturesToTrack(
                    frame0_gray, mask=None, **feature_params)
                corners1, state, errors = cv2.calcOpticalFlowPyrLK(
                    frame0_gray, frame_gray, corners0, None, **lk_params)

            found_current = corners1[state == 1]
            found_prev = corners0[state == 1]

            changes = found_current - found_prev
            if changes.shape[0] != 0:
                avg_change = np.sum(changes, axis=0) / changes.shape[0]
                self.px_movements.append(avg_change)

            frame0_gray = frame_gray.copy()
            corners0 = np.reshape(found_current, (-1, 1, 2))

        cv2.destroyAllWindows()


if __name__ == "__main__":
    driver = TelloOpticalFlow()
    driver.sparse_optical_flow_lk()
