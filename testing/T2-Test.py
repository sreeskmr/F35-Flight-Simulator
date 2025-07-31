import RPi.GPIO as GPIO
import time

# Inputs (rows)
inputs = [24, 14]
# Outputs (columns)
outputs = [15, 25]

# Directions from matrix logic
direction_map = {
    (14, 15): "Left",
    (24, 25): "Right"
}

GPIO.setmode(GPIO.BCM)

for pin in inputs:
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
for pin in outputs:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.HIGH)

# Track how long Left is held
left_start_time = None
center_hold_duration = 1.0  # seconds

print("Matrix scanning 4-way switch with hold-left = Center...")

try:
    while True:
        detected = None
        is_left_pressed = False

        # Standard matrix scan
        for out_pin in outputs:
            GPIO.output(out_pin, GPIO.LOW)
            for in_pin in inputs:
                if GPIO.input(in_pin) == GPIO.LOW:
                    if (in_pin, out_pin) == (14, 15) or (out_pin, in_pin) == (14, 15):
                        is_left_pressed = True  # Track Left press
                    else:
                        direction = direction_map.get((in_pin, out_pin)) or direction_map.get((out_pin, in_pin))
                        if direction:
                            detected = direction
            GPIO.output(out_pin, GPIO.HIGH)

        # Hold-to-Center logic
        if is_left_pressed:
            if left_start_time is None:
                left_start_time = time.time()
            elif time.time() - left_start_time >= center_hold_duration:
                detected = "Center"
        else:
            if left_start_time is not None and time.time() - left_start_time < center_hold_duration:
                detected = "Left"
            left_start_time = None

        # Special cases
        if GPIO.input(25) == GPIO.LOW and GPIO.input(14) == GPIO.LOW:
            detected = "Down"
        if GPIO.input(15) == GPIO.LOW and GPIO.input(24) == GPIO.LOW:
            detected = "Up"

        if detected:
            print(f"{detected} pressed")
            time.sleep(0.25)
        else:
            time.sleep(0.05)

except KeyboardInterrupt:
    GPIO.cleanup()