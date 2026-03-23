#!/usr/bin/env python3

# TODO: Create chains for all 4 legs
#       Export the active (mobile) joint names with:
#       get_joint_names(chain)
#
#       Actually use Chain -> joint_names in the script
#
#       Explore PyKDL for dynamically getting robot Tree & Chain from URDF
#           kdl_parser
#           C++ native services --> C++ wrapper
# 

# packages to make it work
import rclpy
from rclpy.node import Node
from rclpy.duration import Duration
from rclpy.qos import QoSProfile, DurabilityPolicy, ReliabilityPolicy
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from std_msgs.msg import String

from math import pi
import kdl_wrapper as kdl

from .Inverse_Kinematics import inverse_kinematic_FR, inverse_kinematic_FL, inverse_kinematic_RL, inverse_kinematic_RR
from .Rotations import walking_cycle
import numpy as np

class JointTrajectoryPublisher(Node): # nodes are class objects, what defines it
    def __init__(self): # when create class, automatically runs on class creation
        super().__init__('BigSteppy')

        # Create Subscriptions
        qos_profile = QoSProfile( #for getting xml string (robot description, recall from robotics class we used it for part 1)
            depth=1, #how deep in array
            durability=DurabilityPolicy.TRANSIENT_LOCAL, # rrquired but neil (moi) shouldnt mess with it.
            reliability=ReliabilityPolicy.RELIABLE
        )
        self.subscription_ = self.create_subscription( # sets up messaging
            String,                                    # message type
            '/robot_description',                      # topic name
            self.urdf_callback,                        # function to run when you recieve message
            qos_profile                                # just runs (ignore but still needed)
        )

        # Create Publishers
        publisher1_ = self.create_publisher(
            JointTrajectory,                                    #msg type
            '/joint_trajectory_controller_1/joint_trajectory',  #topic name
            10)                                                 #depth (qos depth related thingy)
        publisher2_ = self.create_publisher(
            JointTrajectory, 
            '/joint_trajectory_controller_2/joint_trajectory', 
            10)
        publisher3_ = self.create_publisher(
            JointTrajectory, 
            '/joint_trajectory_controller_3/joint_trajectory', 
            10)
        publisher4_ = self.create_publisher(
            JointTrajectory, 
            '/joint_trajectory_controller_4/joint_trajectory', 
            10)
        self.jtc_publishers = {1: publisher1_, # for each leg, compiled here into neat dictionary
                               2: publisher2_, # these were declared above, 
                               3: publisher3_, # so we can easily loop through them
                               4: publisher4_} 

        self.duration_step = .1  # how long each step should take, 
        self.timer_ = self.create_timer(self.duration_step*21, self.publish_trajectory) # makes timer, for timing actions. 15 default
        self.get_logger().info('Joint trajectory publisher started!')                   # try number of points?

        self.point_4Leg_array = self.create_angle_array() #creates the path. Here it only creates 1 and reuses it.

    def urdf_callback(self, msg: JointTrajectory): #extracts names of joints from urdf tree.
        '''
        Create the Chain and extract mobile joint names for each leg
        '''

        try:
            self.tree = kdl.tree_from_xml(msg.data)
            self.get_logger().info(f'Tree created with {self.tree.getNrOfSegments()} segments')

            base_link = 'base_link'
            tip_link = 'fr_end_effector'
            tip_link = ['fr_end_effector', 'fl_end_effector', 'bl_end_effector', 'br_end_effector']

            self.chains = {}
            self.chain_names = {}

            for i in range(0,4):
                chain = self.tree.getChain(base_link, tip_link[i])

                num_joints = chain.getNrOfJoints()
                self.get_logger().info(f"Chain extracted from {base_link} to {tip_link[i]}")
                self.get_logger().info(f"Number of joints in chain: {num_joints}")

                # Get names of mobile joints
                names = get_joint_names(chain) # function is down below
                self.get_logger().info(f"Active joints in chain: {names}")

                # Add to chains dict
                self.chains[i+1] = chain
                self.chain_names[i+1] = names

            # self.chain = self.tree.getChain(base_link, tip_link)

            # num_joints = self.chain.getNrOfJoints()
            # self.get_logger().info(f"Chain extracted from {base_link} to {tip_link}")
            # self.get_logger().info(f"Number of joints in chain: {num_joints}")

            ## Get names of mobile joints
            #names = get_joint_names(self.chain)
            #self.get_logger().info(f"Active joints in chain: {names}")

            # Stop listening after data received
            self.destroy_subscription(self.subscription_)

            # You can now use this 'chain' object for dynamics!
            
        except Exception as e:
            self.get_logger().error(f"Failed to setup KDL: {str(e)}")
    

    def create_angle_array(self):
        [FL,FR,BL,BR] = walking_cycle(0) #create point loop with correct offset for each leg

        # Pull the points from the walking cycle #
        Points_FL = FL[0:3,:].T  # I believe this this strips off the extra 1?
        Points_FR = FR[0:3,:].T
        Points_BL = BL[0:3,:].T
        Points_BR = BR[0:3,:].T

        total_pts = 20 #number of points in a path, currently hardcoded. Needed for calibration reasons below.
        point_array_FL = []
        point_array_FR = []
        point_array_BL = []
        point_array_BR = []
        for i in range(total_pts):
            theta_FL = inverse_kinematic_FL(Points_FL[(15 + i) % total_pts,:]) 
            theta_FR = inverse_kinematic_FR(Points_FR[(5 + i) % total_pts,:])
            theta_BL = inverse_kinematic_RL(Points_BL[(10 + i) % total_pts,:])
            theta_BR = inverse_kinematic_RR(Points_BR[(0 + i) % total_pts,:])
            point_array_FL.append(theta_FL)
            point_array_FR.append(theta_FR)
            point_array_BL.append(theta_BL)
            point_array_BR.append(theta_BR)
            
        return {1: point_array_FR, 2: point_array_FL, 3: point_array_BL, 4: point_array_BR}

    def publish_trajectory(self):
        self.get_logger().info('publish_trajectory') # send logger message (shows up in terminal for debugging)
                        # logger means print to consol here
        ## Create the JointTrajectory message
        msg_FR = JointTrajectory() 
        msg_FL = JointTrajectory() 
        msg_BL = JointTrajectory() 
        msg_BR = JointTrajectory() # creates an object of jointTrajectory Message type
        msg = {1: msg_FR, 2: msg_FL, 3: msg_BL, 4: msg_BR} #array became disctonary :D
        
        for i in msg: # honest no clue whatthis is for, does not crash if I comment it out.
            msg[i].header.stamp = self.get_clock().now().to_msg() # timestamps message
            msg[i].header.frame_id = 'base_link' # its an id, has to be here
            #print("test",i)
        # msg[1].header.stamp = self.get_clock().now().to_msg() # timestamps message
        # msg[1].header.frame_id = 'base_link' # its an id, has to be here
        # msg[2].header.stamp = self.get_clock().now().to_msg() # timestamps message
        # msg[2].header.frame_id = 'base_link' # its an id, has to be here
        # msg[3].header.stamp = self.get_clock().now().to_msg() # timestamps message
        # msg[3].header.frame_id = 'base_link' # its an id, has to be here


        ## Create trajectory point
        point_array = [ # custom path made of angles 
            [0.0, 0.0, 0.0],
            [pi/2, 0.0, 0.0],
            [0.0, 0.0, 0.0],
            [-pi/2, 0.0, 0.0],
            [0.0, 0.0, 0.0],
            [0.0, pi/2, 0.0],
            [0.0, 0.0, 0.0],
            [0.0, -pi/2, 0.0],
            [0.0, 0.0, 0.0],
            [0.0, 0.0, pi/2],
            [0.0, 0.0, 0.0],
            [0.0, 0.0, -pi/2],
            [0.0, 0.0, 0.0],
        ]

        point_duration = 0.0 # 3 angles, duragtion. This tells how long travel time should take. (we guess this)
        # functionally does wha tpause(.01) does but properly. 

        ## Append points to trajectory
        for j in range(1, 4+1):
            #msg.points = [] # resets points so messages dont contaminate each other
            for points in self.point_4Leg_array[j]: #point_array: # only runs once, part of set up. (packages each point for message sendoff)
                point = JointTrajectoryPoint()  ## note/\ every other array index starts at 1 (why?), the j-1 is because point_4leg_array starts at 0
                point.positions = points
                point.time_from_start = Duration(seconds=point_duration).to_msg() #adds how much time it takes to get to point.
                point_duration += self.duration_step

                msg[j].points.append(point) #adds points to end of message, msg gets overwritten every time.

            ## Publish JointTrajectory message, idex notes: 1 is FR, 2>FL, 3>BL, 4>BR
            #for i in range(1, 4+1): # loop takes joint names (stored chain names)
            msg[j].joint_names = self.chain_names[j] # for like angle 1 gets asssigned to joint *_sholder and such.
            self.jtc_publishers[j].publish(msg[j]) # what sends out the message neil added i here.
            self.get_logger().info(f'Published joint trajectory to controller {j}. Points: {len(msg[j].points)}')



