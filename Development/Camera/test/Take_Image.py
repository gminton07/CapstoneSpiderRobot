import io
import cv2
import numpy as np
import subprocess


def Capture_Image(row = '1640', column = '1232'):

    # Create the command to take a video frame #
    command = ['rpicam-vid','-t','1','--frames','1','--width', str(column),'--height',str(row),'--codec','mjpeg','-o','-','-n']

    # Run the subprocess to allow the command #
    pic = subprocess.run(command,capture_output=True, check=True)
    img_byte = pic.stdout # Send the bits out #

    nparr = np.frombuffer(img_byte,np.uint8) # the format of the decoder #
    # Create the decoded image #
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    return img
