# Python USB CDC script
# PC version

import serial, threading, time
import platform

# Dynamically set PORT based on the system OS
PLATFORM = platform.system()
if PLATFORM == 'Windows':
    PORT = 'COM6'
elif PLATFORM == 'Linux':
    PORT = '/dev/ttyACM0'

BAUD = 115200

ser = serial.Serial(PORT, BAUD, timeout=1)
time.sleep(2)       # Allow board to fully reset

def read_from_board():
    while True:
        if ser.in_waiting:
            line = ser.readline().decode(errors='ignore').strip()
            if line:
                print('RP2040 -> PC:', line)

def write_to_board():
    while True:
        msg = input('PC -> RP2040:')
        ser.write((msg + '\n').encode())


# Start background reader
reader = threading.Thread(target=read_from_board, daemon=True)
reader.start()

print("Connected to RP2040")
write_to_board()