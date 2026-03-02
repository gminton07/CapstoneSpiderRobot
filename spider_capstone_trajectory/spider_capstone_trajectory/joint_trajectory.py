#!/usr/bin/env python3

#TODO: Explore PyKDL for dynamically getting robot Tree & Chain from URDF
#       
#      kdl_parser
#       C++ native services --> C++ wrapper
# 

import rclpy
from rclpy.node import Node
from rclpy.duration import Duration
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from std_msgs.msg import String

from math import pi
import kdl_wrapper as kdl

class JointTrajectoryPublisher(Node):
    def __init__(self):
        super().__init__('joint_trajectory_publisher')

        self.subscription_ = self.create_subscription(
            String,
            '/robot_description',
            self.urdf_callback,
            10
        )
        self.publisher_ = self.create_publisher(JointTrajectory, '/joint_trajectory_controller_1/joint_trajectory', 10)
        self.timer_ = self.create_timer(15.0, self.publish_trajectory)
        self.get_logger().info('Joint trajectory publisher started!')

    def urdf_callback(self, msg):
        try:
            tree = kdl.tree_from_xml(msg.data)
            self.get_logger().info(f'Tree created with {tree.getNrOfSegments()}')

            base_link = 'base_link'
            tip_link = 'fr_end_effector'

            chain = tree.getChain(base_link, tip_link)

            num_joints = chain.getNrOfJoints()
            self.get_logger().info(f"Chain extracted from {base_link} to {tip_link}")
            self.get_logger().info(f"Number of joints in chain: {num_joints}")

            # Export chain to class variable
            self.chain1 = chain

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
        point_duration = 1.0

        ## Append points to trajectory
        for points in point_array:
            point = JointTrajectoryPoint()
            point.positions = points
            point.time_from_start = Duration(seconds=point_duration).to_msg()
            point_duration += 1
            
            msg.points.append(point)

        
        ## Publish JointTrajectory message
        self.publisher_.publish(msg)
        self.get_logger().info(f'Published joint trajectory. Points: {len(msg.points)}')

def main():
    rclpy.init()
    node = JointTrajectoryPublisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()