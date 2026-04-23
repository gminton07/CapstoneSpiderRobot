import numpy as np
import time
from Camera_Functions import Camera, img_process
from Take_Image import Capture_Image

while True:
    # Loop indefinitely and take a one second wait #
    time.sleep(1)
    Camera(debug=True, take_img=True, debug_img = True, Gradient= (180, 40))

