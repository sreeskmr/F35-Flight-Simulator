import RPi.GPIO as GPIO             # Raspberry Pi GPIO control library
import spidev                      # SPI interface library for communicating with MCP3008
import time                        # Time utilities (e.g., sleep)
import csv                         # CSV writing module
from datetime import datetime      # For timestamp formatting

# ====== File Setup ======

# Name of the file to log button and analog events
log_file = "button_log.csv"

# Create the file and write the header row
with open(log_file, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Timestamp", "Input", "Value"])  # CSV header row

# ====== Digital GPIO Input Setup ======

# Dictionary of all button names mapped to their GPIO pins
digital_pins = {
    "T1_Button1": 0,
    "T1_Button2": 1,
    "T2_Dir1": 12,
    "T2_Dir2": 13,
    "T2_Dir3": 14,
    "T2_Dir4": 15,
    "T2_Center": 16,
    "T6": 2,
    "T7_Button1": 17,
    "T7_Button2": 18,
    "T7_Button3": 19,
    "T7_Button4": 20,
    "T7_Button5": 21,
    "T10_Button1": 3,
    "T10_Button2": 4,
    "T11": 5,
    "T12": 6,
    "T8": 7
}

# Set GPIO pin numbering scheme (BCM = GPIO numbers, not board pin numbers)
GPIO.setmode(GPIO.BCM)

# Disable GPIO warnings
GPIO.setwarnings(False)

# Set each button pin as an input with internal pull-up resistor
for pin in digital_pins.values():
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# ====== SPI and MCP3008 Setup ======

# Create SPI device object
spi = spidev.SpiDev()

# Open SPI bus 0, chip select CE0 (connects to MCP3008 CS/SHDN pin)
spi.open(0, 0)

# Set SPI clock speed (1.35 MHz)
spi.max_speed_hz = 1350000

# Define analog channels on the MCP3008
analog_channels = {
    "T3_X": 0,   # Joystick X-axis connected to CH0
    "T3_Y": 1,   # Joystick Y-axis connected to CH1
    "T4": 4,     # Some analog device on CH4
    "T3_Z": 7    # Another analog device on CH7
}

# Function to read an analog value from a specific MCP3008 channel
def read_adc(channel):
    result = spi.xfer2([1, (8 + channel) << 4, 0])  # Send SPI read command
    return ((result[1] & 3) << 8) + result[2]       # Combine result bytes to 10-bit value

# ====== Track Previous Button States ======

# Dictionary to keep track of last known state of each button
# This helps detect when a button transitions from not pressed → pressed
last_states = {name: GPIO.input(pin) for name, pin in digital_pins.items()}

# ====== Main Monitoring Loop ======
try:
    print("Logging button presses. Press Ctrl+C to stop.")

    while True:
        # Get current timestamp with microsecond precision
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")

        # === Check each button for state change ===
        for name, pin in digital_pins.items():
            current = GPIO.input(pin)              # Read current state (HIGH or LOW)
            if current != last_states[name]:       # Compare with previous state
                last_states[name] = current        # Update last state
                if current == GPIO.LOW:            # If button is pressed (LOW = pressed)
                    with open(log_file, mode='a', newline='') as file:
                        writer = csv.writer(file)
                        writer.writerow([timestamp, name, "Pressed"])  # Log it to CSV
                    print(f"{timestamp} - {name} pressed")  # Print to console

        # === Read and log analog values ===
        for name, ch in analog_channels.items():
            val = read_adc(ch)                     # Read analog value (0–1023)
            with open(log_file, mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([timestamp, name, val])  # Log analog reading
            print(f"{timestamp} - {name}: {val}")  # Print to console

        # Wait a short time before next loop iteration (reduce CPU usage/log spam)
        time.sleep(0.2)

# ====== Graceful Exit on Ctrl+C ======
except KeyboardInterrupt:
    print("\nExiting cleanly.")
    spi.close()        # Close SPI interface
    GPIO.cleanup()     # Reset GPIO pins to safe state
