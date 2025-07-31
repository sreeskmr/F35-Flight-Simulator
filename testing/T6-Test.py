import RPi.GPIO as GPIO
import time

T6_PIN = 16  # Adjust as needed

GPIO.setmode(GPIO.BCM)
GPIO.setup(T6_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

try:
    print("Waiting for T6 button press...")
    while True:
        if GPIO.input(T6_PIN) == GPIO.LOW:
            print("T6 pressed → APC / SSS / Auto-STO activated")
            time.sleep(0.3)  # debounce delay
        time.sleep(0.01)

except KeyboardInterrupt:
    GPIO.cleanup()
