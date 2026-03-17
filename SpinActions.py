import numpy as np
import matplotlib.pyplot as plt
from time import time
from Inverse_Kinematics import inverse_kinematic_FR, inverse_kinematic_FL, inverse_kinematic_RL, inverse_kinematic_RR
from Rotations import Right_Rear_Rotation_1_0, Right_Front_Rotation_1_0, Left_Rear_Rotation_1_0, Left_Front_Rotation_1_0, Rotation_2_0, Rotation_3_0


# started coding around  7:00pm 3/16/2026

# only need to run below once:
# creates fixed rotated paths
def Spin_cycle():
    ####### Create parameters #########
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
    P2 = np.array([1, S+(2*A)]) # made 0->0.5 for counting points.
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

def plot_robot_spins(ax,theta_FR,theta_FL,theta_RR,theta_RL, view_elev = 45,view_azim = 45):
    # Set the link length #
    Link_1 = np.array([[0, 0, 0],[3.8,0,0]])
    Link_2 = np.array([[0, 0, 0], [4.19, 0, 0]])
    Link_3 = np.array([[0,0,0], [3.67,0,.5], [04.67,0,0]])
    
    # Create the base #
    base = np.array([[5.66023622/2, -4.98385827/2, 0],[5.66023622/2,4.98385827/2,0],[-5.66023622/2,4.98385827/2,0],[-5.66023622/2,-4.98385827/2,0],[5.66023622/2,-4.98385827/2,0]])
    ax.plot3D(base[:,0],base[:,1],base[:,2])

    # # Set the axis names and range #
    # ax.set_xlabel('X-Axis')
    # ax.set_ylabel('Y-Axis')
    # ax.set_zlabel('Z-Axis')
    
    # View_min = -10
    # View_max = 10
    
    # ax.set_xlim(View_min,View_max)
    # ax.set_ylim(View_min,View_max)
    # ax.set_zlim(View_min,View_max)

    # below will overwrite the vew angle, best to unuse or move outside this fcn.
    #ax.view_init(elev=view_elev, azim=view_azim) # Set elevation and azimuth
    
    ####################### Rear Right Points ########################
    [Right_Rear_Points_1,Rz] = Right_Rear_Rotation_1_0( Link_1 , theta_RR[0])
    [Right_Rear_Points_2,RzRy] = Rotation_2_0(Link_2, theta_RR[1], Rz,Link_1[1,0])
    Right_Rear_Points_3 = Rotation_3_0(Link_3, theta_RR[2] ,RzRy,Link_2[1,0])
    
    # Plot the Rotational Points #
    ax.plot3D(Right_Rear_Points_1[:,0],Right_Rear_Points_1[:,1],Right_Rear_Points_1[:,2])
    ax.plot3D(Right_Rear_Points_2[:,0],Right_Rear_Points_2[:,1],Right_Rear_Points_2[:,2])
    ax.plot3D(Right_Rear_Points_3[:,0],Right_Rear_Points_3[:,1],Right_Rear_Points_3[:,2],'red')
    
    
    
    ############################# Front Right Points #########################
    [Right_Front_Points_1,Rz] = Right_Front_Rotation_1_0( Link_1 , theta_FR[0])
    [Right_Front_Points_2,RzRy] = Rotation_2_0(Link_2,theta_FR[1], Rz,Link_1[1,0])
    Right_Front_Points_3 = Rotation_3_0(Link_3,theta_FR[2],RzRy,Link_2[1,0])
    
    # Plot the Rotational Points #
    ax.plot3D(Right_Front_Points_1[:,0],Right_Front_Points_1[:,1],Right_Front_Points_1[:,2])
    ax.plot3D(Right_Front_Points_2[:,0],Right_Front_Points_2[:,1],Right_Front_Points_2[:,2])
    ax.plot3D(Right_Front_Points_3[:,0],Right_Front_Points_3[:,1],Right_Front_Points_3[:,2],'grey')
    
    
    
    ############################### Rear Left Points #################################
    [Left_Rear_Points_1,Rz] = Left_Rear_Rotation_1_0( Link_1 , theta_RL[0])
    [Left_Rear_Points_2,RzRy] = Rotation_2_0(Link_2, theta_RL[1], Rz, Link_1[1,0])
    Left_Rear_Points_3 = Rotation_3_0(Link_3, theta_RL[2],RzRy,Link_2[1,0])
    
    # Plot the Rotational Points #
    ax.plot3D(Left_Rear_Points_1[:,0],Left_Rear_Points_1[:,1],Left_Rear_Points_1[:,2])
    ax.plot3D(Left_Rear_Points_2[:,0],Left_Rear_Points_2[:,1],Left_Rear_Points_2[:,2])
    ax.plot3D(Left_Rear_Points_3[:,0],Left_Rear_Points_3[:,1],Left_Rear_Points_3[:,2],'blue')
    
    
    ################################# Front Left Points ######################
    [Left_Front_Points_1,Rz] = Left_Front_Rotation_1_0( Link_1 , theta_FL[0])
    [Left_Front_Points_2,RzRy] = Rotation_2_0(Link_2, theta_FL[1], Rz,Link_1[1,0])
    Left_Front_Points_3 = Rotation_3_0(Link_3, theta_FL[2] ,RzRy,Link_2[1,0])
    
    # Plot the Rotational Points #
    ax.plot3D(Left_Front_Points_1[:,0],Left_Front_Points_1[:,1],Left_Front_Points_1[:,2])
    ax.plot3D(Left_Front_Points_2[:,0],Left_Front_Points_2[:,1],Left_Front_Points_2[:,2])
    ax.plot3D(Left_Front_Points_3[:,0],Left_Front_Points_3[:,1],Left_Front_Points_3[:,2],'green')

