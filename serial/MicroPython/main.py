# ================================
# RP2040 MicroPython USB CDC Script
# ================================

# Import packages
import sys
import select
import time
from servo import servo2040, Servo
# Import user code
import LED_RAINBOW_code
from get_current import get_current

#from analog import Analog
import math

### Setup the servos ###
s = []
NUM_SERVOS = 3
for i in range(NUM_SERVOS):
    # getattr() for dynamic looping
    s.append(Servo(getattr(servo2040, f'SERVO_{i+1}')))

for servo in s:
    servo.enable()
### Setup the servos ###

def handle_command(cmd):
    parts = cmd.strip().split()

    if not parts:
        return

    if parts[0] == "PING":
        print("PONG")

    elif parts[0] == "LED":
        # Example placeholder command
        print("ACK LED")
        LED_RAINBOW_code.led_rainbow()
        
    elif parts[0] == '1':
        print('BLUE')
        LED_RAINBOW_code.led_color('blue')
        
    elif parts[0] == 'SERVO':
        try:
            s[0].value(float(parts[1]))
            s[1].value(float(parts[2]))
            s[2].value(float(parts[3]))
            print('Servo positions set')
            print(f'{get_current()=}')
        except IndexError:
            print('SERVO command must have 3 arguments')
        
    elif parts[0] == 'CURRENT':
        current = get_current()
        print(f'{current=}')

    else:
        print("UNKNOWN:", cmd)
    

print("RP2040 USB CDC Ready")

while True:
    # Non-blocking read
    if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
        message = sys.stdin.readline().strip()

        if message:
            print("Received:", message)
            handle_command(message)

    time.sleep(0.01)