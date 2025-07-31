import RPi.GPIO as GPIO
import time

# GPIO pin numbers for the two sides of the toggle switch
PIN_STD = 27   # Standard lighting
PIN_NVG = 21   # NVG/Covert lighting

GPIO.setmode(GPIO.BCM)

# Set both GPIOs as input with pull-up resistors
GPIO.setup(PIN_STD, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(PIN_NVG, GPIO.IN, pull_up_down=GPIO.PUD_UP)

print("Testing T11 (External Lights 3-position switch)...")
print("Positions: OFF (neutral), STD (standard), NVG (covert)")

try:
    while True:
        std_state = GPIO.input(PIN_STD)
        nvg_state = GPIO.input(PIN_NVG)

        if std_state == 0:
            print("T11 Position: STANDARD LIGHTING")
        elif nvg_state == 0:
            print("T11 Position: NVG / COVERT LIGHTING")
        else:
            print("T11 Position: OFF / NEUTRAL")

        time.sleep(0.5)

except KeyboardInterrupt:
    GPIO.cleanup()
