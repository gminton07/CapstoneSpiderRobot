import rclpy
from rclpy.node import Node
from visualization_msgs.msg import Marker
from geometry_msgs.msg import Point
import math
import numpy as np


class LegWorkspaceNode(Node):

    def __init__(self):
        super().__init__('leg_workspace_node')

        self.publisher = self.create_publisher(
                Marker,
                'leg_workspace',
                10
        )

        self.timer = self.create_timer(1.0, self.publish_workspace)

        self.frame_id = 'base_link'
        
        # Leg base frames
        self.legs = {'leg1': 'arm',
                     #'front_left': 'fl_hip_link'
        }

    
    def publish_workspace(self):
        marker_id = 0

        for leg_name, frame in self.legs.items():
            marker = Marker()
            marker.header.frame_id = frame
            marker.header.stamp = self.get_clock().now().to_msg()
            marker.ns = 'leg_workspace'
            marker.id = marker_id
            marker_id += 1

            marker.type = Marker.POINTS
            marker.action = Marker.ADD

            marker.scale.x = 0.005
            marker.scale.y = 0.005

            marker.color.r = 0.5
            marker.color.g = 0.8
            marker.color.b = 0.2
            marker.color.a = 0.8

            marker.pose.position.x = 0.0
            marker.pose.position.y = 0.0
            marker.pose.position.z = 0.0
            marker.pose.orientation.w = 1.0

            marker.lifetime.sec = 0

            marker.points = []

            for q1 in self.frange(-math.pi/2, math.pi/2, 0.05):
                for q2 in self.frange(-math.pi/2, math.pi/2, 0.05):
                    x, y, z = self.fk(q1, q2)
                    p = Point(x=x, y=y, z=z)
                    #print(f'{x = } {y = } {z = } {q1 = } {q2 = }')
                    marker.points.append(p)

            self.publisher.publish(marker)
            self.get_logger().info(f'Publishing {len(marker.points)} points for {leg_name}')

    def rot_z(self, theta):
        c, s = math.cos(theta), math.sin(theta)
        return np.array([
            [ c, -s,  0, 0],
            [ s,  c,  0, 0],
            [ 0,  0,  1, 0],
            [ 0,  0,  0, 1],
        ])

    def rot_y(self, theta):
        c, s = math.cos(theta), math.sin(theta)
        return np.array([
            [ c,  0,  s, 0],
            [ 0,  1,  0, 0],
            [-s,  0,  c, 0],
            [ 0,  0,  0, 1],
        ])

    def trans_x(self, d):
        return np.array([
            [1, 0, 0, d],
            [0, 1, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1],
        ])

    def fk(self, q1, q2):
        L1 = 0.05
        L2 = 0.15

        T = (
            self.rot_z(q1) @
            self.trans_x(L1) @
            self.rot_y(q2) @
            self.trans_x(L2)
        )

        pos = T[:3, 3]
        return pos


    """
    def fk(self, q1, q2):
        (c1, c2) = (math.cos(q1), math.cos(q2))
        (s1, s2) = (math.sin(q1), math.sin(q2))
        c1, s1 = math.cos(q1), math.sin(q1)
        c2, s2 = math.cos(q2), math.sin(q2)
        arm_len = 0.05
        forearm_len = 0.15

        trans_1_2 = np.array(np.asmatrix(f'{c1} 0 {s1} {arm_len};  {-s1} 0 {c1} 0;  0 0 1 0;  0 0 0 1'))
        trans_2_3 = np.array(np.asmatrix(f'{c2} {-s2} 0 {forearm_len};  {s2} {c2} 0 0;  0 0 1 0;  0 0 0 1'))
        
        trans_1_3 = trans_1_2 @ trans_2_3

        return trans_1_3[:3, 3]
    """


    def frange(self, start, stop, step):
        while start <= stop:
            yield start
            start += step


def main():
    rclpy.init()
    node = LegWorkspaceNode()
    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()
