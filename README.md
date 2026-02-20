# CapstoneSpiderRobot
Capstone project: developing quadruped spider robot

I am updating the documentation as we go!

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

### If the following does not work:
Make sure colcon, and rosdep are installed.  
```bash
apt-get python3-rosdep
sudo rosdep init
rosdep update
```

## Packages
* spider_capstone
  - Metapackage for spider_capstone packages
  - Make sure that all project packages are installed

* spider_capstone_description
  - URDF robot descriptions
  - RViz configurations
  - Launch file for RViz robot visualization
  - Future: will include ros2_control tags for URDF descriptions

* spider_capstone_visualize
  - Workspace envelope visualization for RViz
  - Use with spider_capstone_description:view_spider.launch.py

* spider_capstone_trajectory
  - Calculate and publish trajectory messages to the robot/ simulation
  - test_jsp
    - Calculates joint-space positions for the end effector (radians)
    - Currently uses joints from 02-stl-move.urdf for single-leg movement (can be changed for use with 4-legs)
    - Currently launches with view_spider.launch.py (model:=___, gui:=false)

### Create new packages for each separate feature
This way, everything will be organized better. 
Push updates into a new branch (feature/[feature]) so nothing breaks.
```bash
git checkout -b [new_branch_name]
```
