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
P1 = np.append(x1,y1)
P2 = np.append(x2,y2)
vector =P2 - P1

# Apply an average filter to remove excessive lines #

# Magnitude filter (Use the median) #
median_num = np.median(np.abs(vector))

for i in vector:
    if np.abs(vector[i]) > median_num + args.offset:
        med_vector[i] = 1
    else:
        med_vector[i] = 0

# find the indices where the vector is zero and remove those lines #
indices = np.where(med_vector==0)[0]
new_P1 = (indices.T)@P1
new_P2 = (indices.T)@P2

new_lines = np.append(new_P1, new_P2)

# With args debug we can have a plot to check if we have a good filter model #
if args.debug:
    black_img = np.zeros( (args.resolution[1], args.resolution[0],dtype='uint8')
        for line in new_lines:
            x1,y1,x2,y2 = line[0]
            cv2.line(black_img,(x1,y1),(x2,y2),255,1)

    cv2.imwshow('lines detected',black_img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

# perform computation and replot for testing #

