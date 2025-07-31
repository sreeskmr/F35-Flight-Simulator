import RPi.GPIO as GPIO
import time

# GPIO pins connected to the switch
CHAFF_PIN = 5
FLARE_PIN = 6

GPIO.setmode(GPIO.BCM)
GPIO.setup(CHAFF_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(FLARE_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

print("Monitoring T5: Chaff / Flare 3-position switch...")

try:
    while True:
        chaff = GPIO.input(CHAFF_PIN) == GPIO.LOW
        flare = GPIO.input(FLARE_PIN) == GPIO.LOW

        if chaff:
            print("Chaff deployed (Up)")
        elif flare:
            print("Flare deployed (Down)")
        else:
            print("Auto mode (Middle)")

        time.sleep(0.25)

except KeyboardInterrupt:
    GPIO.cleanup()
