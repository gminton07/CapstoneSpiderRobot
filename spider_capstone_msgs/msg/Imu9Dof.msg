# This message holds all of the data from our ICM20948
# 
# Acceleration: m/s^2
# Angular velocity (gyro): degrees/sec
# Magnetic: uT

std_msgs/Header header

geometry_msgs/Vector3 linear_acc
geometry_msgs/Vector3 angular_gyr
geometry_msgs/Vector3 magnetic
