# Read joystick information and output direction for BigSteppy

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from sensor_msgs.msg import Joy

import numpy as np

class JoyController(Node):
    def __init__(self):
        super().__init__('joy_controller')

        # Subscriber
        self.subscriber_ = self.create_subscription(
                Joy,
                '/joy',
                self.joy_callback,
                10
        )

        # Publisher
        self.publisher_ = self.create_publisher(
                String,
                '/joy_controller',
                10
        )


    def joy_callback(self, msg):
        # Get axes from the Joy msg and calculate which octant the angle rests in
        axes = msg.axes

        # Create new message
        msg = String()

        mag = np.sqrt(axes[0]**2 + axes[1]**2)
        if mag >= 0.7:
            left_stick_ang = np.arctan2(axes[0], axes[1])

            if np.abs(left_stick_ang) <= np.pi/8:
                msg.data = "North"
            elif np.abs(left_stick_ang) >= np.pi*7/8:
                msg.data = "South"
            elif left_stick_ang > 0:
                if left_stick_ang <= np.pi*3/8:
                    msg.data = "NorthWest"
                elif left_stick_ang <= np.pi*5/8:
                    msg.data = "West"
                elif left_stick_ang <= np.pi*7/8:
                    msg.data = "SouthWest"
                else:
                    msg.data = "JOYSTICK ERROR 0"
            else:
                left_stick_ang = np.abs(left_stick_ang)
                if left_stick_ang <= np.pi*3/8:
                    msg.data = "NorthEast"
                elif left_stick_ang <= np.pi*5/8:
                    msg.data = "East"
                elif left_stick_ang <= np.pi*7/8:
                    msg.data = "SouthEast"
                else:
                    msg.data = "JOYSTICK ERROR 1"

            self.get_logger().info(f'ang = {left_stick_ang:.4f}, dir = {msg.data}')

            self.publisher_.publish(msg)



def main():
    rclpy.init()
    node = JoyController()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
