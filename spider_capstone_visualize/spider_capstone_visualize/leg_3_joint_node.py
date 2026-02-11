import rclpy
from rclpy.node import Node
from visualization_msgs.msg import Marker
from geometry_msgs.msg import Point
import math
import numpy as np
from scipy.spatial import ConvexHull


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
        self.show_4_legs = False
        if self.show_4_legs:
            self.legs = {'front_right': 'fr_shoulder_base',
                         'front_left': 'fl_shoulder_base',
                         'back_right': 'br_shoulder_base',
                         'back_left': 'bl_shoulder_base',
                         #'front_left': 'fl_hip_link'
            }
        else:
            self.legs = {'base': 'shoulder_base'}
        
    
    def publish_workspace(self):
        marker_id = 0

        for leg_name, frame in self.legs.items():
            self.get_logger().info(f"{marker_id = } {leg_name = } {frame = }")
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

            # Change colors for each leg's point cloud
            if self.show_4_legs:
                marker.color.r = 1.0 if marker.id==0 else 0.2
                marker.color.g = 1.0 if marker.id==1 else 0.2
                marker.color.b = 1.0 if marker.id==2 else 0.2
                marker.color.a = 0.3
            if not self.show_4_legs:
                print(f'{self.show_4_legs}')
                marker.color.r = 0.4
                marker.color.g = 1.0
                marker.color.b = 0.0
                marker.color.a = 0.8
                

            marker.pose.position.x = 0.0
            marker.pose.position.y = 0.0
            marker.pose.position.z = 0.0
            marker.pose.orientation.w = 1.0

            marker.lifetime.sec = 0

            marker.points = []

            for q1 in self.frange(-math.pi/2, math.pi/2, 0.2):
                for q2 in self.frange(-math.pi/2, math.pi/2, 0.2):
                    for q3 in self.frange(-math.pi/2, math.pi/2, 0.2):
                        x, y, z = self.fk(q1, q2, q3)
                        p = Point(x=x, y=y, z=z)
                        if z <= -0.06:
                            #print(f'{x = } {y = } {z = } {q1 = } {q2 = } {q3 = }')
                            marker.points.append(p)

            #marker = self.points_to_mesh(marker.points, marker.header.frame_id, marker.id)
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
            [ c,  0,  s, 0],            [ 0,  1,  0, 0],
            [-s,  0,  c, 0],
            [ 0,  0,  0, 1],
        ])

    def trans_xyz(self, d:list[int]):
        return np.array([
            [1, 0, 0, d[0]],
            [0, 1, 0, d[1]],
            [0, 0, 1, d[2]],
            [0, 0, 0, 1],
        ])

    def points_to_mesh(self, points, frame_id, marker_id):
        pts = np.array([[p.x, p.y, p.z] for p in points])

        hull = ConvexHull(pts)

        marker = Marker()
        marker.header.frame_id = frame_id
        marker.header.stamp = self.get_clock().now().to_msg()
        marker.ns = 'leg_workspace'
        marker.id = marker_id
        marker.type = Marker.TRIANGLE_LIST
        marker.action = Marker.ADD

        marker.pose.orientation.w = 1.0

        marker.scale.x = 1.0
        marker.scale.y = 1.0
        marker.scale.z = 1.0
        
        #marker.color.r = 0.2
        #marker.color.g = 0.6
        #marker.color.b = 1.0
        #marker.color.a = 0.3

        # Change colors for each leg's point cloud
        marker.color.r = 1.0 if marker.id==0 else 0.2
        marker.color.g = 1.0 if marker.id==1 else 0.2
        marker.color.b = 1.0 if marker.id==2 else 0.2
        marker.color.a = 0.6

        marker.points = []

        for simplex in hull.simplices:
            for idx in simplex:
                x, y, z = pts[idx]
                marker.points.append(Point(x=x, y=y, z=z))

        return marker


    def fk(self, q1, q2, q3):

        # np.array(np.asmatrix())
        # shoulder to Link1            
        trans_1_2 = self.trans_xyz([0.07, 0, 0.04])
        # Link1 to Link2               
        trans_2_3 = self.rot_z(q1) @ self.trans_xyz([0.092, 0, 0])
        # Link2 to Link3               
        trans_3_4 = self.rot_y(q2) @ self.trans_xyz([0.092, 0, 0.005])
        # Link3 to end_effector        
        trans_4_5 = self.rot_y(q3) @ self.trans_xyz([0.11, 0.02, 0])
        
        trans_1_3 = trans_1_2 @ trans_2_3
        trans_1_5 = (trans_1_2 @ trans_2_3 @
                    trans_3_4 @ trans_4_5)

        return trans_1_5[:3, 3]

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
