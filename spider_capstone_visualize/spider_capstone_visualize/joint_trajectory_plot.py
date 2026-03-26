"""
Joint Trajectory Arc Plotter
Created 23 Mar 2026
Edited 24 Mar 2026

This will plot the arc of each leg and publish it to RViz
as a Marker msg
"""


        # Possibly create a timer
        # Should probably run forever, overwriting the oldest msg points as we go
        
        # Probably have a set length like 2/3 of the full path
        # give each point index a color based on a colormap
        # keep track of the current point index and do INDEX % LENGTH to keep looping

        # Also try changing Marker().lifetime.sec
        # how long before autodelete (ns) 0 = permanent


# Import libraries
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, DurabilityPolicy, ReliabilityPolicy

from geometry_msgs.msg import Point
from sensor_msgs.msg import JointState
from std_msgs.msg import String, ColorRGBA
from visualization_msgs.msg import Marker, MarkerArray

import kdl_wrapper as kdl

from .colors import get_colormap


class JointTrajectoryPlot(Node):

    def __init__(self):
        super().__init__('joint_trajectory_plot')

        # Define constants
        self.THROTTLE_DURATION = 1.0        # How often to show logger statements
        self.MARKER_NUM_PTS = 50            # Number of points in Marker msg, loop through them
        self.LOOP_COUNTER = 0               # How many times Marker points are updated
        self.PUBLISH_HZ = 30

        qos_profile = QoSProfile(
            depth=1,
            durability=DurabilityPolicy.TRANSIENT_LOCAL,
            reliability=ReliabilityPolicy.RELIABLE
        )
        self.urdf_sub = self.create_subscription(
            String,
            '/robot_description',
            self.urdf_callback,
            qos_profile
        )

        self.marker_pub = self.create_publisher(
                    MarkerArray,
                    'joint_trajectory_plot',
                    10
                )

        # Latest joint state variable
        self.latest_joint_state = None

        self.timer = self.create_timer(1 / self.PUBLISH_HZ, self.timer_callback)

        self.frame_id_ = 'base_link'

        # Leg names
        self.legs = ['fr', 'fl', 'bl', 'br']
        
        # Define dicts
        self.chains = {}
        self.chain_joint_names = {}
        self.fk_solver = {}
        self.id_solver = {}
        self.marker_msgs = {}

        # Get colormap colors
        self.colormap, self.cmap = get_colormap(self.MARKER_NUM_PTS)

        # Define /joint_state subscriber
        self.joint_state_sub = None


        for key in self.legs:
            self.marker_msgs[key] = self.setup_marker_msg(Marker(), key)


    def setup_marker_msg(self, marker: Marker, leg: str):       
        # Setup the marker (for fr leg)
        marker_id = 0
        marker = Marker()
        marker.header.frame_id = self.frame_id_
        marker.header.frame_id = self.frame_id_

        marker.header.stamp = self.get_clock().now().to_msg()   # Put in the callback
        marker.ns = 'joint_trajectory_plot'

        match leg:
            case 'fr':
                marker_id = 0
            case 'fl':
                marker_id = 1
            case 'bl':
                marker_id = 2
            case 'br':
                marker_id = 3
            case _:
                self.get_logger().error("setup_marker_msg: Key not found!")
        marker.id = marker_id

        #marker.type = Marker.LINE_STRIP
        marker.type = Marker.POINTS
        marker.action = Marker.ADD

        #marker.scale.x = 0.001
        marker.scale.x = 0.005
        marker.scale.y = 0.005

        # Set the colors
        marker.colors = [ColorRGBA() for _ in range(self.MARKER_NUM_PTS)]
        self.setup_color_marker_msg(marker)
        

        marker.pose.position.x = 0.0
        marker.pose.position.y = 0.0
        marker.pose.position.z = 0.0
        marker.pose.orientation.w = 1.0

        # Set a marker lifetime
        marker.lifetime.sec = 0

        marker.points = [Point(x=0.0, y=0.0, z=0.0)]*self.MARKER_NUM_PTS

        return marker

    def setup_color_marker_msg(self, marker: Marker):
        # Set the point colors, keeping the current one yellow (for viridis)
        index = self.LOOP_COUNTER
        num_points = self.MARKER_NUM_PTS
        
        for i in range(num_points):
            age = ((index - i) % num_points) / (num_points - 1) if num_points > 1 else 0
            r, g, b, a = self.cmap(1 - age)
            marker.colors[i].a = a
            marker.colors[i].r = r
            marker.colors[i].g = g
            marker.colors[i].b = b
        
    def urdf_callback(self, msg: String):
        '''
        Setup KDL
        '''

        try:
            self.tree = kdl.tree_from_xml(msg.data)
            self.get_logger().info(f'Tree created with {self.tree.getNrOfSegments()} segments')

            """
            # --- THE TRACER SCRIPT ---
            curr_link = 'fr_end_effector'
            path = [curr_link]
            
            # Walk backwards until we hit the root or an error
            while True:
                parent = self.tree.getParent(curr_link)
                if parent in ["ROOT", "NOT_FOUND"]:
                    path.append(f"[{parent}]")
                    break
                path.append(parent)
                curr_link = parent
            
            # Reverse the path so it reads top-down
            path.reverse()
            self.get_logger().info(f"Ancestry Path: {' --> '.join(path)}")
            # -------------------------
            """

            for key in self.legs:
                tip_link = f'{key}_end_effector'

                self.get_logger().info(f'Finding chain: {self.frame_id_} --> {tip_link}')
                chain = self.tree.getChain(self.frame_id_, tip_link)

                num_joints = chain.getNrOfJoints()
                self.get_logger().info(f"Chain extracted from {self.frame_id_} to {tip_link}")
                self.get_logger().info(f"Number of joints in chain: {num_joints}")

                # Get names of mobile joints
                names = get_joint_names(chain) # function is down below
                self.get_logger().info(f"Active joints in chain: {names}")

                # Add to chains dict
                self.chains[key] = chain
                self.chain_joint_names[key] = names

                # Initialize solvers
                self.fk_solver[key] = kdl.ChainFkSolverPos_recursive(self.chains[key])
                gravity = kdl.Vector(0.0, 0.0, -9.81)
                self.id_solver[key] = kdl.ChainIdSolver_RNE(self.chains[key], gravity)

                self.get_logger().info(f'KDL ready! Found {len(self.chain_joint_names[key])} moving joints.')

            self.joint_state_sub = self.create_subscription(
                JointState, '/joint_states', self.joint_state_callback, 10)

            self.destroy_subscription(self.urdf_sub)

        except Exception as e:
            self.get_logger().error(f'Failed to setup KDL: {str(e)}')

    def sync_joint_state(self, msg: JointState, leg: str):
        # Map incoming ROS JointState to a KDL JntArray
        jnt_pos = kdl.JntArray(len(self.chain_joint_names[leg]))
        ros_pos_map = dict(zip(msg.name, msg.position))

        for i, name in enumerate(self.chain_joint_names[leg]):
            if name in ros_pos_map:
                jnt_pos[i] = ros_pos_map[name]
        return jnt_pos

    def joint_state_callback(self, msg: JointState):
        # Extremely fast update. No math here!
        self.latest_joint_state = msg

    def timer_callback(self):
        # Don't run if no joint state or KDL chains
        if self.latest_joint_state is None or not self.fk_solver:
            return
        
        # Make a MarkerArray
        marker_array = MarkerArray()

        # Sync data
        for leg in self.legs:
            q = self.sync_joint_state(self.latest_joint_state, leg)

            # Forward kinematics
            frame = self.fk_solver[leg].JntToCart(q)
            pos = frame.p
            #self.get_logger().info(f'End Effector: x={pos.x:.2f}, y={pos.y:.2f}, x={pos.z:.2f}', throttle_duration_sec=self.THROTTLE_DURATION)

            self.marker_msgs[leg].points[self.LOOP_COUNTER%self.MARKER_NUM_PTS] = Point(x=pos.x, y=pos.y, z=pos.z)
            self.marker_msgs[leg].header.stamp = self.get_clock().now().to_msg()
            self.setup_color_marker_msg(self.marker_msgs[leg])  # Set the current color scheme
            marker_array.markers.append(self.marker_msgs[leg])
            
        self.marker_pub.publish(marker_array)
        self.get_logger().info(f'Publishing {len(marker_array.markers)} markers with {len(marker_array.markers[0].points)} points each.', throttle_duration_sec=self.THROTTLE_DURATION)

        # Increment main loop
        self.LOOP_COUNTER += 1

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
            
    return joint_names


def main():
    rclpy.init()
    node = JointTrajectoryPlot()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()
