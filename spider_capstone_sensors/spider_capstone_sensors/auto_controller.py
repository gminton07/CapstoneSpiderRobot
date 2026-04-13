import rclpy
from rclpy.node import Node

from spider_capstone_msgs.msg import Control, Imu9Dof

from enum import IntEnum


# Direction enumerator from Control message
class Direction(IntEnum):
    ERROR2 = Control.ERROR2
    ERROR1 = Control.ERROR1
    FRONT = Control.NORTH
    FRONTLEFT = Control.NORTHWEST
    LEFT = Control.WEST
    BACKLEFT = Control.SOUTHWEST
    BACK = Control.SOUTH
    BACKRIGHT = Control.SOUTHEAST
    RIGHT = Control.EAST
    FRONTRIGHT = Control.NORTHEAST
    ROTCW = Control.ROTCW
    ROTCCW = Control.ROTCCW


class AutoControl(Node):
    def __init__(self):
        super().__init__('auto_control')

        # Create subscribers
        self.imu_sub = self.create_subscription(
            Imu9Dof,
            '/imu_pub',
            self.imu_cb,
            10
        )
         
        # TODO Camera subscription
        '''self.cam_sub
        '''
        
        # Create publisher
        self.control_pub = self.create_publisher(
            Control,
            '/spider_control',
            10
        )

        # Create timer
        TIMER_PERIOD = 0.5
        self.timer_ = self.create_timer(
            TIMER_PERIOD,
            self.timer_cb
        )

    def imu_cb(self, msg):
        self.acceleration = msg.linear_acc
        self.gyro = msg.angular_gyr
        self.magnetic = msg.magnetic

    def timer_cb(self):
        # TODO: Algorithm taking in IMU and camera data
        # and giving an output

        msg = Control()
        # msg.direction from Direction enum
        # msg.stop -> stop ActionSteppy

        raise NotImplementedError


def main():
    rclpy.init()
    node = AutoControl()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
