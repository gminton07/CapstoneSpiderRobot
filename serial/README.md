Here are backups of RP2040 files. And a script to interface from the host computer. usb_testing.py should work on all (Windows/Linux) platforms.

As of 25 March, 2026:
-   All scripts are loaded onto servo2040 board
-   main.py uses the commands given by the spider_capstone_hardware/SpiderHardwareInterface. Supports colored LED output for some lifecycle states. Also has white LED power indication.
-   LED_RAINBOW_code.py has updated led control methods