# Sensor tests -- Gabe

## IMU (ICM20948)
Set ```sudo raspi-config``` --> enable I2C interface
```sudo i2cdetect -y 1``` --> check I2C device address
Installed adafruit-circuitpython-icm20x (+ dependencies) from pip
icm_test.py reads + prints the data

## Camera (RPi Camera 1.3)
Set ```sudo raspi-config``` --> enable Legacy Camera
Make sure cv2 is installed (mine already was)
camera_test.py shows live video on screen

## Next Steps
Have a msg format to send ICM data to auto-control node
Implement image processing --> auto-control node
Change both into proper ROS nodes
Create msg format for joy/auto-control nodes --> ActionSteppy
