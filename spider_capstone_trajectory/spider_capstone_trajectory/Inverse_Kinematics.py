import numpy as np;import cmath; import math; import cmath; # import matplotlib.pyplot as plt 
from .Rotations import walking_cycle, Right_Rear_Rotation_1_0, Right_Front_Rotation_1_0, Left_Rear_Rotation_1_0, Left_Front_Rotation_1_0, Rotation_2_0, Rotation_3_0, walking_cycle



def inverse_kinematic(Point):
    
    # print(Point)
    # Create the rotation matrix #
    # Trans = np.array([[np.cos(-np.pi/4), -np.sin(-np.pi/4), 0, 5.66023622/2],[np.sin(-np.pi/4) , np.cos(-np.pi/4), 0, -4.98385827/2],[0,0,1,0],[0,0,0,1]])
    # Trans_inv = np.linalg.inv(Trans)
    # Point = np.append(Point,1)
    
    # Points = (Trans_inv@Point)
    # Change the point location relative to the offset #
    X = Point[0] - 5.66023622/2
    Y = Point[1] + 4.98385827/2
    Z = Point[2]
    

    
    
    # Link Lengths #
    Link1 = 3.8
    Link2 = 4.19
    Link3 = 4.67
    
    # Find the shoulder angle theta 1 #
    theta1 = np.arctan2(Y,X)+np.pi/4
    
    # Geometric variables for theta #
    r2 = np.abs((X)/(np.cos(theta1 - np.pi/4))) - Link1
    r1 = math.sqrt(Z**2 + r2**2)

 
    phi2 = np.arctan2(Z,r2)
    phi1 =  np.arccos((Link3**2 -Link2**2 -r1**2)/(-2* Link2 *r1))

    
    # Find angle 2 from the elbow #
    theta2 = phi1 + phi2
    
    phi3 = np.arccos( (r1**2 -Link2**2 -Link3**2)/(-2*Link3*Link2))
    
    # Find the final angle #
    theta3 = -(np.pi - phi3)
    
    
    return theta1,-theta2,-theta3




# X axis is forward towards the front of the robot, and y is to the left of the robot, z is upwards #
# Coordinates are within the body frame #
# Input should be a coordinate point #
# Idea rotate points into Link1 frame #

def inverse_kinematic_FR(Point):
    
    # print(Point)
    # Create the rotation matrix #
    # Trans = np.array([[np.cos(-np.pi/4), -np.sin(-np.pi/4), 0, 5.66023622/2],[np.sin(-np.pi/4) , np.cos(-np.pi/4), 0, -4.98385827/2],[0,0,1,0],[0,0,0,1]])
    # Trans_inv = np.linalg.inv(Trans)
    # Point = np.append(Point,1)
    
    # Points = (Trans_inv@Point)
    # Change the point location relative to the offset #
    X = Point[0] - 5.66023622/2
    Y = Point[1] + 4.98385827/2
    Z = Point[2]
    

    
    
    # Link Lengths #
    Link1 = 3.8
    Link2 = 4.19
    Link3 = 4.67
    
    # Find the shoulder angle theta 1 #
    theta1 = np.arctan2(Y,X)+np.pi/4
    
    # Geometric variables for theta #
    r2 = np.abs((X)/(np.cos(theta1 - np.pi/4))) - Link1
    r1 = math.sqrt(Z**2 + r2**2)

 
    phi2 = np.arctan2(Z,r2)
    phi1 =  np.arccos((Link3**2 -Link2**2 -r1**2)/(-2* Link2 *r1))

    
    # Find angle 2 from the elbow #
    theta2 = phi1 + phi2
    
    phi3 = np.arccos( (r1**2 -Link2**2 -Link3**2)/(-2*Link3*Link2))
    
    # Find the final angle #
    theta3 = -(np.pi - phi3)
    
    
    return theta1,-theta2,-theta3



def inverse_kinematic_FL(Point):
    
    # print(Point)
    # Create the rotation matrix #
    # Trans = np.array([[np.cos(-np.pi/4), -np.sin(-np.pi/4), 0, 5.66023622/2],[np.sin(-np.pi/4) , np.cos(-np.pi/4), 0, -4.98385827/2],[0,0,1,0],[0,0,0,1]])
    # Trans_inv = np.linalg.inv(Trans)
    # Point = np.append(Point,1)
    
    # Points = (Trans_inv@Point)
    # Change the point location relative to the offset #
    X = Point[0] - 5.66023622/2
    Y = Point[1] - 4.98385827/2
    Z = Point[2]
    

    
    
    # Link Lengths #
    Link1 = 3.8
    Link2 = 4.19
    Link3 = 4.67
    
    # Find the shoulder angle theta 1 #
    theta1 = np.arctan2(Y,X)-np.pi/4
    
    # Geometric variables for theta #
    r2 = np.abs((X)/(np.cos(theta1 + np.pi/4))) - Link1
    r1 = math.sqrt(Z**2 + r2**2)

 
    phi2 = np.arctan2(Z,r2)
    phi1 =  np.arccos((Link3**2 -Link2**2 -r1**2)/(-2* Link2 *r1))

    
    # Find angle 2 from the elbow #
    theta2 = phi1 + phi2
    
    phi3 = np.arccos( (r1**2 -Link2**2 -Link3**2)/(-2*Link3*Link2))
    
    # Find the final angle #
    theta3 = -(np.pi - phi3)
    
    
    return theta1,-theta2,-theta3

