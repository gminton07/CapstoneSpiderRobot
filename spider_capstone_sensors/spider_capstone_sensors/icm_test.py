## TODO: Find/create message format for all sensor data

import time
import board
import adafruit_icm20x

# Setup I2C parameters
i2c = board.I2C()
## i2c = board.STEMMA_2C()
icm = adafruit_icm20x.ICM20948(i2c)

# Forever loop
while True:
    acc = icm.acceleration
    gyr = icm.gyro
    mag = icm.magnetic

    print(f'Acceleration: {acc}')
    print(f'Gyro: {gyr}')
    print(f'Magnetometer: {mag}')
    print('')

    time.sleep(0.2)
