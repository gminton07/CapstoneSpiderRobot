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
