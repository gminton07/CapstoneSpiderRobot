import time
import numpy as np
import cv2
import argparse
from Take_Image import Capture_Image

# Set up the arguments #
parser = argparse.ArgumentParser()
parser.add_argument('--debug',help='helps to debug by saving images to SD rather than ram and provides debug statements',action='store_true')
parser.add_argument('--resolution',help='adjust the resolution of the camera for speed and memory sake', type = int, nargs='+', default = [1640,1232])
parser.add_argument('--sleep', help='time delay after taking image', type = float, default = .1)
parser.add_argument('--Gradient', help = 'Alter the gradient min and max for Canny detection', type = int, nargs='+', default = [50,80] )
parser.add_argument('--ApertureSize', help='Adjust the Canny algorithm to find filter the magnitude of the gradient for line detection. Gradients are computed using the convolution of a pixel, possible alternative is the scharr function, they are both discrete derivative aproximations', type = int, default=3)
parser.add_argument('--take_img', help='choosing whether to take a picture or import image', action='store_true')
args = parser.parse_args()

# Select the Camera Resolution #
row = args.resolution[0]
column = args.resolution[1]

# Take the image #

if args.take_img:
    img = Capture_Image(row,column)
else:
    filename = input('Enter Filename: ')
    img = cv2.imread(filename)
    img = cv2.resize(img,(row,column) )


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

# Apply Canny detection #
canny_img = cv2.Canny(blur_gray_img, args.Gradient[0], args.Gradient[1],apertureSize=args.ApertureSize)

# Apply the lines detection #
lines = cv2.HoughLinesP(canny_img, 1, np.pi/180, threshold = 100, minLineLength=20, maxLineGap=10)

with open('lines.txt','w') as file:
    file.write(f'str{lines}\n')

# make the black image #
black_img = np.zeros( (args.resolution[1],args.resolution[0]),dtype='uint8')


if lines is not None:
    for line in lines:
        x1,y1,x2,y2 = line[0]
        cv2.line(black_img, (x1,y1),(x2,y2),255,1)

# Display img #
cv2.imshow('lines detected', black_img)
cv2.waitKey(0)
