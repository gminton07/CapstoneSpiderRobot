# CapstoneSpiderRobot
Capstone project: developing quadruped spider robot

Look around at what I have made so far.
I will update this to have better information later.

## Initial Setup
1.  If ROS2 workspace not already created: $ mkdir -p ~/ros2_ws/src && cd ~/ros2_ws/src
2.  Clone repo (I suggest using SSH keys)
3.  $ cd ~/ros2_ws && colcon build --symlink-install   # Always install symlinks, it will be easier in the long run
4.  $ source ~/ros2_ws/install.setup.bash
5.  $ ros2 launch spider_capstone view_spider.launch.py

## Packages
* spider_capstone
  - URDF robot descriptions
  - Launch file for RViz robot visualization

* spider_viz
  - Workspace envelope visualization for RViz
  - Use with spider_capstone:view_spider.launch.py

### Create new packages for each separate feature
This way, everything will be organized better. 
Push updates into a new branch (feature/[feature]) so nothing breaks.