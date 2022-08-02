#!/usr/bin/python3

import cv2
import numpy as np
from djitellopy import Tello

PX_TO_MM_FACTOR = 0.0264583     # inaccurate


class TelloOpticalFlow:
    def __init__(self):
        self.tello = Tello()
        self.tello.connect()
        self.tello.streamon()

        self.frame = None

        self.px_movements = np.array()

    def get_frame(self):
        try:
            self.frame = self.tello.get_frame_read().frame
            self.frame = np.array(self.frame, dtype='uint8')
            return self.frame
        except Exception as e:
            print(e)

    def sparse_optical_flow_lk(self):
        feature_params = dict(maxCorners =  15, qualityLevel = 0.01, minDistance = 2, blockSize = 7) # helps decide what corners should be tracked
        frame0 = self.get_frame()
        frame0_gray = cv2.cvtColor(frame0, cv2.COLOR_BGR2GRAY)
        corners0 = cv2.goodFeaturesToTrack(frame0_gray, mask=None, **feature_params) # add mask from led detection so that we have a ROI

        lk_params = dict(winSize=(15, 15), maxLevel=2, criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))

        while True:
            self.get_frame()
            frame_gray = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
            corners1, state, errors = cv2.calcOpticalFlowPyrLK(frame0_gray, frame_gray, corners0, None, **lk_params)

            found_current = corners1[state == 1]
            found_prev = corners0[state == 1]

            if found_current.shape == found_prev.shape:
                changes = found_current - found_prev
                avg_change = np.sum(changes, axis=0) / changes.shape[0] # assuming ROI

                # calculate forward-backward change from ratio of (current average side length) / (previous average side length)
                curr_len = np.mean(found_current[1][0]-found_current[0][0], found_current[2][0]-found_current[3][0], 
                                    found_current[3][1]-found_current[0][1], found_current[2][1]-found_current[1][1])
                prev_len = np.mean(found_current[1][0]-found_current[0][0], found_current[2][0]-found_current[3][0], 
                                    found_current[3][1]-found_current[0][1], found_current[2][1]-found_current[1][1])
                fb_change = (curr_len - prev_len) * PX_TO_MM_FACTOR

                np.insert(avg_change, 1, fb_change)
                np.append(self.px_movements, avg_change)



if __name__ == "__main__":
    tello_optical_flow = TelloOpticalFlow()
    tello_optical_flow.get_frame()
    tello_optical_flow.sparse_optical_flow_lk()

    print("px_movements:", tello_optical_flow.px_movements)