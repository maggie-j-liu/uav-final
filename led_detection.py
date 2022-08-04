from imutils import contours
import imutils
from skimage import measure
import cv2
from djitellopy import Tello
import numpy as np
import time
import os


def detect_leds(img):
    img_mask = np.zeros(img.shape, dtype=np.uint8)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (11, 11), 0)
    thresh = cv2.threshold(blurred, 200, 255, cv2.THRESH_BINARY)[1]
    thresh = cv2.erode(thresh, None, iterations=2)
    thresh = cv2.dilate(thresh, None, iterations=4)

    # perform a connected component analysis on the thresholded
    # image, then initialize a mask to store only the "large"
    # components
    labels = measure.label(thresh, background=0)
    mask = np.zeros(thresh.shape, dtype="uint8")
    # loop over the unique components
    for label in np.unique(labels):
        # if this is the background label, ignore it
        if label == 0:
            continue
        # otherwise, construct the label mask and count the
        # number of pixels
        labelMask = np.zeros(thresh.shape, dtype="uint8")
        labelMask[labels == label] = 255
        numPixels = cv2.countNonZero(labelMask)
        # if the number of pixels in the component is sufficiently
        # large, then add it to our mask of "large blobs"
        if numPixels > 100:
            mask = cv2.add(mask, labelMask)

        # find the contours in the mask, then sort them from left to
        # right
        cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
                                cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        try:
            cnts = contours.sort_contours(cnts)[0]
        except ValueError:
            # do nothing
            print('No LEDs in frame')
        except:
            # do nothing
            print('Something else went wrong')
        else:
            # loop over the contours
            radii = []
            for (i, c) in enumerate(cnts):
                # draw the bright spot on the image
                (x, y, w, h) = cv2.boundingRect(c)
                ((cX, cY), radius) = cv2.minEnclosingCircle(c)
                radii.append(radius)
                cv2.circle(img, (int(cX), int(cY)),
                           int(radius), (0, 0, 255), 3)
                cv2.circle(img_mask, (int(cX), int(cY)), int(radius),
                           (255, 255, 255), -1)
                print("saw smth")
                # cv2.putText(img, "#{}".format(i + 1), (x, y - 15),
                #             cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 255), 2)

    cv2.imshow("circles", img)
    cv2.imshow("mask", img_mask)
    cv2.waitKey(1)
    return img_mask, radii[0]


if __name__ == "__main__":
    images = os.listdir("images")

    for img_name in images:
        img = cv2.imread(f"images/{img_name}")
        img = detect_leds(img)
        # cv2.imwrite(f"output_2/{img_name}", img)
        cv2.imshow(img_name, img)
    cv2.waitKey(0)
    # tello = Tello()
    # tello.connect()

    # tello.streamon()
    # frame_read = tello.get_frame_read()

    # # tello.takeoff()

    # while True:
    #     img = frame_read.frame
    #     img = detect_leds(img)
    #     cv2.imshow("LEDs in image", img)
    #     time.sleep(0.75)
    #     key = cv2.waitKey(1) & 0xff
    #     if key == ord('q'):
    #         break

    # tello.streamoff()
    # tello.end()
