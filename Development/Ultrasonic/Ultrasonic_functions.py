import RPi.GPIO as GPIO
import time

def Initialize_Ult(pin_read, pin_out)
    
    # Set the board mode #
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    # Setup the GPIO pins #
    GPIO.setup(pin_out,GPIO.OUT)
    GPIO.output(pin_out, False)
    GPIO.setup(pin_read, GPIO.IN)
    
    # Let the ssensor initialize and config #
    time.sleep(.02)


# Under assumption the configuration for the GPIO warnings and mode is preconfigured in the main script when calling #
def Distance_Read(Read,Trigger) # This is for setting the pin layout #

    GPIO.output(Trigger,True)
    time.sleep(.00001) # Sendout one pulse #
    GPIO.output(Trigger,False)

    # Read right after signal left
    start_time = time.time()

    # Check when the read in pin detects the ultrasonic reflection #
    while GPIO.input(Read) == False:
        end_time = time.time()

    # Find when the it stops detecting (This would be the true travel dT) #
    while GPIO.input(Read) == True:
        end_time_prime = time.time()



    # Find the time difference #
    delta_T = end_time_prime - start_time

    # Speed of sound in room temperature #
    V_temp = 340  # Set to meters/s #

    # Read the calculated distance #
    Distance_meters = (V_temp  * delta_T)/2
    Distance_inches = Distance_meters * 39.37

    return Distance_meters, Distance_inches
