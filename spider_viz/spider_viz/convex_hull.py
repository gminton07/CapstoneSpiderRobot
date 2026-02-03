import numpy as np
from scipy.spatial import ConvexHull
from geometry_msgs.msg import Point
from visualization_msgs.msg import Marker

def points_to_mesh(points, frame_id, marker_id):
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
    
    marker.color.r = 0.2
    marker.color.g = 0.6
    marker.color.b = 1.0
    marker.color.a = 0.3

    marker.points = []

    for simplex in hull.simplices:
        for idx in simplex:
            x, y, z = pts[idx]
            marker.points.append(Point(x=x, y=y, z=z))

    return marker
