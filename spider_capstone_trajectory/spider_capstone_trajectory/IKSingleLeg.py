import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, DurabilityPolicy, ReliabilityPolicy
from std_msgs.msg import String
import kdl_wrapper as kdl

class JointSpaceSkeletonGenerator(Node):
    def __init__(self):
        super().__init__('joint_space_skeleton_generator')
        
        # This will hold the final list of joint positions for your interpolator
        self.joint_trajectory_skeleton = []
        
        # Setup Subscription to get URDF
        qos = QoSProfile(
            depth=1, 
            durability=DurabilityPolicy.TRANSIENT_LOCAL, 
            reliability=ReliabilityPolicy.RELIABLE
        )
        self.urdf_sub = self.create_subscription(
            String, 
            '/robot_description', 
            self.urdf_callback, 
            qos
        )
        
        self.get_logger().info("Setup Stage: Awaiting URDF to generate joint-space values...")

    def urdf_callback(self, msg):
        try:
            tree = kdl.tree_from_xml(msg.data)
            # Extracting the single leg chain
            chain = tree.getChain("base_link", "fr_end_effector")
            
            # Initialize the IK Solver (LMA is robust for spider legs)
            ik_solver = kdl.ChainIkSolverPos_LMA(chain)
            
            # Initial seed (all zeros)
            num_joints = chain.getNrOfJoints()
            q_seed = kdl.JntArray(num_joints)

            # --- PREDEFINED WAYPOINTS ---
            # Cartesian coordinates relative to base_link
            cartesian_points = [
                (0.18, -0.12, -0.05),
                (0.20, -0.12, -0.02), # Step up
                (0.22, -0.12, -0.05)  # Step down
            ]

            # Orientation: Keeping the foot level (Roll=0, Pitch=0, Yaw=0)
            # This uses the new static RPY method we added to the wrapper
            target_rotation = kdl.Rotation.RPY(0.0, 0.0, 0.0)

            self.get_logger().info(f"Generating skeleton for {len(cartesian_points)} points...")

            for pt in cartesian_points:
                target_frame = kdl.Frame()
                target_frame.p = kdl.Vector(pt[0], pt[1], pt[2])
                target_frame.M = target_rotation

                # Solve IK
                status, q_out = ik_solver.CartToJnt(q_seed, target_frame)

                if status >= 0:
                    # Convert to standard Python list and store
                    joint_angles = [q_out[i] for i in range(q_out.rows())]
                    self.joint_trajectory_skeleton.append(joint_angles)

                    # Update seed with this result so the next IK call starts from here
                    for i in range(q_out.rows()):
                        q_seed[i] = q_out[i]
                else:
                    self.get_logger().warn(f"IK failed for point {pt}. Out of reach?")

            self.get_logger().info("Joint-space skeleton generated successfully.")
            
            # Proceed to your interpolation logic here
            # Send to joint trajectory controllers
            self.start_interpolation_service()

            # Cleanup subscription
            self.destroy_subscription(self.urdf_sub)

        except Exception as e:
            self.get_logger().error(f"Setup Stage Failed: {e}")

    def start_interpolation_service(self):
        # Placeholder for where you trigger your downstream joint-space logic
        self.get_logger().info(f"Ready to interpolate {len(self.joint_trajectory_skeleton)} keyframes.")

def main():
    rclpy.init()
    node = JointSpaceSkeletonGenerator()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()