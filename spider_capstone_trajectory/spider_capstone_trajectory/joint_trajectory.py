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
        self.publisher_ = self.create_publisher(JointTrajectory, '/joint_trajectory_controller_1/joint_trajectory', 10)
        self.timer_ = self.create_timer(30.0, self.publish_trajectory)
        self.get_logger().info('Joint trajectory publisher started!')

    def urdf_callback(self, msg: JointTrajectory):
        try:
            self.tree = kdl.tree_from_xml(msg.data)
            self.get_logger().info(f'Tree created with {self.tree.getNrOfSegments()} segments')

            base_link = 'base_link'
            tip_link = 'fr_end_effector'

            self.chain = self.tree.getChain(base_link, tip_link)

            num_joints = self.chain.getNrOfJoints()
            self.get_logger().info(f"Chain extracted from {base_link} to {tip_link}")
            self.get_logger().info(f"Number of joints in chain: {num_joints}")

            # Get names of mobile joints
            names = get_joint_names(self.chain)
            self.get_logger().info(f"Active joints in chain: {names}")

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
        #####TODO: update to PyKDL and kdl_parser
        msg.header.frame_id = 'base_link'
        msg.joint_names = ['fr_shoulder', 'fr_elbow', 'fr_wrist']
        #####

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
            point_duration += 2
            
            msg.points.append(point)

        
        ## Publish JointTrajectory message
        self.publisher_.publish(msg)
        self.get_logger().info(f'Published joint trajectory. Points: {len(msg.points)}')

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
            print(f'{joint.getName()}: {joint.getTypeName()}')
            
    return joint_names

# NOTE: This section gets current robot state from /joint_states topic
#       and saves into JntArray object
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