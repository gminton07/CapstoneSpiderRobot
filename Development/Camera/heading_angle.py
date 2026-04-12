import numpy as np
import cv2
import pandas as pd
import argparse

# Setup arguments #
parser = argparse.ArgumentParser()
parser.add_argument('--offset', help = 'Sets the filter offset to remove more lines ', type=int,default=10)
parser.add_argument('--debug',help='helps us check if we have a good filter', action='store_true')
parser.add_argument('--resolution', help='sets the resolution of the image', type=int, nargs='+',default=[1640,1232])
args = parser.parse_args()

# find the data we want to import #
filename = input('Enter file: ')
data = pd.read_csv(filename,header=None)

# Pull each data set #
x1 = data[0]
y1 = data[1]
x2 = data[2]
y2 = data[3]

# Create the point locations and find the vector #
P1 = np.column_stack((x1,y1))
P2 = np.column_stack((x2,y2))
vector =P2 - P1

# Apply an average filter to remove excessive lines #

magnitude = np.linalg.norm(vector,axis=1)

# Magnitude filter (Use the median) #
median_num = np.median(magnitude)

# initialize the median filter vector #
med_vector = magnitude > (median_num + args.offset).astype(int)

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

# distance in pixels from one another #
distance_filter = 10

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
filtered_p2 = new_P1[keep]

# find the line equation and solve for the distance
        # this is a filter that will check if we want to remove the line given the distance
# remove the line with the lesser magnitude

#new_vector = new_P2 - new_P1
#new_magnitude = np.linalg.norm(new_vector,axis=1)

#### Place in the new line points ####
new_lines = np.column_stack( (filtered_p1, filtered_p2) )

# new_lines = np.column_stack((new_p1, new_p2))

# With args debug we can have a plot to check if we have a good filter model #
if args.debug:
    black_img = np.zeros( (args.resolution[1], args.resolution[0]),dtype='uint8')
    for line in new_lines:
        x1,y1,x2,y2 = line
        cv2.line(black_img,(int(x1),int(y1)),(int(x2),int(y2)),255,1)

    cv2.imshow('lines detected',black_img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

# perform computation and replot for testing #

