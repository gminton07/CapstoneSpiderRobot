# ============================
# servo2040 MicroPython script
# Version 2
# Interface with ros2_control
# Created: 12 Mar, 2026
# ============================

# ************************
# Command Format:
# COMMAND arg1 arg2 arg3 ...
#
# COMMANDS: PING, CONFIGURE, CLEANUP, ACTIVATE, DEACTIVATE, SHUTDOWN, READ, WRITE
# args: float numbers
# ************************


# Import packages
import sys, select, time
from servo import servo2040, Servo
# Import user code

def handle_command(line: str) -> None:
    # Separate words and parse args
    parts = line.split()
    cmd = parts[0]
    args = [float(x) for x in parts[1:]]

    if not parts: return

    if cmd == "PING":
        print("PONG")

    elif cmd == "CONFIGURE":
        print("RP2040 Configured successfully")

    elif cmd == 'CLEANUP':
        return None

    elif cmd == "ACTIVATE":
        activate_servos()
        print("Activated")

    elif cmd == "DEACTIVATE":
        deactivate_servos()
        print("Deactivated")

    elif cmd == "SHUTDOWN":
        print('Shutdown')
    
    elif cmd == "READ":
        print('Read')

    elif cmd == "WRITE":
        print('Write')

def activate_servos():
    ##### Begin: Change to servo group
    NUM_SERVOS = 12
    s = []
    for i in range(NUM_SERVOS):
        s.append(Servo(servo2040, i))
        for servo in s:
            servo.enable
    ##### End: Change to servo group

def deactivate_servos():
    # servos delete/close
    raise NotImplementedError

# Read loop (non-blocking)
while True:
    if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
        message = sys.stdin.readline().strip()

        if message:
            print("Received: ", message)
            handle_command(message)

    time.sleep(0.001)