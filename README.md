# CapstoneSpiderRobot
Capstone project: developing quadruped spider robot

## ROS2 Packages
* __spider_capstone__
  - Metapackage for spider_capstone dependency packages
    - Listed in package.xml
  - Makes sure that all project packages are installed

* __spider_capstone_bringup__
  * config
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
        * use_gui -- (bool, Default: false) Whether to launch GUI nodes. Not for use of headless pi
        * core_group -- (bool, Default: true) Whether to launch core node group. Turn off for use on external (non-robot) computer
        * use_sensors -- (bool, Default: true) Whether to launch sensor group (true) or joy group (false)

    - spider_capstone_launch.xml (DEPRECATED)
      - XML launch file for starting controllers and RViz

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
  - Loaded as the hardware_interface in spider.ros2_control.xacro of spider_capstone_description (this is the default URDF now)

* __spider_capstone_msgs__
  - Special message types for inter-node communication
  - Control
    - Sends general control data for the ActionSteppy leg gait controller.
    - direction, stop
  - Imu9Dof
    - Sends linear acceleration, angular velocity, and magnetic from our 9 DoF imu.

* __spider_capstone_trajectory__
  - Calculate and publish trajectory messages to the controller stack
  - test_jsp
    - Calculates joint-space positions for the end effector (radians)
    - Currently uses joints from 02-stl-move.urdf for single-leg movement (can be changed for use with 4-legs)
    - Launch alongside ```view_spider.launch.py model:=02-stl-move.urdf gui:= false```
  - joint_trajectory
    - This node sends a JointTrajectory message to joint_trajectory_controller_1 (front_right leg). I am trying to use kdl_py_bridge to extract the names of mobile joints for each leg (instead of hard-coding).

* __spider_capstone_sensors__
  - Where the sensor nodes will live (joystick, camera, IMU, etc.)
  - joy_readings
    - Takes input from joystick controller and outputs direction as 1/8 cardinal directions (North, NorthWest, West, SouthWest, South, SouthEast, East, NorthEast)
    - Publishes on topic '/joy_controller' with type std_msgs.msg.String
    - Can be extended for further joystick input needs

* __spider_capstone_visualize__
  - Workspace envelope visualization for RViz
  - Use with spider_capstone_description:view_spider.launch.py

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
    
    - __MicroPython dir__: Holds a copy of the MP files loaded onto the servo2040 board. Current as of March 03.

### Create new packages for each separate feature
This way, everything will be organized better. 
Push updates into a new branch (feature/[feature]) so nothing breaks.
```bash
git checkout -b [new_branch_name]
```
