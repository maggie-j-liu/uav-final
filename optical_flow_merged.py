import cv2
import numpy as np
from djitellopy import Tello
import time


class TelloOpticalFlow:
    def __init__(self):
        self.tello = Tello()
        self.tello.connect()
        self.tello.streamon()

        self.frame = None
        self.px_movements = []
        self.time0 = time.time()

        self.PX_TO_MM_FACTOR = 0.0264583    # may be inaccurate
        self.feature_params = dict(maxCorners =  15, qualityLevel = 0.01, minDistance = 2, blockSize = 7)
        self.lk_params = dict(winSize=(15, 15), maxLevel=2, criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))

    def get_frame(self):
        try:
            self.frame = self.tello.get_frame_read().frame
            self.frame = np.array(self.frame, dtype='uint8')
            return self.frame
        except Exception as e:
            print(e)

    def sparse_optical_flow_lk(self, led_mask):
        frame0 = self.get_frame()
        frame0_gray = cv2.cvtColor(frame0, cv2.COLOR_BGR2GRAY)
        corners0 = cv2.goodFeaturesToTrack(frame0_gray, led_mask, **self.feature_params)

        while time.time() - self.time0 < 1.5:
            self.get_frame()
            cv2.imshow("Frame", self.frame)
            cv2.waitKey(1)

            frame_gray = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
            corners1, state, errors = cv2.calcOpticalFlowPyrLK(frame0_gray, frame_gray, corners0, None, **self.lk_params)

            if corners1 is not None:
                print('corners found')
                found_current = corners1[state == 1]
                found_prev = corners0[state == 1]

                changes = found_current - found_prev
                if changes.shape[0] != 0:
                    avg_change = np.sum(changes, axis=0) / changes.shape[0]
                    
                    curr_len = np.mean([found_current[1][0]-found_current[0][0], found_current[2][0]-found_current[3][0], 
                                    found_current[3][1]-found_current[0][1], found_current[2][1]-found_current[1][1]])
                    prev_len = np.mean([found_current[1][0]-found_current[0][0], found_current[2][0]-found_current[3][0], 
                                    found_current[3][1]-found_current[0][1], found_current[2][1]-found_current[1][1]])
                    fb_change = (curr_len - prev_len) / self.PX_TO_MM_FACTOR
                    np.insert(avg_change, 1, fb_change)
                    
                    self.px_movements.append(avg_change)

                frame0_gray = frame_gray.copy()
                corners0 = np.reshape(found_current, (-1, 1, 2))
            else:
                print('no corners found')
        
        return self.px_movements