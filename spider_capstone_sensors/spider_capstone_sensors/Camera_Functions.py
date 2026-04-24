### This code is using the Camera_Test.py code to be defined as a function call ###
import numpy as np
import cv2
import io
import subprocess

def Capture_Image(row = '1640', column = '1232'):
     # Create the command to take a video frame #
#     command = ['rpicam-vid','-t','1','--frames','1','--width', str(column),'--height', str(row),'--codec','mjpeg','-o','-','-n']
     # Run the subprocess to allow the command #
    #  pic = subprocess.run(command,capture_output=True, check=True)
    #  img_byte = pic.stdout # Send the bits out #

    #  nparr = np.frombuffer(img_byte,np.uint8) # the format of the decoder #
     # Create the decoded image #
    #  img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    ret, img = cam.read()


    return img

def Camera(resolution=(1640, 1230), HSV_lim = (150, 180) , debug = False, debug_img = False, ApertureSize = 3, Gradient = (50,80), take_img=False):
    
    # Select the Camera Resolution #
    row = resolution[0]
    column = resolution[1]
    
    # Take the image #
    
    if take_img:
        img = Capture_Image(row,column)
    else:
        filename = input('Enter Filename: ')
        img = cv2.imread(filename)
        img = cv2.resize(img,(row,column) )
    
    
    # Debug statement of saving the image #
#    if debug_img:
#        cv2.imwrite('test_image.png',img)
#        print('saving image as test_image')
    
    # Convert image to HSV #
    HSV_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # Mask the HSV range to look for desired color #
    Mask_img = cv2.inRange(HSV_img, (HSV_lim[0],130, 50), (HSV_lim[1], 255, 255) )
    if debug:
        cv2.imwrite('masked_img.jpeg',Mask_img)
        cv2.imshow('masked',Mask_img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    # Find the moments of the Masked image #
    M = cv2.moments(Mask_img)
    cX = int(M['m10']/M['m00'])
    cY = int(M['m01']/M['m00'])

    # Find the center of the image #
    center = [int(resolution[1]/2) , int(resolution[0]/2) ] # [x,y] #
    heading_angle = np.arctan2( ((center[0]-cX)), (abs(center[1] - cY)) )
    heading_angle = heading_angle * 180/(np.pi)
    if debug:
        print(heading_angle)


####### Everything below is commented out to accomodate the color detection algorithm #######
    
    # Blur out the image interpolating a 5x5 area surrounding pixel #
#    blur_gray_img = cv2.blur(gray_img,(3,3)) # Altering might help with line detect? #
    
#    if debug_img:
#        cv2.imwrite('test_gray_img.png',blur_gray_img)
#        print('saving the image as a test image')
    
    # Apply Canny detection #
#    canny_img = cv2.Canny(blur_gray_img, Gradient[0], Gradient[1],apertureSize=ApertureSize)
    
    # Apply the lines detection #
#    lines = cv2.HoughLinesP(canny_img, 1, np.pi/180, threshold = 100, minLineLength=20, maxLineGap=10)

    # Extrapolate the lines #    
#    if lines is not None:
#        data=lines.reshape(-1,4)
#        if debug_img:
            # Create a black image to plot lines detected #
#            black_img = np.zeros( (resolution[1], resolution[0]), dtype = 'uint8' )
#            for line in lines:
#                x1,y1,x2,y2 = line[0]
#                cv2.line(black_img, (x1,y1), (x2,y2), 255,1)
#            cv2.imshow('before magnitude and angular filter', black_img)
#            cv2.waitKey(0)
#            cv2.destroyAllWindows()
    # Call in additional Image processing #
#    img_process(data, debug = debug)
    
    
    return heading_angle


def img_process(data,angle_offset=10, debug=False,resolution = (1640,1230), distance_filter = 20):
    # Pull each data set #
    x1 = data[:,0]
    y1 = data[:,1]
    x2 = data[:,2]
    y2 = data[:,3]

    # Create the point locations and find the vector #
    P1 = np.column_stack((x1,y1))
    P2 = np.column_stack((x2,y2))
    vector =P2 - P1

    # Apply an average filter to remove excessive lines #

    magnitude = np.linalg.norm(vector,axis=1)

    # Magnitude filter (Use the median) #
    median_num = np.median(magnitude)

    # initialize the median filter vector #
    med_vector = magnitude > (median_num + angle_offset).astype(int)

    # find the indices where the vector is zero and remove those lines #
    new_P1 = P1[med_vector]
    new_P2 = P2[med_vector]

    # Apply a distance filter between vectors #

    ########## order of the filter ###############
    # find the angle of the vector
    # this is a filter in itself to filter lines with the same angle
    new_vector = new_P2 - new_P1
    theta = np.arctan2(new_vector[:,1],new_vector[:,0])

    # create the offset #
    angle_offset = 5* np.pi / 180

    # initialize the mask angle vectors#
    angle_mask = np.zeros([len(theta),len(theta)])

    # filter through the angles #
    diff = np.abs(theta[:,None] - theta[None,:])
    diff = np.minimum(diff, np.pi-diff)
    angle_mask = (diff < angle_offset).astype(int)

    # Now we can check for the row vectors that would be the same and eliminate those #
    new_magnitude = np.linalg.norm(new_vector,axis=1)
    unit_vector = new_vector/new_magnitude[:,None]

    # create the filter matrix #
    distance_mask = np.zeros((len(theta),len(theta)))

    # run through each line to find the distance and apply threshold #
    for i in range(len(theta)):

        diff_point = new_P1 - new_P1[i]

        cross = np.abs( np.cross(diff_point,unit_vector[i]) )

        distance_mask[i,:] = (cross < distance_filter).astype(int)

    # Combine the anglular and distance filter #
    Mask = angle_mask*distance_mask
    np.fill_diagonal(Mask,0)

    # initialize the keep matrix that defines which lines are to be kept #
    keep = np.ones(len(theta), dtype = bool)
    magnitudes = np.linalg.norm(new_vector, axis=1)


    # Create the keep matrix and remove redundant relationships #
    # keeps matrix based on magnitude #
    for i in range(len(theta)):
        if not keep[i]:
            continue
        duplicates = np.where(Mask[i] == 1)[0]
        for j in duplicates:
            if magnitudes[j]<= magnitudes[i]:
                keep[j] = False
            else:
                keep[i] = False
                break

    # filtered output of the image processing #
    filtered_p1 = new_P1[keep]
    filtered_p2 = new_P2[keep]


    ########### Place in the new line points #########
    new_lines = np.column_stack( (filtered_p1, filtered_p2) )


    # With args debug we can have a plot to check if we have a good filter model #
    if debug:
        black_img = np.zeros( (resolution[1], resolution[0]),dtype='uint8')
        for line in new_lines:
            x1,y1,x2,y2 = line
            cv2.line(black_img,(int(x1),int(y1)),(int(x2),int(y2)),255,1)

        cv2.imshow('lines detected',black_img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    return

