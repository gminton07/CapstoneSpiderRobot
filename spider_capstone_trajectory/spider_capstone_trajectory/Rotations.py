import numpy as np

# Variables
XOFFSET = 5.66023622 / 2
YOFFSET = 4.98385827 / 2

# Calculate rotation matrices for each leg
# on robot frame
def Rotation_1_0(link: np.ndarray, theta: float, leg: int = 1) \
    -> tuple[np.ndarray, np.ndarray]:
    # Set x- / y- axis and angular offsets
    x_offset, y_offset = 0, 0
    theta_offset = 0
    match leg:
        # Rear-right rotation
        case 1:
            x_offset = -XOFFSET
            y_offset = -YOFFSET
            theta_offset = -3/4 * np.pi
            pass
        # Front-right rotation
        case 2:
            x_offset = XOFFSET
            y_offset = -YOFFSET
            theta_offset = -1/4 * np.pi
            pass
        # Front-left rotation
        case 3:
            x_offset = XOFFSET
            y_offset = YOFFSET
            theta_offset = 1/4 * np.pi
            pass
        # Rear-left rotation
        case 4:
            x_offset = -XOFFSET
            y_offset = YOFFSET
            theta_offset = 3/4 * np.pi
            pass
        case _:
            raise Exception(f'Error: leg ({leg}) not supported')

    link = matrix_setup(link)
    
    # Normalize the angle theta relative to the rotation
    theta += theta_offset

    # Create rotation matrix
    Rz = np.array([
        [np.cos(theta), -np.sin(theta), 0, x_offset],
        [np.sin(theta),  np.cos(theta), 0, y_offset],
        [0,              0,             1, 0],
        [0,              0,             0, 1]
    ])
    
    # Transformation Matrix
    Trans_Link1= (Rz@link.T).T
    
    return Trans_Link1, Rz

# Matrix resize helper
def matrix_setup(A: np.ndarray) -> np.ndarray:
    rows = np.size(A, 0)
    part_scale = np.ones([rows, 1])
    return np.hstack((A, part_scale))

## Testing Code ##
if __name__ == '__main__':
    A = np.array([
        [0, 0, 0],
        [2, 0, 0],
    ])

    print(A)
    print(matrix_setup(A))

    try:
        trans, rA1 = Rotation_1_0(A, 1.0, 1)
        print(f'{rA1 = }\n{trans = }')
        print(np.shape(rA1))
        rA2 = Rotation_1_0(A, 1.0, 2)
        print(f'{rA2 = }')
        rA3 = Rotation_1_0(A, 1.0, 3)
        print(f'{rA3 = }')
        rA4 = Rotation_1_0(A, 1.0, 4)
        print(f'{rA4 = }')
        rA = Rotation_1_0(A, 1.0, 6)
        print(f'{rA = }')
    except Exception as e:
        print(e)
## Testing Code ##

# Calculates translation matrix from frame-2 to frame-0
def Rotation_2_0(x,theta,Rz,Length):
    
    # Find the number of rows to impliment a ones matrix #
    rows = np.size(x[:,0])
    part_scale = np.ones([rows,1])
    
    # Sandwich the matrix with the ones vector #    
    x = np.hstack((x,part_scale))
    
    # Create the rotation matrix #
    Ry = np.array([[np.cos(theta),0,np.sin(theta), Length],[0,1,0,0],[-np.sin(theta),0,np.cos(theta),0],[0,0,0,1]])
    
    # Transformation Matrix #
    RzRy = Rz@Ry
    
    # Transformation Matrix #
    Trans_Link2= (RzRy@x.T).T
    
    return Trans_Link2, RzRy

# Calculates translation matrix from frame-3 to frame-0
def Rotation_3_0(x,theta,RzRy,Length):
    # Find the number of rows to impliment a ones matrix #
    rows = np.size(x[:,0])
    part_scale = np.ones([rows,1])
    
    # Sandwich the matrix with the ones vector #    
    x = np.hstack((x,part_scale))
    
    # Create the Rotation Matrix #
    Ry2 = np.array([[np.cos(theta),0,np.sin(theta),Length],[0,1,0,0],[-np.sin(theta),0,np.cos(theta),0],[0,0,0,1]])
    
    # Create the Transformations #
    Trans_Link2 = (RzRy@Ry2@x.T).T
    
    return Trans_Link2

