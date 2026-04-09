import time
import numpy as np
import cv2
import argparse
from Take_Image import Capture_Image

# Set up the arguments #
parser = argparse.ArgumentParser()
parser.add_argument('--debug',help='helps to debug by saving images to SD rather than ram and provides debug statements',action='store_true')
parser.add_argument('-resolution',help='adjust the resolution of the camera for speed and memory sake', type = int, nargs='+', default = [1640,1232])
parser.add_argument('--sleep', help='time delay after taking image', type = float, default = .1)
args = parser.parse_args()

# Select the Camera Resolution #
row = args.resolution[0]
column = args.resolution[1]

# Take the image #
img = Capture_Image(row,column)

# Debug statement of saving the image #
if args.debug:
    cv2.imwrite('test_image.png',img)
    print('saving image as test_image')

# Convert image to grayscale #
gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# Blur out the image interpolating a 5x5 area surrounding pixel #
blur_gray_img = cv2.blur(gray_img,(5,5))
if args.debug:
    cv2.imwrite('test_gray_img.png',blure_gray_img)
    print('saving the image as a test image')

# Apply the lines detection #
lines = cv2.HoughLinesP(blur_gray_img, 1, np.pi/180, threshold = 100, minLineLength=20, maxLineGap=10)
