import RPi.GPIO as GPIO
import time

T12_PIN = 12  # Adjust as needed

GPIO.setmode(GPIO.BCM)
GPIO.setup(T12_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

try:
    print("Waiting for T12 button press...")
    while True:
        if GPIO.input(T12_PIN) == GPIO.LOW:
            print("T12 pressed → Manual Pitch Override activated")
            time.sleep(0.3)  # debounce delay
        time.sleep(0.01)

except KeyboardInterrupt:
    GPIO.cleanup()