def walking_cycle(gamma,spin): ## NOTE: if -1 spin cw and ignore gamma, if 0 use gamma, if 1 ignore gamma and spin ccw
    ####### Create parameters #########
    
    # keep gamma 0 until we can walk  #
    
    # S = Static Reference point height #
    S = 0 #7.6327774131716355
    

    # A = Parabolic Height maximum #
    A = 4#2

    # T = Walking Line length #
    T = 6

    # Create the number of step points in the walking cycle #
    num_points_c = 7 #lets try 5 - (add 2 when entering) (the and end points)
    num_points_L = 15 # line = 3 x curve pts.


    # Place Parabolic equation constants #
    P1 = np.array([-T/2, S])
    P2 = np.array([0.5, S+(2*A)]) # made 0->0.5 for counting points.
    P3 = np.array([T/2, S])
    points = np.linspace(0,1,num_points_c)

    # Create the curve function #
    xcurve = (1-points**2) * P1[0] + 2*(1-points)*points*P2[0]+ (points**2) * P3[0]
    zcurve = (1-points**2)*P1[1] + 2*(1-points) * points*P2[1] + (points**2) * P3[1]

    # Create the line function #
    xline = np.linspace(T/2,-T/2,num_points_L)
    zline = np.linspace(S,S,num_points_L)


    # combine the parabolic and line function on a 2D plane #
    x_points = np.concatenate((xcurve[1:num_points_c-1],xline)) #added [1:num_points_c-1] to chop redundant pts
    z_points = np.concatenate((zcurve[1:num_points_c-1],zline))
    y_points = np.zeros((1,len(x_points)))


    # Stack the points into a row matrix format # 
    walking_path = np.vstack((x_points,y_points,z_points,np.ones((1,len(x_points)))))
    
    # x_offset = 0.2
    # Y_offset = 0.2
    # z_offset = 6 #subtracted from z
        
    # Rot_Front_Right = np.array([[np.cos(gamma), -np.sin(gamma),0,7.965677269102155-x_offset],[np.sin(gamma), np.cos(gamma),0,-7.273934903508881+Y_offset],[0,0,1,-7.6327774131716355-z_offset],[0,0,0,1]])
    # Rot_Front_Left = np.array([[np.cos(gamma), -np.sin( gamma), 0, 7.965677269102155-x_offset],[np.sin(gamma),np.cos(gamma),0,7.273934903508881-Y_offset],[0,0,1,-7.6327774131716355-z_offset],[0,0,0,1]])
    # Rot_Rear_Left = np.array([[np.cos(gamma), -np.sin( gamma), 0, -7.965677269102155+x_offset],[np.sin(gamma), np.cos(gamma),0,7.273934903508881-Y_offset],[0,0,1,-7.6327774131716355-z_offset],[0,0,0,1]])
    # Rot_Rear_Right = np.array([[np.cos(gamma), -np.sin(gamma), 0, -7.965677269102155+x_offset],[np.sin(gamma), np.cos(gamma),0,-7.273934903508881+Y_offset],[0,0,1,-7.6327774131716355-z_offset],[0,0,0,1]])
    
    x_offset = 6 #added
    Y_offset = 6
    z_offset = 5 #subtracted from z

    if spin == 0:
        x_offset = 6 #added
        Y_offset = 6    
        Rot_Front_Right = np.array([[np.cos(gamma), -np.sin(gamma),0,7.965677269102155+x_offset],[np.sin(gamma), np.cos(gamma),0,-7.273934903508881-Y_offset],[0,0,1,-7.6327774131716355-z_offset],[0,0,0,1]])
        x_offset = 6 #added
        Y_offset = 6
        Rot_Front_Left = np.array([[np.cos(gamma), -np.sin( gamma), 0, 7.965677269102155+x_offset],[np.sin(gamma),np.cos(gamma),0,7.273934903508881+Y_offset],[0,0,1,-7.6327774131716355-z_offset],[0,0,0,1]])
        x_offset = 6 #added
        Y_offset = 6        
        Rot_Rear_Left = np.array([[np.cos(gamma), -np.sin( gamma), 0, -7.965677269102155-x_offset],[np.sin(gamma), np.cos(gamma),0,7.273934903508881+Y_offset],[0,0,1,-7.6327774131716355-z_offset],[0,0,0,1]])
        x_offset = 6 #added
        Y_offset = 6       
        Rot_Rear_Right = np.array([[np.cos(gamma), -np.sin(gamma), 0, -7.965677269102155-x_offset],[np.sin(gamma), np.cos(gamma),0,-7.273934903508881-Y_offset],[0,0,1,-7.6327774131716355-z_offset],[0,0,0,1]])
    else: # idea is that by multiplying by 1/-1 (spin) we can set the rotation direction
        Rot_Front_Right = np.array([[np.cos(spin*np.pi/4), -np.sin(spin*np.pi/4),0,7.965677269102155+x_offset],[np.sin(np.pi/4), np.cos(np.pi/4),0,-7.273934903508881-Y_offset],[0,0,1,-7.6327774131716355-z_offset],[0,0,0,1]])
        Rot_Front_Left = np.array([[np.cos(spin*np.pi*(3/4)), -np.sin(spin*np.pi*(3/4)), 0, 7.965677269102155+x_offset],[np.sin(spin*np.pi*(3/4)),np.cos(spin*np.pi*(3/4)),0,7.273934903508881+Y_offset],[0,0,1,-7.6327774131716355-z_offset],[0,0,0,1]])
        Rot_Rear_Left = np.array([[np.cos(spin*np.pi*(5/4)), -np.sin(spin*np.pi*(5/4)), 0, -7.965677269102155-x_offset],[np.sin(spin*np.pi*(5/4)), np.cos(spin*np.pi*(5/4)),0,7.273934903508881+Y_offset],[0,0,1,-7.6327774131716355-z_offset],[0,0,0,1]])
        Rot_Rear_Right = np.array([[np.cos(spin*np.pi*(7/4)), -np.sin(spin*np.pi*(7/4)), 0, -7.965677269102155-x_offset],[np.sin(spin*np.pi*(7/4)), np.cos(spin*np.pi*(7/4)),0,-7.273934903508881-Y_offset],[0,0,1,-7.6327774131716355-z_offset],[0,0,0,1]])

    rot_walking_path_FR = Rot_Front_Right @ walking_path
    rot_walking_path_FL = Rot_Front_Left@walking_path
    rot_walking_path_RR = Rot_Rear_Right@walking_path
    rot_walking_path_RL = Rot_Rear_Left@walking_path
    
    return rot_walking_path_FL,rot_walking_path_FR,rot_walking_path_RL,rot_walking_path_RR
    
