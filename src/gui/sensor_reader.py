import time

try:
    import RPi.GPIO as GPIO
    from hx711 import HX711
    import spidev  # for MCP3008 ADC
except ImportError:
    GPIO = None  # Allows testing on non-Pi systems

hx = None
spi = None

def init_sensors():
    global hx, spi
    if GPIO:
        GPIO.setmode(GPIO.BCM)

        # HX711 Setup
        hx = HX711(dout_pin=5, pd_sck_pin=6)
        hx.set_reading_format("MSB", "MSB")
        hx.set_reference_unit(1)
        hx.reset()
        hx.tare()

        # MCP3008 Setup for Hall sensor (connected to CH0)
        spi = spidev.SpiDev()
        spi.open(0, 0)
        spi.max_speed_hz = 1350000

def read_adc(channel):
    if not spi:
        return 0.0
    adc = spi.xfer2([1, (8 + channel) << 4, 0])
    data = ((adc[1] & 3) << 8) + adc[2]
    return (data / 1023.0) * 100.0  # Return % throttle

def get_throttle_position():
    return read_adc(0)  # Replace 0 with correct MCP3008 channel

def get_force_reading():
    if not hx:
        return 0.0
    val = hx.get_weight(5)
    return val

def zero_load_cell():
    if hx:
        hx.tare()

def reset_throttle_range():
    print("Throttle range reset – implement calibration logic as needed.")
