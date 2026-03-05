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


import rclpy
from rclpy.node import Node
from rclpy.duration import Duration
from rclpy.qos import QoSProfile, DurabilityPolicy, ReliabilityPolicy
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from std_msgs.msg import String

from math import pi
import kdl_wrapper as kdl

class JointTrajectoryPublisher(Node):
    def __init__(self):
        super().__init__('joint_trajectory_publisher')

        # Create Subscriptions
        qos_profile = QoSProfile(
            depth=1,
            durability=DurabilityPolicy.TRANSIENT_LOCAL,
            reliability=ReliabilityPolicy.RELIABLE
        )
        self.subscription_ = self.create_subscription(
            String,
            '/robot_description',
            self.urdf_callback,
            qos_profile
        )

        # Create Publishers
        publisher1_ = self.create_publisher(
            JointTrajectory, 
            '/joint_trajectory_controller_1/joint_trajectory', 
            10)
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
        self.jtc_publishers = {1: publisher1_,
                               2: publisher2_,
                               3: publisher3_,
                               4: publisher4_} 

        self.duration_step = 1.5
        self.timer_ = self.create_timer(self.duration_step*15, self.publish_trajectory)
        self.get_logger().info('Joint trajectory publisher started!')

    def urdf_callback(self, msg: JointTrajectory):
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
                names = get_joint_names(chain)
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
    
    def publish_trajectory(self):
        self.get_logger().info('publish_trajectory')

        ## Create the JointTrajectory message
        msg = JointTrajectory()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'base_link'
        # msg.joint_names = self.chain_names[1]

        ## Create trajectory point
        point_array = [
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
        point_duration = 0.0

        ## Append points to trajectory
        for points in point_array:
            point = JointTrajectoryPoint()
            point.positions = points
            point.time_from_start = Duration(seconds=point_duration).to_msg()
            point_duration += self.duration_step
            
            msg.points.append(point)

        
        ## Publish JointTrajectory message
        for i in range(1, 4+1):
            msg.joint_names = self.chain_names[i]
            self.jtc_publishers[i].publish(msg)
            self.get_logger().info(f'Published joint trajectory to controller {i}. Points: {len(msg.points)}')

def get_joint_names(chain):
    joint_names = []
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




def main():
    rclpy.init()
    node = JointTrajectoryPublisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
