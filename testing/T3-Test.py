import spidev
import time

# Open SPI bus 0, device 0 (CE0)
spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 1350000  # Safe for MCP3008

def read_channel(channel):
    if channel < 0 or channel > 7:
        return -1
    adc = spi.xfer2([1, (8 + channel) << 4, 0])
    value = ((adc[1] & 3) << 8) | adc[2]
    return value

def convert_to_voltage(value, vref=3.3):
    return (value * vref) / 1023

# Determine direction: -1 = center, 0 = up/left, 1 = down/right
def get_direction(voltage):
    if voltage < 1.0:
        return 0  # up or left
    elif voltage > 2.2:
        return 1  # down or right
    else:
        return -1  # center

def direction_label(x_dir, y_dir):
    if x_dir == -1 and y_dir == -1:
        return "Center"
    elif y_dir == 0:
        return "Up"
    elif y_dir == 1:
        return "Down"
    elif x_dir == 0:
        return "Right"
    elif x_dir == 1:
        return "Left"
    return "Unknown"

print("Reading joystick analog values from MCP3008 (CH0 = Y, CH1 = X)...")
try:
    while True:
        y_raw = read_channel(0)
        x_raw = read_channel(1)
        y_volt = convert_to_voltage(y_raw)
        x_volt = convert_to_voltage(x_raw)

        x_dir = get_direction(x_volt)
        y_dir = get_direction(y_volt)
        label = direction_label(x_dir, y_dir)

        print(f"X: {x_dir} ({x_volt:.2f} V) | Y: {y_dir} ({y_volt:.2f} V) → Direction: {label}")
        time.sleep(0.1)

except KeyboardInterrupt:
    print("\nExiting...")
    spi.close()
