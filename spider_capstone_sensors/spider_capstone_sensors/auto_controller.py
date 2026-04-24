import rclpy
from rclpy.node import Node
from std_msgs.msg import String

from spider_capstone_msgs.msg import Control, Imu9Dof

from enum import IntEnum


# Direction enumerator from Control message
class Direction(IntEnum):
    ERROR2 = Control.ERROR2
    ERROR1 = Control.ERROR1
    IDLE = Control.IDLE
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

        # Create msg data objects
        self.acceleration = None
        self.gyro = None
        self.magnetic = None

        self.camera_msg_data = None

        self.distance = None

        # Create subscribers
        self.imu_sub = self.create_subscription(
            Imu9Dof,
            '/imu_pub',
            self.imu_cb,
            10
        )
         
        self.camera_sub = self.create_subscription(
            String,
            '/camera_pub',
            self.camera_cb,
            10
        )

        self.ultra_sub = self.create_subscription(
            String,
            '/ultrasonic_pub',
            self.ultra_cb,
            10
        )
        
        # Create publisher
        self.control_pub = self.create_publisher(
            Control,
            '/spider_control',
            10
        )

        # Create timer
        TIMER_PERIOD = 0.2
        self.timer_ = self.create_timer(
            TIMER_PERIOD,
            self.timer_cb
        )

    def imu_cb(self, msg):
        self.acceleration = msg.linear_acc
        self.gyro = msg.angular_gyr
        self.magnetic = msg.magnetic

    def camera_cb(self, msg):
        self.camera_msg_data = float(msg.data)

    def ultra_cb(self, msg):
        self.distance = float(msg.data)

    def timer_cb(self):
        # Break if messages not received yet
        '''
        if (not self.acceleration) or (not self.camera_msg_data) or (not self.distance):
            return None
        '''
        
        msg = Control()

        # Check ultrasonic distance
        if not self.distance:
            return
        MIN_DIST = 10   # Minimum distance before stopping
        if self.distance < MIN_DIST:
            msg.stop = True
            self.control_pub.publish(msg)
            self.get_logger().info(f'Control message: {msg.direction=} {msg.stop=}') 
            return # should stop the exit this logic chain

        # Check camera angles
        if not self.camera_msg_data:
            return
        if self.camera_msg_data < -15:    # Turn LEFT?
            msg.direction = Direction.ROTCW
        elif self.camera_msg_data > 15:
            msg.direction = Direction.ROTCCW 
        else: 
            msg.direction = Direction.FRONT
        # -90 to 90 deg?
        self.control_pub.publish(msg)
        self.get_logger().info(f'Control message: {msg.direction=} {msg.stop=}') 


def main():
    rclpy.init()
    node = AutoControl()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
