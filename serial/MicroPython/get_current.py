from pimoroni import Analog
from servo import servo2040
import time

cur_adc = Analog(servo2040.SHARED_ADC, servo2040.CURRENT_GAIN, servo2040.SHUNT_RESISTOR, servo2040.CURRENT_OFFSET)    

def get_current():
    current = 0.0
    SAMPLES = 1
    for i in range(SAMPLES):
        current += cur_adc.read_current()
        time.sleep(0.01)
    current /= SAMPLES
    return current

if __name__ == '__main__':
    get_current()