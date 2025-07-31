import RPi.GPIO as GPIO
import time

BUTTON_PIN = 17  # BCM 0 = Physical pin 27 on Raspberry Pi

GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

print("Waiting for T1 press (on GPIO 0)...")

try:
    while True:
        if GPIO.input(BUTTON_PIN) == GPIO.LOW:
            print("T1 is PRESSED")
        else:
            print("T1 is not pressed")
        time.sleep(0.2)
except KeyboardInterrupt:
    pass
finally:
    GPIO.cleanup()
