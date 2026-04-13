# This Node when activated logs the battery status from the UPS x1209 and saves it to a csv file Excel. (Graphs make rictor happy)
## imports required by ROS2 Jazzy:
import rclpy
from rclpy.node import Node
from rclpy.duration import Duration
from rclpy.qos import QoSProfile, DurabilityPolicy, ReliabilityPolicy
from std_msgs.msg import String
from math import pi       # import number
import numpy as np        # import numpi library for fast math
import kdl_wrapper as kdl # ?
## imports required by UPS code:
import os
import struct
import smbus2
import logging
import subprocess
import gpiod
from subprocess import call
## imports requiredfor data collection:
import csv
from datetime import datetime
## import shared:
import time


class PowerLogger(Node): # nodes are class objects, what defines it
    def __init__(self): # when create class, automatically runs on class creation
        super().__init__('ActionSteppy') # put variable declarations here?
        # User-configurable variables
        self.SHUTDOWN_THRESHOLD = 3  # Number of consecutive failures required for shutdown
        #SLEEP_TIME = 60  # Time in seconds to wait between failure checks
        # Loop =  False
        self.start_time = time.time() # for data stamping

        ################### BOOT UP SECTION ######################
        # Ensure only one instance of the script is running (written by x1209 suptronics =people)
        pid = str(os.getpid()) # "get processs id"
        self.pidfile = "/tmp/X1200.pid" #"/var/run/X1200.pid" # move to /var/run because of conventions
        if os.path.isfile(self.pidfile):
            print("Script already running, closing writer")
            os.unlink(self.pidfile) ## NOTE THIS SHOULD NOT GO HERE, ONLY STOP GAP
            exit(1)
        else:
            with open(self.pidfile, 'w') as f:
                f.write(pid)
        ## CSV related chunk to create log file with header:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S') # pattern: year month day _ 24Hour min sec
        self.log_file = f"/home/neil/Desktop/BattLogs/Battery_log_beginning_{timestamp}.csv" # its in military time
        data = [["Timestamp", "Time(S)","Charge%", "Voltage(V)","Battery Status", "Power Status"]] # the header
        with open(self.log_file, mode='w', newline='') as file: # 'w' overwrites 'a' appends
            writer = csv.writer(file)
            writer.writerows(data)
        
        ###############  
        self.bus = smbus2.SMBus(1) #should just run once
        self.address = 0x36
        PLD_PIN = 6
        chip = gpiod.Chip('gpiochip0') # since kernel release 6.6.45 you have to use 'gpiochip0' - before it was 'gpiochip4'
        self.pld_line = chip.get_line(PLD_PIN)
        self.pld_line.request(consumer="PLD", type=gpiod.LINE_REQ_DIR_IN)
        ## timer to collect data samples
        self.timer_ = self.create_timer(5, self.log_battery) # makes timer, for timing actions. 15 default
        self.data_pts = 0
        self.max_pts = 2000
        self.failure_counter = 0 # for automatic pi shutoff. Lets probably leave this off for now
    
    ## Functions for battery data collection:
    def readVoltage(self,bus):
        read = self.bus.read_word_data(self.address, 2) # reads word data (16 bit)
        swapped = struct.unpack("<H", struct.pack(">H", read))[0] # big endian to little endian
        voltage = swapped * 1.25 / 1000 / 16 # convert to understandable voltage
        return voltage

    def readCapacity(self,bus):
        read = self.bus.read_word_data(self.address, 4) # reads word data (16 bit)
        swapped = struct.unpack("<H", struct.pack(">H", read))[0] # big endian to little endian
        capacity = swapped / 256 # convert to 1-100% scale
        return capacity

    def get_battery_status(self,voltage):
        if 3.87 <= voltage <= 4.2:
            return "Full"
        elif 3.7 <= voltage < 3.87:
            return "High"
        elif 3.55 <= voltage < 3.7:
            return "Medium"
        elif 3.4 <= voltage < 3.55:
            return "Low"
        elif voltage < 3.4:
            return "Critical"
        else:
            return "Unknown"

    def log_battery(self): 
        if self.data_pts > self.max_pts:
            print(f"Max pts reached, Exiting. data pts: {self.data_pts}, max pts: {self.max_pts}")
            exit(0)
        

        #for _ in range(self.SHUTDOWN_THRESHOLD): # NOTE: loop is just to verify if battery is actually out of charge.
                                        # typically this loop only runs once
        ac_power_state = self.pld_line.get_value()
        voltage = self.readVoltage(self.bus)
        battery_status = self.get_battery_status(voltage)
        capacity = self.readCapacity(self.bus)
        #print(f"Capacity: {capacity:.2f}% ({battery_status}), AC Power State: {'Plugged in' if ac_power_state == 1 else 'Unplugged'}, Voltage: {voltage:.2f}V")
        
        data = [[datetime.now(), f'{(time.time() - self.start_time):.3f}', f'{capacity:.2f}',f'{voltage:.4f}',f'{battery_status}',f'{'Plugged in' if ac_power_state == 1 else 'Unplugged'}']] # create log entry line
        with open(self.log_file, mode='a', newline='') as file: # open and save data to file
            writer = csv.writer(file)
            writer.writerows(data)

        if ac_power_state == 0:
            #print("UPS is unplugged or AC power loss detected.")
            #self.failure_counter += 1
            if capacity < 20:
                print("Battery level critical.")
                self.failure_counter += 1
            if voltage < 3.20:
                print("Battery voltage critical.")
                self.failure_counter += 1
        else:
            self.failure_counter = 0

        # if failure_counter < SHUTDOWN_THRESHOLD: ## NOTE: ros2 jazzy will handle waiting.
        #     time.sleep(SLEEP_TIME) 
        self.data_pts += 1
        if self.failure_counter >= self.SHUTDOWN_THRESHOLD:
            shutdown_reason = ""
            if capacity < 20:
                shutdown_reason = "due to critical battery level."
            elif voltage < 3.20:
                shutdown_reason = "due to critical battery voltage."
            elif ac_power_state == 0:
                shutdown_reason = "due to AC power loss or UPS unplugged."

            shutdown_message = f"Critical condition met {shutdown_reason} Initiating shutdown."
            print(shutdown_message)
            print("Neil: shutdown feature currently disabled for pending ros integration")
            #call("sudo nohup shutdown -h now", shell=True) # the shutdown feature
        # else:
        #     #print("System operating within normal parameters. No action required.")
        #     if Loop:
        #         time.sleep(SLEEP_TIME)
        #     else:
        #         exit(0)
    
    def cleanup(self):
        if os.path.isfile(self.pidfile):
            os.unlink(self.pidfile) # deletes file path means delete file (not overwrite just declare as free space)

# always need a main!
def main(): # makes object and spins up node
    try:
        rclpy.init()
        node = PowerLogger() # while in the spin (state?) I think BigSteppy() acts as main loop?
        rclpy.spin(node) # neil note: I think the node exists here until you hit ctrl^c or otherwise terminate node.
    except KeyboardInterrupt:
        node.cleanup()
        node.destroy_node()
        rclpy.shutdown()

# technically this is executed first if you think about it.
if __name__ == '__main__':
    main()