def get_joint_names(chain): #kdl wrapper library (kinmatics and dynamics)
    joint_names = []        # just gets names of MOVEABLE joints
    # Loop through every segment in the chain
    for i in range(chain.getNrOfSegments()):
        segment = chain.getSegment(i)
        joint = segment.getJoint()
        
        # KDL::Joint::None represents a fixed connection (0 DOF)
        # We usually only want 'Revolute' or 'Prismatic' joints
        if joint.getTypeName() not in ["None", "Fixed"]:
            joint_names.append(joint.getName())
            #print(f'{joint.getName()}: {joint.getTypeName()}')
            
    return joint_names

# NOTE: This section gets current robot state from /joint_states topic
#       and saves into JntArray object
#       Available if we want to integrate feedback loops
# 
# TODO: If using this section:
#       Add subscriber to /joint_states, using
#       sync_joint_state as the Callback function
#
# from sensor_msgs.msg import JointState
#
# def sync_joint_state(self, msg: JointState):
#     """Maps incoming ROS JointState to a KDL JntArray in the correct order."""
    
#     # 1. Get the names of the moving joints in our specific chain
#     # (Assuming you stored self.chain_joint_names during URDF parsing)
#     kdl_names = self.chain_joint_names 
    
#     # 2. Create a JntArray of the correct size
#     jnt_pos = kdl_wrapper.JntArray(len(kdl_names))
    
#     # 3. Create a mapping for quick lookup: { "joint_name": position_value }
#     ros_pos_map = dict(zip(msg.name, msg.position))
    
#     # 4. Fill the JntArray in the order KDL expects
#     for i, name in enumerate(kdl_names):
#         if name in ros_pos_map:
#             jnt_pos[i] = ros_pos_map[name]
#         else:
#             self.get_logger().warn(f"Joint {name} not found in JointState message!")
    
#     return jnt_pos




def main(): # makes object and spins up node
    rclpy.init()
    node = JointTrajectoryPublisher() # 
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
