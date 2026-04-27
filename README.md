# CapstoneSpiderRobot
Capstone project: developing quadruped spider robot

## ROS2 Packages
- __spider_capstone__
  - Metapackage for spider_capstone dependency packages
    - Listed in package.xml
  - Makes sure that all project packages are installed at build time

- __spider_capstone_bringup__
  - config
    - spider_capstone_controllers.yaml
      - Configures the controller_manager and its controllers with ros__parameters
      - update_rate: How fast the controllers will try to run (Hz)
      - joints: Names for the joints each JointTrajectoryController can use
      - control_interfaces: Input parameter types
      - state_interfaces: Output parameter types  
  * launch
    - spider_capstone.launch.py
      - Python launch file for the project
      - CLI arguments
        * use_mock_hardware -- (bool, Default: false) Whether to run real or mock hardware
        * use_gui -- (bool, Default: false) Whether to launch GUI group. Not for use on headless pi. Includes: rviz2, trajectory plotter.
        * core_group -- (bool, Default: true) Whether to launch core node group. Includes: robot_state_publisher, controller_manager & controller spawners.
        * use_sensors -- (bool, Default: true) Whether to launch sensor group. Includes: camera, ICM, ultrasonic, sensor control.
        * use_joy -- (bool, Default: false) Whether to launch Joy group. Includes: joy_node, joy_controller.
    - spider_capstone_launch.xml (DEPRECATED)
      - XML launch file for starting controllers and RViz
    - laptop.launch.py
      - Launch things for the local machine. GUI and Joy groups available.
    - pi.launch.py
      - Launch things for the robot itself. Core and Sensor groups, leg gait node available. Requires an SSH key for Pi to run smoothly.
  - python
    - gui_launcher.py
      - Opens a GUI launcher for running the ROS2 system from another machine through SSH. Runs laptop.launch.py on the local machine and pi.launch.py on the robot. Includes: checkboxes for the CLI arguments as defined above, selector for leg gait controller, and Launch/ Stop buttons. The Pi and Local machines must be on the same subnet for proper operation.

* __spider_capstone_description__
  - URDF robot descriptions with STL meshes
  - ros2_control xacro plugin for main URDF
  - RViz configurations
  - Launch file for RViz robot visualization: view_spider.launch.py
    - Parameters
      - model
      - rviz_config
      - gui

* __spider_capstone_hardware__
  - The hardware interface to work with our Servo2040 servo control board
  - Plugin: spider_capstone_hardware/SpiderCapstoneInterface
  - Loaded as the hardware_interface in the default URDF

* __spider_capstone_msgs__
  - Special message types for inter-node communication
  - Control
    - General control data for the ActionSteppy leg gait controller.
    - direction (8 cardinal directions, rotation, error), stop
  - Imu9Dof
    - Linear acceleration, angular velocity, and magnetic from our 9 DoF imu.

* __spider_capstone_sensors__   
  - Where all sensor nodes/ scripts live.
  - auto_controller
    - Takes in data from the camera, imu, and ultrasonic sensors and outputs a Control message for the active leg gait node.
  - joy_controller
    - Takes in joystick readings and outputs the Control message for active leg gait node.
  - camera_node
    - Takes an image and processes it, sending result to auto_controller
  - icm_node
    - Reads out ICM20948 data and publishes Imu9Dof message for auto_controller
  - PowerLogger
    - Reads Pi battery status from the UPS and logs it to csv.
  - Ultrasonic_node
    - Reads distance from ultrasonic sensor and publishes to auto_controller

* __spider_capstone_trajectory__
  - Calculate and publish trajectory messages to the controller stack
  - test_jsp
    - Calculates joint-space positions for the end effector (radians)
    - Currently uses joints from 02-stl-move.urdf for single-leg movement (can be changed for use with 4-legs)
    - Launch alongside ```view_spider.launch.py model:=02-stl-move.urdf gui:= false```
  - joint_trajectory
    - This node sends a JointTrajectory message to joint_trajectory_controller_1 (front_right leg). I am trying to use kdl_py_bridge to extract the names of mobile joints for each leg (instead of hard-coding).
  - BigSteppy
    - A leg gait node, sending JointTrajectory messages to joint trajectory controllers through the topic interface. Uses our functions to compute inverse kinematics and walking cycles. 
  - ActionSteppy
    - ***The main leg gait node***, sending JointTrajectory messages to joint trajectory controllers through action interface. Takes input from sensor's joy_controller/auto_controller. Uses our inverse kinematics functions still. Unlike BigSteppy, ActionSteppy will cancel the leg trajectory if it receives an "IDLE" command. 
  - IKSingleLeg
    - Imports link lengths and offsets from the URDF file and does inverse kinematics using the LMA solver from orocos_kdl package. Not currently in use.
   
* __spider_capstone_visualize__
  * Nodes to draw extra RViz visualizations
    * joint_trajectory_plot
      * 
    * leg_3_joint_node
      * Shows the workspace envelope for a 3-joint leg. We played with voxel points and convex meshes. Featuring hard-coded forward kinematics with measurements for the Prototype meshes.
    * leg_2_joint_node
      * A relic from when we tested having 2 joints per leg instead of 3. This shows the leg's workspace envelope in that case. It is more a surface than a volume.

* __kdl_py_bridge__
  - Exposes some classes and class methods from C++ into a Python package.
  - See kdl_wrapper.cpp for what is available. This is not an exhaustive list of what the KDL packages offer.

## Utilities
  * __Serial__
    - Contains all files necessary to run servo2040 motor board. We are using USB CDC communications through the serial library. There are scripts for the host- and peripheral-sides. The pimoroni micropython UF2 binary is also there for resetting the servo2040's firmware.
    - __usb_testing.py__ is the Host python script. This should be configured to work on both Linux and Windows machines. 
      - If you cannot run the script as $USER on Linux, you must add yourself to the dialout group which owns the connection:
    ```sudo usermod -aG dialout $USER```.
    Check if this worked with ```groups $USER```.
    Afterwards, it $\color{#f00}{\textsf{SHOULD NOT}}$ require ```sudo``` to run the python script.
    This may require a logout/ restart to fully activate.
    
    - __MicroPython dir__: Holds a copy of the MP files loaded onto the servo2040 board. Current as of 27 Apr 2026.
