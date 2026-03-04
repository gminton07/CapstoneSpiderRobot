# CapstoneSpiderRobot
Capstone project: developing quadruped spider robot

## Tasks
Create spreadsheet for who is doing what & how ist going? Like WUAIR?

* __servo__
  * Update message format to accept float[12] of joint positions.
* __trajectory_publisher__
  * Integrate other python into a JointTrajectory msg publisher

## Initial Setup

```bash
# Create workspace if not already done
mkdir -p ~/ros2_ws/src && cd ~/ros2_ws/src

# Clone the repo with SSH keys
git clone git@github.com:gminton07/CapstoneSpiderRobot.git

# Install dependencies with ROSDEP
# --from-paths src:   Dir to find packages
# -y:                 Yes to all prompts
# --ignore-src:       Ignore installing present packages
cd ~/ros2_ws
rosdep install --from-paths src -y --ignore-src 

# Build workspace with symlinks
colcon build --symlink-install

# Source the workspace
source ~/ros2_ws/install/setup.bash

# Launch general viewing nodes
ros2 launch spider_capstone_description view_spider.launch.py
```

### If the above does not work:
Make sure colcon, and rosdep are installed.  
```bash
apt-get python3-rosdep
sudo rosdep init
rosdep update
```

## Packages
* __spider_capstone__
  - Metapackage for spider_capstone dependency packages
    - Listed in package.xml
  - Makes sure that all project packages are installed

* __spider_capstone_bringup__
  - spider_capstone_controllers.yaml
    - Configures the controller_manager and its controllers with ros__parameters
    - update_rate: How fast the controllers will try to run (Hz)
    - joints: Names for the joints each JointTrajectoryController can use
    - control_interfaces: Input parameter types
    - state_interfaces: Output parameter types
  - spider_capstone_launch.xml
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

* __spider_capstone_trajectory__
  - Calculate and publish trajectory messages to the controller stack
  - test_jsp
    - Calculates joint-space positions for the end effector (radians)
    - Currently uses joints from 02-stl-move.urdf for single-leg movement (can be changed for use with 4-legs)
    - Launch alongside ```view_spider.launch.py model:=02-stl-move.urdf gui:= false```
  - joint_trajectory
    - This node sends a JointTrajectory message to joint_trajectory_controller_1 (front_right leg). I am trying to use kdl_py_bridge to extract the names of mobile joints for each leg (instead of hard-coding).

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
    Afterwards, it <span style="color:red;">SHOULD NOT </span> require ```sudo``` to run the python script.
    This may require a logout/ restart to fully activate.
    - __MicroPython dir__: Holds a copy of the MP files loaded onto the servo2040 board. Current as of March 03.

### Create new packages for each separate feature
This way, everything will be organized better. 
Push updates into a new branch (feature/[feature]) so nothing breaks.
```bash
git checkout -b [new_branch_name]
```
