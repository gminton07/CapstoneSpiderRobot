#!/usr/bin/env python3
# 
# See Controllers in GUI format
# ros2 run rqt_controller_manager rqt_controller_manager

# yaml for saving joint trajectories as dict
import yaml
domp = (yaml.dump({'right': [[1,2,3],[4,5,6],[7,8,9]]}))
print(f'{domp = }')

input = yaml.load(domp, )
print(f'{input = }')

del input