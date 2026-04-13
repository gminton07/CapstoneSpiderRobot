# ============================
# servo2040 MicroPython script
# Version 2
# Interface with ros2_control
# Created: 12 Mar, 2026
# Updated 12 Apr, 2026
# ============================

# ************************
# Command Format:
# COMMAND arg1 arg2 arg3 ...
#
# COMMANDS: PING, ENABLE, DISABLE, MOVE
# args: float numbers
#
# LED colors:
#   blue:   Board powered on
#   green:  Hardware enabled
#   red:    Show an error
#   off:    Hardware deactivated, turn light off
#	POWER:	white, board is powered on
# ************************


# Import packages
import sys, select, time
from servo import servo2040, Servo
from math import pi

# Import user modules
from LED_RAINBOW_code import led_color, power_led

# Create variables
servos = []

# Actions on startup
print('Initialized')
power_led()

def handle_command(line: str) -> None:
    # Separate words and parse args
    parts = line.split()
    cmd = parts[0]
    args = [float(x) for x in parts[1:]]

    if not parts: return

    if cmd == "PING":
        print("PONG")

    elif cmd == "ENABLE":
        activate_servos()
        led_color('green')
        print("Activated")

    elif cmd == "DISABLE":
        deactivate_servos()
        led_color('off')
        print("Deactivated")
        
    elif cmd == "MOVE":
        move_servos(args)
        print("Moving")

    elif cmd=="ERROR":
        led_color('red')
        print('Error')

    else:
        print(f'CMD not recognized: {cmd}')

        

def activate_servos():
    ##### Begin: Change to servo group
    NUM_SERVOS = 12
    START_PIN = servo2040.SERVO_1
    END_PIN = servo2040.SERVO_12
    for i in range(START_PIN, END_PIN + 1):
        servos.append(Servo(i))
    for s in servos:
        s.enable()

    ##### End: Change to servo group

def deactivate_servos():
    for s in servos:
        s.disable()
        
def move_servos(position):
    for i in range(len(position)):
        if i in [5, 8, 11]:
            ang = rad_to_deg(position[i])
            servos[i].value(-ang)
        
def rad_to_deg(rad: float) -> float:
    deg = rad * 180 / pi
    return deg

# Read loop (non-blocking)
while True:
    if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
        message = sys.stdin.readline().strip()

        if message:
            #print("Received: ", message)
            handle_command(message)

    time.sleep(0.001)