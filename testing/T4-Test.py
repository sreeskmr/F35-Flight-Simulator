import spidev
import time

# === SPI SETUP ===
spi = spidev.SpiDev()
spi.open(0, 0)  # SPI bus 0, device 0 (CE0)
spi.max_speed_hz = 1350000

# === MCP3008 READ FUNCTION ===
def read_channel(channel):
    if channel < 0 or channel > 7:
        return -1
    adc = spi.xfer2([1, (8 + channel) << 4, 0])
    return ((adc[1] & 3) << 8) + adc[2]

# === VOLTAGE CONVERSION ===
def convert_to_voltage(value, vref=3.3):
    return (value * vref) / 1023

# === INTERPRET FNR ACTION ===
def get_t4_action(voltage):
    if voltage > 2.6:
        return "DECEL"
    elif voltage < 1.0:
        return "ACCEL"
    else:
        return "NEUTRAL"

# === CONFIGURATION ===
# Adjust if you're using a different channel
T4_AXIS_CHANNEL = 2  # CH2 (e.g., X-axis or Y-axis of FNR joystick)

print("🛫 T4 Joystick (FNR) Test — Press Ctrl+C to exit")
try:
    while True:
        raw_val = read_channel(T4_AXIS_CHANNEL)
        voltage = convert_to_voltage(raw_val)
        action = get_t4_action(voltage)

        print(f"T4 Voltage: {voltage:.2f} V | Action: {action}")
        time.sleep(0.1)

except KeyboardInterrupt:
    print("\nExiting T4 test.")
    spi.close()
