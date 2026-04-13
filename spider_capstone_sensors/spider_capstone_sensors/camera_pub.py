import rclpy
from rclpy.node import Node
from std_msgs.msg import String ## Placeholder

import cv2

class CameraNode(Node):
    def __init__(self):
        super().__init__('camera_node')
        
        self.cam_pub = self.create_publisher(
               String,
               '/camera_pub',
               10
        )

        DURATION = 0.5
        self.timer = self.create_timer(
                DURATION,
                self.timer_callback
        )

        self.cap = cv2.VideoCapture('/dev/video0', cv2.CAP_V4L)
        # TODO: Set height and width for self.cap

    def timer_callback(self):
        rval, frame = self.cap.read()

        self.image_process(frame)

    def image_process(self, frame):
        # TODO: Add computations and 
        # publish on self.cam_pub

        # TODO: What message format does the auto_control
        # node require?

        raise NotImplementedError


def main():
    rclpy.init()
    node = CameraNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