def inverse_kinematic_RL(Point):
    
    # print(Point)
    # Create the rotation matrix #
    # Trans = np.array([[np.cos(-np.pi/4), -np.sin(-np.pi/4), 0, 5.66023622/2],[np.sin(-np.pi/4) , np.cos(-np.pi/4), 0, -4.98385827/2],[0,0,1,0],[0,0,0,1]])
    # Trans_inv = np.linalg.inv(Trans)
    # Point = np.append(Point,1)
    
    # Points = (Trans_inv@Point)
    # Change the point location relative to the offset #
    X = Point[0] + 5.66023622/2
    Y = Point[1] - 4.98385827/2
    Z = Point[2]
    

    
    
    # Link Lengths #
    Link1 = 3.8
    Link2 = 4.19
    Link3 = 4.67
    
    # Find the shoulder angle theta 1 #
    theta1 = np.arctan2(Y,X)-np.pi*3/4
    
    # Geometric variables for theta #
    r2 = np.abs((X)/(np.cos(theta1 +np.pi*3/4))) - Link1
    r1 = math.sqrt(Z**2 + r2**2)

 
    phi2 = np.arctan2(Z,r2)
    phi1 =  np.arccos((Link3**2 -Link2**2 -r1**2)/(-2* Link2 *r1))

    
    # Find angle 2 from the elbow #
    theta2 = phi1 + phi2
    
    phi3 = np.arccos( (r1**2 -Link2**2 -Link3**2)/(-2*Link3*Link2))
    
    # Find the final angle #
    theta3 = -(np.pi - phi3)
    
    
    return theta1,-theta2,-theta3



def inverse_kinematic_RR(Point):
    
    # print(Point)
    # Create the rotation matrix #
    # Trans = np.array([[np.cos(-np.pi/4), -np.sin(-np.pi/4), 0, 5.66023622/2],[np.sin(-np.pi/4) , np.cos(-np.pi/4), 0, -4.98385827/2],[0,0,1,0],[0,0,0,1]])
    # Trans_inv = np.linalg.inv(Trans)
    # Point = np.append(Point,1)
    
    # Points = (Trans_inv@Point)
    # Change the point location relative to the offset #
    X = Point[0] + 5.66023622/2
    Y = Point[1] + 4.98385827/2
    Z = Point[2]
    

    
    
    # Link Lengths #
    Link1 = 3.8
    Link2 = 4.19
    Link3 = 4.67
    
    # Find the shoulder angle theta 1 #
    theta1 = np.arctan2(Y,X)+np.pi*3/4
    
    # Geometric variables for theta #
    r2 = np.abs((X)/(np.cos(theta1 - np.pi*3/4))) - Link1
    r1 = math.sqrt(Z**2 + r2**2)

 
    phi2 = np.arctan2(Z,r2)
    phi1 =  np.arccos((Link3**2 -Link2**2 -r1**2)/(-2* Link2 *r1))

    
    # Find angle 2 from the elbow #
    theta2 = phi1 + phi2
    
    phi3 = np.arccos( (r1**2 -Link2**2 -Link3**2)/(-2*Link3*Link2))
    
    # Find the final angle #
    theta3 = -(np.pi - phi3)
    
    
    return theta1,-theta2,-theta3



    
# def plot_robot_V1(ax,theta_FR,theta_FL,theta_RR,theta_RL, holdFig, ShowPath, view_elev = 45,view_azim = 45):
#     # Set the link length #
#     Link_1 = np.array([[0, 0, 0],[3.8,0,0]])
    
#     Link_2 = np.array([[0, 0, 0], [4.19, 0, 0]])
    
#     Link_3 = np.array([[0,0,0], [3.67,0,.5], [04.67,0,0]])
    
#     # Create the base #
#     base = np.array([[5.66023622/2, -4.98385827/2, 0],[5.66023622/2,4.98385827/2,0],[-5.66023622/2,4.98385827/2,0],[-5.66023622/2,-4.98385827/2,0],[5.66023622/2,-4.98385827/2,0]])
        
#     # For plotting use ax.plot3D and adjustments use ax. for setting limits or title #
    
#     # plotting #
#     # fig = plt.figure()
#     # ax = plt.axes(projection='3d')
#     ax.plot3D(base[:,0],base[:,1],base[:,2])

#     # Set the axis names and range #
#     ax.set_xlabel('X-Axis')
#     ax.set_ylabel('Y-Axis')
#     ax.set_zlabel('Z-Axis')
    
#     View_min = -10
#     View_max = 10
    
#     ax.set_xlim(View_min,View_max)
#     ax.set_ylim(View_min,View_max)
#     ax.set_zlim(View_min,View_max)
    
    
#     # below will overwrite the vew angle, best to unuse or move outside this fcn.
#     #ax.view_init(elev=view_elev, azim=view_azim) # Set elevation and azimuth
    
