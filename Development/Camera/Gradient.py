import cv2
import numpy as np

# Import the desired file for the gradient analysis #
filename = input('Enter File Here: ')
orig_img = cv2.imread(filename)

# determine the image size #
y_height = 1640
x_width = 1232

# Find the imae shape and convert the image format #
orig_img = cv2.resize(orig_img, (y_height,x_width), cv2.INTER_LINEAR)
height,width = orig_img.shape[:2]
gray_img = cv2.cvtColor(orig_img, cv2.COLOR_BGR2GRAY)
blur_gray_img = cv2.blur(gray_img,(5,5))
new_img = orig_img.copy()

def blank(x):
    pass;


cv2.namedWindow('window',cv2.WINDOW_NORMAL)
cv2.resizeWindow('window',width,height)


# This code formats the window #
verstr = 'vert_1'
verstr2 = 'vert_2'
horzstr='horz_1'
horzstr2 = 'horz_2'


cv2.createTrackbar(verstr,'window',0,height-1,blank)
cv2.createTrackbar(horzstr,'window',0,width-1, blank)

# Adding another tracker bar to determine the gradient #
cv2.createTrackbar(verstr2,'window',height-1 ,height-1,blank)
cv2.createTrackbar(horzstr2,'window', width-1 ,width-1,blank)


while True:
    # Create a new overlay to prevent saved circles when testing pixels#
    img = blur_gray_img.copy()

    # Creates a red circle #
    lc = cv2.getTrackbarPos(verstr, 'window')
    hc = cv2.getTrackbarPos(horzstr, 'window')

    # Creates a blue circle to know the position #
    lc2 = cv2.getTrackbarPos(verstr2, 'window')
    hc2 = cv2.getTrackbarPos(horzstr2, 'window')


    # obtain the value of at the located point #
    g1val = int(blur_gray_img[lc,hc])     # First point value #
    g2val = int(blur_gray_img[lc2,hc2])   # Second point value #
    gval = np.abs(int(g2val - g1val))               # The gradient or the differential #

    # Set the circular image #
    cv2.circle(img, (hc,lc), radius = int(width*0.005),color=(255,0,0), thickness=int(width*.002)) 
    cv2.circle(img, (hc2,lc2), radius = int(width*0.005),color=(255,0,0), thickness=int(width*.002)) 

    outstring = (f'G1:{g1val}\t G2: {g2val}\tGradient: {gval}')
    cv2.setWindowTitle('window',outstring)
    cv2.imshow('window',img)

    if cv2.waitKey(1) == 32:
        cv2.destroyAllWindows()
        outstring = (f'({lc}, {hc}) H:{hval} S:{sval} V:{vval}')

        # Place the circles on the blur grayed image, not OG image #
        orig_img = cv2.putText(img, outstring, (10,10), cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,255,0),2)
        cv2.imwrite('filtered_img.jpg',img)
        break;
