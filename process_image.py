import cv2 as cv
import os
import math
import numpy as np
from djitellopy import Tello
import time


DEBUG = False


def process_image(img):
    img_mask = np.zeros(img.shape, dtype=np.uint8)
    img_gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    ret, thresh = cv.threshold(img_gray, 200, 255, cv.THRESH_BINARY_INV)
    if DEBUG:
        cv.imshow("thresh", thresh)
        cv.waitKey(0)
    thresh = cv.blur(thresh, (7, 7))
    if DEBUG:
        cv.imshow("thresh", thresh)
        cv.waitKey(0)
    thresh = cv.bitwise_not(thresh)
    if DEBUG:
        cv.imshow("thresh", thresh)
        cv.waitKey(0)
    contours, hierarchy = cv.findContours(
        thresh, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    for contour in contours:
        area = cv.contourArea(contour)
        # print('area', area)
        if area > 100:
            M = cv.moments(contour)
            cx = int(M['m10'] / M['m00'])
            cy = int(M['m01'] / M['m00'])
            (x, y), radius = cv.minEnclosingCircle(contour)
            center = (int(x), int(y))
            radius = int(radius)
            extent = float(area) / (math.pi * (radius ** 2))
            if extent > 0.39:
                cr = int(math.sqrt(area / math.pi))
                circle_img = np.zeros(
                    (img.shape[0], img.shape[1], 3), np.uint8)
                cv.circle(circle_img, (cx, cy), cr, (255, 255, 255), 1)
                gray_circle_img = cv.cvtColor(circle_img, cv.COLOR_BGR2GRAY)
                ret, circle_thresh = cv.threshold(
                    gray_circle_img, 200, 255, cv.THRESH_BINARY)
                circle_contours, hierarchy = cv.findContours(
                    circle_thresh, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
                circle_contour = circle_contours[0]

                match = cv.matchShapes(
                    circle_contour, contour, 1, 0.0)
                # print("match", match)
                if match < 0.31:
                    cv.circle(img, center, radius, (255, 0, 0), 3)
                    cv.drawContours(img, [contour], 0, (0, 255, 0), 3)
                    cv.drawContours(img, [circle_contour], 0, (0, 0, 255), 3)
                    cv.circle(img_mask, center, radius, (255, 255, 255), -1)

    return img, img_mask


if __name__ == "__main__":
    tello = Tello()
    tello.connect()
    tello.streamon()
    tello.takeoff()
    frame_read = tello.get_frame_read()
    while True:
        frame = frame_read.frame
        circles, img_mask = process_image(frame)
        cv.imshow("circles", circles)
        cv.imshow("mask", img_mask)
        key = cv.waitKey(1) & 0xFF
        if key == ord("q"):
            break
        time.sleep(1 / 5)
    tello.streamoff()
    tello.land()
    tello.end()
    # images = os.listdir("images")

    # for img_name in images:
    #     img = cv.imread(f"images/{img_name}")
    #     img = process_image(img)
    # cv.imwrite(f"output_1/{img_name}", img)

    # cv.waitKey(0)
