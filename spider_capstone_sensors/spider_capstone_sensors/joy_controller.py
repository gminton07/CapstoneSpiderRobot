# Read joystick information and output direction for BigSteppy

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Joy

from spider_capstone_msgs.msg import Control

from enum import Enum
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
                Control,
                '/joy_controller',
                10
        )


    def joy_callback(self, msg):
        # Get axes from the Joy msg and calculate which octant the angle rests in
        axes = msg.axes

        # Create new message
        out_msg = Control()

        mag = np.sqrt(axes[0]**2 + axes[1]**2)
        if mag >= 0.7:
            left_stick_ang = np.arctan2(axes[0], axes[1])

            if np.abs(left_stick_ang) <= np.pi/8:
                out.msg.direction = Control.NORTH
            elif np.abs(left_stick_ang) >= np.pi*7/8:
                out.msg.direction = Control.SOUTH
            elif left_stick_ang > 0:
                if left_stick_ang <= np.pi*3/8:
                    out.msg.direction = Control.NORTHWEST
                elif left_stick_ang <= np.pi*5/8:
                    out.msg.direction = Control.WEST
                elif left_stick_ang <= np.pi*7/8:
                    out.msg.direction = Control.SOUTHWEST
                else:
                    out.msg.direction = Control.ERROR1
            else:
                left_stick_ang = np.abs(left_stick_ang)
                if left_stick_ang <= np.pi*3/8:
                    out.msg.direction = Control.NORTHEAST
                elif left_stick_ang <= np.pi*5/8:
                    out.msg.direction = Control.EAST
                elif left_stick_ang <= np.pi*7/8:
                    out.msg.direction = Control.SOUTHEAST
                else:
                    out.msg.direction = Control.ERROR2

                out_msg.stop = true

            self.get_logger().info(f'ang = {left_stick_ang:.4f}, dir = {out_msg.direction}, stop = {out_msg.stop}')


            self.publisher_.publish(out.msg)



def main():
    rclpy.init()
    node = JoyController()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