def spining_cycle(direction):
    ####### Create parameters #########
    # S = Static Reference point height #
    S = 0 #7.6327774131716355
    # A = Parabolic Height maximum #
    A = 2
    # T = Walking Line length #
    T = 3

    # Create the number of step points in the walking cycle #
    num_points_c = 7 #lets try 5 - (add 2 when entering) (the and end points)
    num_points_L = 15 # line = 3 x curve pts.


    # Place Parabolic equation constants #
    P1 = np.array([-T/2, S])
    P2 = np.array([0.5, S+(2*A)]) # made 0->0.5 for counting points.
    P3 = np.array([T/2, S])
    points = np.linspace(0,1,num_points_c)

    # Create the curve function #
    xcurve = (1-points**2) * P1[0] + 2*(1-points)*points*P2[0]+ (points**2) * P3[0]
    zcurve = (1-points**2)*P1[1] + 2*(1-points) * points*P2[1] + (points**2) * P3[1]

    # Create the line function #
    xline = np.linspace(T/2,-T/2,num_points_L)
    zline = np.linspace(S,S,num_points_L)


    # combine the parabolic and line function on a 2D plane #
    x_points = np.concatenate((xcurve[1:num_points_c-1],xline)) #added [1:num_points_c-1] to chop redundant pts
    z_points = np.concatenate((zcurve[1:num_points_c-1],zline))
    y_points = np.zeros((1,len(x_points)))


    # Stack the points into a row matrix format # 
    walking_path = np.vstack((x_points,y_points,z_points,np.ones((1,len(x_points)))))
    
        
    Rot_Front_Right = np.array([[np.cos(np.pi/4), -np.sin(np.pi/4),0,7.965677269102155-.2],[np.sin(np.pi/4), np.cos(np.pi/4),0,-7.273934903508881+.2],[0,0,1,-7.6327774131716355],[0,0,0,1]])
    Rot_Front_Left = np.array([[np.cos(np.pi*(3/4)), -np.sin(np.pi*(3/4)), 0, 7.965677269102155-.2],[np.sin(np.pi*(3/4)),np.cos(np.pi*(3/4)),0,7.273934903508881-.2],[0,0,1,-7.6327774131716355],[0,0,0,1]])
    Rot_Rear_Left = np.array([[np.cos(np.pi*(5/4)), -np.sin(np.pi*(5/4)), 0, -7.965677269102155+.2],[np.sin(np.pi*(5/4)), np.cos(np.pi*(5/4)),0,7.273934903508881-.2],[0,0,1,-7.6327774131716355],[0,0,0,1]])
    Rot_Rear_Right = np.array([[np.cos(np.pi*(7/4)), -np.sin(np.pi*(7/4)), 0, -7.965677269102155+.2],[np.sin(np.pi*(7/4)), np.cos(np.pi*(7/4)),0,-7.273934903508881+.2],[0,0,1,-7.6327774131716355],[0,0,0,1]])
    
    rot_walking_path_FR = Rot_Front_Right @ walking_path
    rot_walking_path_FL = Rot_Front_Left@walking_path
    rot_walking_path_RR = Rot_Rear_Right@walking_path
    rot_walking_path_RL = Rot_Rear_Left@walking_path
    
    return rot_walking_path_FL,rot_walking_path_FR,rot_walking_path_RL,rot_walking_path_RR
