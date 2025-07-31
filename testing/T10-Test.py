import RPi.GPIO as GPIO
import time

BUTTON_PIN = 18  # BCM 0 = Physical pin 27 on Raspberry Pi

GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

print("Waiting for T10 press (on GPIO 4)...")

try:
    while True:
        if GPIO.input(BUTTON_PIN) == GPIO.LOW:
            print("T10 is PRESSED")
        else:
            print("T10 is not pressed")
        time.sleep(0.2)
except KeyboardInterrupt:
    pass
finally:
    GPIO.cleanup()