#     ####################### Rear Right Points ########################
#     [Right_Rear_Points_1,Rz] = Right_Rear_Rotation_1_0( Link_1 , theta_RR[0])
#     [Right_Rear_Points_2,RzRy] = Rotation_2_0(Link_2, theta_RR[1], Rz,Link_1[1,0])
#     Right_Rear_Points_3 = Rotation_3_0(Link_3, theta_RR[2] ,RzRy,Link_2[1,0])
    
#     # Plot the Rotational Points #
#     ax.plot3D(Right_Rear_Points_1[:,0],Right_Rear_Points_1[:,1],Right_Rear_Points_1[:,2])
#     ax.plot3D(Right_Rear_Points_2[:,0],Right_Rear_Points_2[:,1],Right_Rear_Points_2[:,2])
#     ax.plot3D(Right_Rear_Points_3[:,0],Right_Rear_Points_3[:,1],Right_Rear_Points_3[:,2],'red')
    
    
    
#     ############################# Front Right Points #########################
#     [Right_Front_Points_1,Rz] = Right_Front_Rotation_1_0( Link_1 , theta_FR[0])
#     [Right_Front_Points_2,RzRy] = Rotation_2_0(Link_2,theta_FR[1], Rz,Link_1[1,0])
#     Right_Front_Points_3 = Rotation_3_0(Link_3,theta_FR[2],RzRy,Link_2[1,0])
    
#     # Plot the Rotational Points #
#     ax.plot3D(Right_Front_Points_1[:,0],Right_Front_Points_1[:,1],Right_Front_Points_1[:,2])
#     ax.plot3D(Right_Front_Points_2[:,0],Right_Front_Points_2[:,1],Right_Front_Points_2[:,2])
#     ax.plot3D(Right_Front_Points_3[:,0],Right_Front_Points_3[:,1],Right_Front_Points_3[:,2],'grey')
    
    
    
#     ############################### Rear Left Points #################################
#     [Left_Rear_Points_1,Rz] = Left_Rear_Rotation_1_0( Link_1 , theta_RL[0])
#     [Left_Rear_Points_2,RzRy] = Rotation_2_0(Link_2, theta_RL[1], Rz, Link_1[1,0])
#     Left_Rear_Points_3 = Rotation_3_0(Link_3, theta_RL[2],RzRy,Link_2[1,0])
    
#     # Plot the Rotational Points #
#     ax.plot3D(Left_Rear_Points_1[:,0],Left_Rear_Points_1[:,1],Left_Rear_Points_1[:,2])
#     ax.plot3D(Left_Rear_Points_2[:,0],Left_Rear_Points_2[:,1],Left_Rear_Points_2[:,2])
#     ax.plot3D(Left_Rear_Points_3[:,0],Left_Rear_Points_3[:,1],Left_Rear_Points_3[:,2],'blue')
    
    
#     ################################# Front Left Points ######################
#     [Left_Front_Points_1,Rz] = Left_Front_Rotation_1_0( Link_1 , theta_FL[0])
#     [Left_Front_Points_2,RzRy] = Rotation_2_0(Link_2, theta_FL[1], Rz,Link_1[1,0])
#     Left_Front_Points_3 = Rotation_3_0(Link_3, theta_FL[2] ,RzRy,Link_2[1,0])
    
#     # Plot the Rotational Points #
#     ax.plot3D(Left_Front_Points_1[:,0],Left_Front_Points_1[:,1],Left_Front_Points_1[:,2])
#     ax.plot3D(Left_Front_Points_2[:,0],Left_Front_Points_2[:,1],Left_Front_Points_2[:,2])
#     ax.plot3D(Left_Front_Points_3[:,0],Left_Front_Points_3[:,1],Left_Front_Points_3[:,2],'green')
      
    
#     [FL,FR,RL,RR] = walking_cycle(0)
    
#     if ShowPath: ## allows point toggling (better clarity)
#         ax.plot3D(FL[0,:],FL[1,:],FL[2,:],'.',markerfacecolor='none',color="darkgreen")
#         ax.plot3D(FR[0,:],FR[1,:],FR[2,:],'.',markerfacecolor='none',color="black")
#         ax.plot3D(RR[0,:],RR[1,:],RR[2,:],'.',markerfacecolor='none',color="DarkRed")
#         ax.plot3D(RL[0,:],RL[1,:],RL[2,:],'.',markerfacecolor='none',color="DarkBlue")

#     #plt.ion()
#     plt.show(block=holdFig)
#     #print("test")
#     #plt.show(block=False)  ## HOLY HECK A 100 WINDOWS
#     #plt.draw() # Neil: hopefully this wont recreate the figure.
#     #print(plt.fignum_exists(1)) # junk now, tests if figure is present? 1 is for "figure 1"
#     #plt.gcf()
#     # if not plt.fignum_exists(1):
#     #     plt.show(block=False)
#     # else:
#     #     plt.draw()
#     # return