def GraphFinisher(ax):
    # Set the axis names and range #
    # need to rerun thisevery frame for some reason (WHY WONT IT SAVE SETTING, UPDATE DONT RECREATE)
    ax.set_xlabel('X-Axis')
    ax.set_ylabel('Y-Axis')
    ax.set_zlabel('Z-Axis')

    View_min = -10
    View_max = 10

    ax.set_xlim(View_min,View_max)
    ax.set_ylim(View_min,View_max)
    ax.set_zlim(View_min,View_max)
    plt.show(block=False)



# just testing code

[FL,FR,RL,RR] = Spin_cycle()

#fig = plt.ion()
fig = plt.figure()  # brought out here.
ax = plt.axes(projection='3d')



# Pull the points from the walking cycle #
Points_FL = FL[0:3,:].T
Points_FR = FR[0:3,:].T
Points_RL = RL[0:3,:].T
Points_RR = RR[0:3,:].T
# throwing this here
total_pts = 20   # total path points, here to avoid out of bounds indexing
T_start = time() # start time
T_now = time()   # current time tracker
T_duration =  30 # seconds
T_pause = 0.25    # time between each point, funtionally the period. 
T_lastP = time() # like T_now but for steps
i = 0              # our ticker


while T_now <= (T_start + T_duration):
    T_now = time()  # update time

    theta_FL = inverse_kinematic_FL(Points_FL[(15 + i) % total_pts,:]) 
    theta_FR = inverse_kinematic_FR(Points_FR[(5 + i) % total_pts,:])
    theta_RL = inverse_kinematic_RL(Points_RL[(10 + i) % total_pts,:])
    theta_RR = inverse_kinematic_RR(Points_RR[(0 + i) % total_pts,:])
    # plot the robot with leg theta values (for when we send off to real robot?)
    plot_robot_spins(ax,theta_FR,theta_FL,theta_RR,theta_RL)

    
    # Triange plotting code:
    tri = [(Points_FL[(15 + i) % total_pts,:]), (Points_FR[(5 + i) % total_pts,:]),(Points_RL[(10 + i) % total_pts,:]),(Points_RR[(0 + i) % total_pts,:])]
    triout = [0,0,0,0] #hopefully  declaration saves computation time
    i2 = 0
    for x in tri:   #grabs points on ground and chucks into array
        if x[2] < -7.62:
            triout[i2] = x
            i2 = i2 + 1
            triout[3] = triout[0]
    trix = [triout[0][0],triout[1][0],triout[2][0],triout[3][0]]
    triy = [triout[0][1],triout[1][1],triout[2][1],triout[3][1]]
    triz = [triout[0][2],triout[1][2],triout[2][2],triout[3][2]]
    ax.plot3D(trix,triy,triz,'red')

    i = (i + 1) % total_pts          # iterate because ye

    # plot points # (put here becausr ax.clear() keeps erasing)
    ax.plot3D(FL[0,:],FL[1,:],FL[2,:],'.',markerfacecolor='none',color="darkgreen")
    ax.plot3D(FR[0,:],FR[1,:],FR[2,:],'.',markerfacecolor='none',color="black")
    ax.plot3D(RR[0,:],RR[1,:],RR[2,:],'.',markerfacecolor='none',color="DarkRed")
    ax.plot3D(RL[0,:],RL[1,:],RL[2,:],'.',markerfacecolor='none',color="DarkBlue")
    GraphFinisher(ax)
    plt.pause(0.1)         # needed for grapher to graph. Currently controls speedof rotation
    ax.clear()             # so doesnt overlap itself
