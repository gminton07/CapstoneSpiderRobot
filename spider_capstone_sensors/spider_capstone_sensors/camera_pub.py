import rclpy
from rclpy.node import Node
from std_msgs.msg import String ## Placeholder

import numpy as np
import cv2

from .Camera_Functions import Capture_Image

class CameraNode(Node):
    def __init__(self):
        super().__init__('camera_node')
        
        self.cam_pub = self.create_publisher(
               String,
               '/camera_pub',
               10
        )

        DURATION = 0.1
        self.timer = self.create_timer(
                DURATION,
                self.timer_callback
        )

        self.cap = cv2.VideoCapture('/dev/video0',cv2.CAP_V4L)
        # TODO: Set height and width for self.cap


    def timer_callback(self):
        ret,frame = self.cap.read()

        if not ret:
            self.get_logger().debug('No Image')
            return
        heading_angle=self.image_process(frame)

        ### ADDED HERE ###
        msg = String()
        msg.data = str(heading_angle)
        self.get_logger().debug(f'sending heading angle {msg.data}')
        self.cam_pub.publish(msg)
        ### ADDED HERE ###

    def image_process(self, frame):
        # TODO: Add computations and
        # publish on self.cam_pub

        # Switch the image into an HSV image for color detection #
        HSV_img = cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
        mask_img1 = cv2.inRange(HSV_img, (0, 150, 30), (20, 255, 255) )
        mask_img2 = cv2.inRange(HSV_img, (160,100,80),(180, 255, 255) )
        Mask_img = cv2.bitwise_or(mask_img1, mask_img2)
        Blur_img = cv2.blur(Mask_img,(5,5))

        thresh = cv2.threshold(Blur_img, 200,255,cv2.THRESH_BINARY)[1]
        M = cv2.moments(thresh)
        if M['m00'] == 0:
            heading_angle = 0
        else:
            cX = int(M['m10']/M['m00'])
            cY = int(M['m01']/M['m00'])
            center = [int(1640/2) , int(1230/2) ] #[x,y]#
            heading_angle = np.arctan2(  (center[1] - cY) , abs(center[0]-cX) )
            heading_angle = heading_angle * 180/(np.pi)

        # TODO: What message format does the auto_control
        # node require?

        return heading_angle


def main():
    rclpy.init()
    node = CameraNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
