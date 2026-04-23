# Publisher for Ultrasonic
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

import RPi.GPIO as GPIO
import time

from .Ultrasonic_functions import Initialize_Ult, Distance_Read


class Ultrasonic(Node):
    def __init__(self):
        super().__init__('Ultrasonic_node')

        # Create publisher & timer
        self.Ultrasonic_pub = self.create_publisher(
                String,
                '/ultrasonic_pub',
                10
        )

        DURATION = 0.5
        self.timer_ = self.create_timer(
                DURATION,
                self.timer_callback
        )
        
        # BCM layout, alternative Boardmode (11 [Read], 13 [Trigger]) #
        self.pin1 = 17 # Read in pin (Echo) #
        self.pin2 = 27 # Output pin (Trigger) #
        self.initialize_ult = Initialize_Ult(self.pin1, self.pin2)
        self.distance = Distance_Read(self.pin1, self.pin2)

    def timer_callback(self):
        # input pins as arguments for pin1 and pin2 (trig, echo) #
        self.initialize_ult(self.pin1, self.pin2)
        distance = self.distance(self.pin1, self.pin2)

        ### ADDED HERE ###
        msg = String
        msg.data = distance
        self.Ultrasonic_pub.publish(msg)
        ### ADDED HERE ###
        
    
def main():
    rclpy.init()
    node = Ultrasonic()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
