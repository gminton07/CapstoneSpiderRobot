'''
Takes a picture every TIMER_PERIOD and opens a viewer
Change to doing computations and sending data off
'''

import cv2
import matplotlib.pyplot as plt
import time

TIMER_PERIOD = 10 # ms 

cap = cv2.VideoCapture('/dev/video0', cv2.CAP_V4L)
# Set frame height & width

try:
    # Open image viewer
    cv2.namedWindow("Input")

    while True:
        rval, frame = cap.read()

        # Show the image
        if rval:
            cv2.imshow("Input", frame)
            cv2.waitKey(TIMER_PERIOD)
        else:
            print("Image not taken")

except KeyboardInterrupt:
    print('STOP')
    cap.release()
    cv2.destroyAllWindows()
