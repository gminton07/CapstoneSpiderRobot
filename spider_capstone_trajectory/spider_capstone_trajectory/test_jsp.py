#!/usr/bin/env python3
# Adapted from:
# https://docs.ros.org/en/jazzy/Tutorials/Intermediate/URDF/Using-URDF-with-Robot-State-Publisher-py.html#publish-the-state

from math import sin, cos, pi
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile
from geometry_msgs.msg import Quaternion
from sensor_msgs.msg import JointState
from tf2_ros import TransformBroadcaster, TransformStamped

class StatePublisher(Node):

    def __init__(self):
        rclpy.init()
        super().__init__('state_publisher')

        # Set QoS and publishers
        qos_profile = QoSProfile(depth=10)
        self.joint_pub = self.create_publisher(JointState, 'joint_states', qos_profile)
        self.broadcaster = TransformBroadcaster(self, qos=qos_profile)
        self.nodeName = self.get_name()
        self.get_logger().info("{0} started".format(self.nodeName))
 
        step = pi/100
        loop_rate = self.create_rate(30)

        # Robot state
        shoulder_angle = 0.
        shoulder = cos(shoulder_angle) * pi/2
        elbow_angle = 0.
        elbow = sin(elbow_angle) * pi/2
        wrist_angle = 0.
        wrist = 0.

        # Message declarations
        odom_trans = TransformStamped()
        odom_trans.header.frame_id = 'odom'
        odom_trans.child_frame_id = 'base_link'
        joint_state = JointState()
        joint_state.name = ['shoulder', 'elbow', 'wrist']

        try:
            while rclpy.ok():
                rclpy.spin_once(self)

                # Update joint states
                now = self.get_clock().now()
                joint_state.header.stamp = now.to_msg()
                joint_state.position = [shoulder, elbow, wrist]

                # Update transform
                # Moving forward
                odom_trans.header.stamp = now.to_msg()
                odom_trans.transform.translation.x = 0.
                odom_trans.transform.translation.y = 0.
                odom_trans.transform.translation.z = 0.
                odom_trans.transform.rotation = \
                    euler_to_quaternion(0, 0, 0)

                # Send joint state & transform
                self.joint_pub.publish(joint_state)
                self.broadcaster.sendTransform(odom_trans)

                # Compute new state
                shoulder_angle += step
                shoulder = cos(shoulder_angle) * pi/2
                elbow_angle += step
                elbow = sin(shoulder_angle) * pi/2

                # Wait until needed each iteration
                loop_rate.sleep()

        except KeyboardInterrupt:
            pass


def euler_to_quaternion(roll, pitch, yaw):
    qx = sin(roll/2) * cos(pitch/2) * cos(yaw/2) - cos(roll/2) * sin(pitch/2) * sin(yaw/2)
    qy = cos(roll/2) * sin(pitch/2) * cos(yaw/2) + sin(roll/2) * cos(pitch/2) * sin(yaw/2)
    qz = cos(roll/2) * cos(pitch/2) * sin(yaw/2) - sin(roll/2) * sin(pitch/2) * cos(yaw/2)
    qw = cos(roll/2) * cos(pitch/2) * cos(yaw/2) + sin(roll/2) * sin(pitch/2) * sin(yaw/2)
    return Quaternion(x=qx, y=qy, z=qz, w=qw)

def main():
    node = StatePublisher()

if __name__ == '__main__':
    main()
