# Publisher for ICM20948 data

import time
import board, adafruit_icm20x

import rclpy
from rclpy.node import Node

from spider_capstone_msgs.msg import Imu9Dof

class IcmNode(Node):
    def __init__(self):
        super().__init__('icm_node')

        # Create publisher & timer
        self.icm_pub = self.create_publisher(
                Imu9Dof,
                '/icm_pub',
                10
        )

        self.timer_ = self.create_timer(
                DURATION,
                self.timer_callback
        )

        # Setup I2C
        self.i2c = board.I2C()
        self.icm = adafruit_icm20x.ICM20948(i2c)

    def timer_callback(self):
        msg = Imu9Dof()

        # Read data from ICM20948
        acc = self.icm.acceleration
        gyr = self.icm.gyro
        mag = self.icm.magnetic

        # Add data to the message
        msg.linear_acc.x = acc[0]
        msg.linear_acc.x = acc[1]
        msg.linear_acc.x = acc[2]

        msg.angular_gyr.x = gyr[0]
        msg.angular_gyr.x = gyr[1]
        msg.angular_gyr.x = gyr[2] 

        msg.magnetic.x = mag[0]
        msg.magnetic.x = mag[1]
        msg.magnetic.x = mag[2]

        self.icm_pub.publish(msg)
        self.get_logger().info('ICM data published')

    
def main():
    rclpy.init()
    node = IcmNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
