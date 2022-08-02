import cv2 as cv
import os

images = os.listdir("images")

for img_name in images:
    img = cv.imread(f"images/{img_name}", cv.IMREAD_GRAYSCALE)
    ret, thresholded = cv.threshold(img, 150, 255, cv.THRESH_BINARY)
    cv.imshow(img_name, thresholded)

cv.waitKey(0)
