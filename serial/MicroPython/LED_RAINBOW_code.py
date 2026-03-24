# ============================
# servo2040 MicroPython script
# Led control library
# Created: 12 Mar, 2026
# Updated 23 Mar, 2026
# ============================

import time
from pimoroni import Button
from plasma import WS2812
from servo import servo2040

"""
Displays a rotating rainbow pattern on the Servo 2040's onboard LED bar.

Press "Boot" to exit the program.

NOTE: Plasma WS2812 uses the RP2040's PIO system, and as
such may have problems when running code multiple times.
If you encounter issues, try resetting your board.
"""

SPEED = 5           # The speed that the LEDs will cycle at
BRIGHTNESS = 0.4    # The brightness of the LEDs
UPDATES = 50        # How many times the LEDs will be updated per second

# Create the LED bar, using PIO 1 and State Machine 0
led_bar = WS2812(servo2040.NUM_LEDS, 1, 0, servo2040.LED_DATA)

# Create the user button
user_sw = Button(servo2040.USER_SW)

# Start updating the LED bar
led_bar.start()

def led_rainbow():
    offset = 0.0
    start_time = time.time()
    curr_time = start_time

    # Make rainbows until the user button is pressed
    while not user_sw.raw() and (curr_time-start_time < 5):

        offset += SPEED / 1000.0

        # Update all the LEDs
        for i in range(servo2040.NUM_LEDS):
            hue = float(i) / servo2040.NUM_LEDS
            led_bar.set_hsv(i, hue + offset, 1.0, BRIGHTNESS)

        time.sleep(1.0 / UPDATES)
        curr_time = time.time()

    # Turn off the LED bar
    led_bar.clear()
    print('Rainbow timed out :(')
    
def led_color(color):
    hue = []
    if color not in ['blue', 'green', 'red', 'off']:
        print(f'Color {color} not recognized')
        hue = [255, 255, 255]
    elif color == 'red':
        hue = [200, 0, 0] 
    elif color == 'green':
        hue = [0, 200, 0]
    elif color == 'blue':
        hue = [0, 0, 200]
    elif color == 'off':
        hue = [0, 0, 0]
       
    for i in range(servo2040.NUM_LEDS):
        led_bar.set_rgb(i, hue[0], hue[1], hue[2])