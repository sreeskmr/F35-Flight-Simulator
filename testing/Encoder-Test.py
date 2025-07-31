import RPi.GPIO as GPIO
import time

# === CONFIGURATION ===
pin_a = 13  # Channel A (green)
pin_b = 26  # Channel B (white)
PPR = 600  # Pulses per revolution
IN_PER_REV = 2.0  # Linear travel per full revolution in inches
MAX_TRAVEL = 5.0  # Max throttle distance in inches

# === SETUP ===
GPIO.setmode(GPIO.BCM)
GPIO.setup(pin_a, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(pin_b, GPIO.IN, pull_up_down=GPIO.PUD_UP)

position_count = 0  # Raw encoder counts
last_a = GPIO.input(pin_a)

def calculate_linear_inches(counts):
    return (counts / PPR) * IN_PER_REV

def calculate_throttle_percent(pos_in_inches):
    if pos_in_inches <= 0:
        return 0
    elif pos_in_inches >= MAX_TRAVEL:
        return 100
    else:
        return round((pos_in_inches / MAX_TRAVEL) * 100)

print("🔄 Reading encoder and converting to linear motion (inches)...")

try:
    while True:
        current_a = GPIO.input(pin_a)
        current_b = GPIO.input(pin_b)

        if current_a != last_a:
            if current_b != current_a:
                position_count += 1
                direction = "Forward"
            else:
                position_count -= 1
                direction = "Reverse"

