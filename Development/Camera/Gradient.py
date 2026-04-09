import cv2

# Import the desired file for the gradient analysis #
filename = input('Enter File Here: ')
orig_img = cv2.imread(filename)

# Find the imae shape and convert the image format #
height,width = orig_img.shape[:2]
gray_img = cv2.cvtColor(orig_img, cv2.COLOR_BGR2GRAY)
blur_gray_img = cv2.blur(gray_img,(5,5))
new_img = orig_img.copy()

def blank(x):
    pass;

# This code formats the window #
verstr = (f'vert 0: {height-1}')
horzstr =(f'hort 0: {width-1}')
cv2.namedWindow('window',cv2.WINDOW_NORMAL)

cv2.resizeWindow('window',width,height)
cv2.createTrackbar(verstr,'window',0,height-2,blank)
cv2.createTrackbar(horzstr,'window',0,width-2, blank)

# Adding another tracker bar to determine the gradient #
cv2.createTrackbar(verstr,'window',0,height-1,blank)
cv2.createTrackbar(horzstr,'window',0,width-1,blank)


while True:

    # Creates a red circle #
    lc = cv2.getTrackbarPos(verstr, 'window')
    hc = cv2.getTrackbarPos(horzstr, 'window')
    new_img = cv2.circle(blur_gray_img, (hc,lc), radius = int(width*0.005),color=(0,0,255), thickness=int(width*.002))

    # Creates a blue circle to know the position #
    lc2 = cv2.getTrackbarPos(verstr, 'window')
    hc2 = cv2.getTrackbarPos(horzstr, 'window')
    new_img = cv2.circle(blur_gray_img, (hc2,lc2), radius = int(width*0.005),color=(255,0,0), thickness=int(width*.002)) 


    # obtain the value of at the located point #
    g1val = blur_gray_img[lc,hc]     # First point value #
    g2val = blur_gray_img[lc2,hc2]   # Second point value #
    gval = g2val - g1val               # The gradient or the differential #

    cv2.imshow('window',new_img)
    outstring = (f'G1:{g1val}\t G2: {g2val}\tGradient: {gval}')
    cv2.setWindowTitle('window',outstring)

    if cv2.waitKey(1) == 32:
        cv2.destroyAllWindows()
        outstring = (f'({lc}, {hc}) H:{hval} S:{sval} V:{vval}')

        # Place the circles on the blur grayed image, not OG image #
        orig_img = cv2.circle(blur_gray_img, (hc,lc), int(width*.005), color=(0,0,255), thickness=int(width*.002))
        orig_img = cv2.circle(blur_gray_img, (hc2,lc2), int(width*.005), color=(255,0,0), thickness=int(width*.002))
        orig_img = cv2.putText(blur_gray_img, outstring, (height//10,width//10), cv2.FONT_HERSHEY_SIMPLEX,2,(0,0,255),5)
        cv2.imwrite('new_img.jpg',blur_gray_img)
        break;
