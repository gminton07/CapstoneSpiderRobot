import numpy as np
# Rotation Matrices #

def Right_Rear_Rotation_1_0(x,theta):
    
    # Find the number of rows to impliment a ones matrix #
    rows = np.size(x[:,0])
    part_scale = np.ones([rows,1])
    
    
    # Sandwich the matrix with the ones vector #    
    x = np.hstack((x,part_scale))
    
    # Normalize the angle theta relative to the rotation #
    theta_1 = theta-3*np.pi/4
    
    # Create the rotation matrix #
    Rz = np.array([[np.cos(theta_1),-np.sin(theta_1),0,-5.66023622/2],[np.sin(theta_1),np.cos(theta_1),0,-4.98385827/2],[0,0,1,0],[0,0,0,1]])
    
    # Transformation Matrix #
    Trans_Link1= (Rz@x.T).T
    
    return Trans_Link1, Rz

def Right_Front_Rotation_1_0(x,theta):
    
    # Find the number of rows to impliment a ones matrix #
    rows = np.size(x[:,0])
    part_scale = np.ones([rows,1])
    
    # Sandwich the matrix with the ones vector #    
    x = np.hstack((x,part_scale))
    
    # Normalize the angle theta relative to the rotation #
    theta_1 = theta - np.pi/4
    
    # Create the rotation matrix #
    Rz = np.array([[np.cos(theta_1),-np.sin(theta_1),0,5.66023622/2],[np.sin(theta_1),np.cos(theta_1),0,-4.98385827/2],[0,0,1,0],[0,0,0,1]])
    
    # Transformation Matrix #
    Trans_Link1= (Rz@x.T).T
    
    return Trans_Link1, Rz

def Left_Front_Rotation_1_0(x,theta):
    
    # Find the number of rows to impliment a ones matrix #
    rows = np.size(x[:,0])
    part_scale = np.ones([rows,1])
    
    # Sandwich the matrix with the ones vector #    
    x = np.hstack((x,part_scale))
    
    # Normalize the angle theta relative to the rotation #
    theta_1 = theta + np.pi/4
    
    # Create the rotation matrix #
    Rz = np.array([[np.cos(theta_1),-np.sin(theta_1),0,5.66023622/2],[np.sin(theta_1),np.cos(theta_1),0,4.98385827/2],[0,0,1,0],[0,0,0,1]])
    
    # Transformation Matrix #
    Trans_Link1= (Rz@x.T).T
    
    return Trans_Link1,Rz

def Left_Rear_Rotation_1_0(x,theta):
    
    # Find the number of rows to impliment a ones matrix #
    rows = np.size(x[:,0])
    part_scale = np.ones([rows,1])
    
    # Sandwich the matrix with the ones vector #    
    x = np.hstack((x,part_scale))
    
    # Normalize the angle theta relative to the rotation #
    theta_1 = theta + np.pi*3/4
    
    # Create the rotation matrix #
    Rz = np.array([[np.cos(theta_1),-np.sin(theta_1),0,-5.66023622/2],[np.sin(theta_1),np.cos(theta_1),0,4.98385827/2],[0,0,1,0],[0,0,0,1]])
    
    # Transformation Matrix #
    Trans_Link1= (Rz@x.T).T
    
    return Trans_Link1,Rz

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

def walking_cycle(gamma):
    ####### Create parameters #########
    
    # keep gamma 0 until we can walk  #
    
    # S = Static Reference point height #
    S = 7.6327774131716355*0
    

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
    
        
    Rot_Front_Right = np.array([[np.cos(gamma), -np.sin(gamma),0,7.965677269102155-.2],[np.sin(gamma), np.cos(gamma),0,-7.273934903508881+.2],[0,0,1,-7.6327774131716355 +2],[0,0,0,1]])
    Rot_Front_Left = np.array([[np.cos(gamma), -np.sin( gamma), 0, 7.965677269102155-.2],[np.sin(gamma),np.cos(gamma),0,7.273934903508881-.2],[0,0,1,-7.6327774131716355 +2],[0,0,0,1]])
    Rot_Rear_Left = np.array([[np.cos(gamma), -np.sin( gamma), 0, -7.965677269102155+.2],[np.sin(gamma), np.cos(gamma),0,7.273934903508881-.2],[0,0,1,-7.6327774131716355 +2],[0,0,0,1]])
    Rot_Rear_Right = np.array([[np.cos(gamma), -np.sin(gamma), 0, -7.965677269102155+.2],[np.sin(gamma), np.cos(gamma),0,-7.273934903508881+.2],[0,0,1,-7.6327774131716355 +2],[0,0,0,1]])
    
    rot_walking_path_FR = Rot_Front_Right @ walking_path
    rot_walking_path_FL = Rot_Front_Left@walking_path
    rot_walking_path_RR = Rot_Rear_Right@walking_path
    rot_walking_path_RL = Rot_Rear_Left@walking_path
    
    return rot_walking_path_FL,rot_walking_path_FR,rot_walking_path_RL,rot_walking_path_RR
    
    
    