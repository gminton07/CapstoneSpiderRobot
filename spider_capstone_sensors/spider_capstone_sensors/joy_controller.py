# Read joystick information and out_ut direction for BigSteppy

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
                '/spider_control',
                10
        )


    def joy_callback(self, msg):
        # Get axes from the Joy msg and calculate which octant the angle rests in
        axes = msg.axes
        buttons = msg.buttons

        # Create new message
        out_msg = Control()

        mag = np.sqrt(axes[0]**2 + axes[1]**2)
        left_stick_ang = 0
        if mag >= 0.7:
            left_stick_ang = np.arctan2(axes[0], axes[1])

            if np.abs(left_stick_ang) <= np.pi/8:
                out_msg.direction = Control.NORTH
            elif np.abs(left_stick_ang) >= np.pi*7/8:
                out_msg.direction = Control.SOUTH
            elif left_stick_ang > 0:
                if left_stick_ang <= np.pi*3/8:
                    out_msg.direction = Control.NORTHWEST
                elif left_stick_ang <= np.pi*5/8:
                    out_msg.direction = Control.WEST
                elif left_stick_ang <= np.pi*7/8:
                    out_msg.direction = Control.SOUTHWEST
                else:
                    out_msg.direction = Control.ERROR1
            else:
                left_stick_ang = np.abs(left_stick_ang)
                if left_stick_ang <= np.pi*3/8:
                    out_msg.direction = Control.NORTHEAST
                elif left_stick_ang <= np.pi*5/8:
                    out_msg.direction = Control.EAST
                elif left_stick_ang <= np.pi*7/8:
                    out_msg.direction = Control.SOUTHEAST
                else:
                    out_msg.direction = Control.ERROR2

        # Check for rotation commands
        if axes[4] == -1.0:
            out_msg.direction = Control.ROTCCW
        elif axes[5] == -1.0:
            out_msg.direction = Control.ROTCW

        # Check the stop button
        if buttons[0]:
            out_msg.stop = True
        else:
            out_msg.stop = False

        # Publish the message
        self.get_logger().info(f'ang = {left_stick_ang:.4f}, dir = {out_msg.direction}, stop = {out_msg.stop}')
        self.publisher_.publish(out_msg)



def main():
    rclpy.init()
    node = JoyController()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
