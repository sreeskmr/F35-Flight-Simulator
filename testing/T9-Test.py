import RPi.GPIO as GPIO
import time

# Use BCM numbering
PIN_BOTTOM = 23   # Connected to left terminal
PIN_TOP = 22  # Connected to right terminal

GPIO.setmode(GPIO.BCM)
GPIO.setup(PIN_BOTTOM, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(PIN_TOP, GPIO.IN, pull_up_down=GPIO.PUD_UP)

try:
    while True:
        bottom = GPIO.input(PIN_BOTTOM)
        top = GPIO.input(PIN_TOP)

        if bottom == GPIO.LOW and top == GPIO.HIGH:
            print("Switch is in BOTTOM position")
        elif top == GPIO.LOW and bottom == GPIO.HIGH:
            print("Switch is in TOP position")
        elif bottom == GPIO.HIGH and top == GPIO.HIGH:
            print("Switch is in CENTER (neutral) position")
        else:
            print("ERROR: both LOW (shouldn’t happen)")
        
        time.sleep(0.2)

except KeyboardInterrupt:
    GPIO.cleanup()
