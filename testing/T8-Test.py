import spidev
import time

spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 1350000

ALPHA_CH = 4
BETA_CH = 5

def read_voltage(channel):
    adc = spi.xfer2([1, (8 + channel) << 4, 0])
    val = ((adc[1] & 3) << 8) | adc[2]
    voltage = val * 3.3 / 1023
    return voltage

def classify(voltage):
    if voltage < 0.5:
        return 0  # UP
    elif voltage > 2.5:
        return 1  # DOWN
    else:
        return -1  # CENTER

prev_state = -1

print("T8 Scroll Selector Active (UP = 0, CENTER = -1, DOWN = 1)")
try:
    while True:
        v_alpha = read_voltage(ALPHA_CH)
        v_beta = read_voltage(BETA_CH)

        logic = classify(v_alpha)  # Just pick Alpha; Beta is redundant here
        if logic != prev_state:
            if logic == 0:
                print("↑ Scroll Up")
            elif logic == 1:
                print("↓ Scroll Down")
            prev_state = logic

        if logic == -1:
            prev_state = -1  # Reset so next move will trigger again

        time.sleep(0.05)

except KeyboardInterrupt:
    spi.close()
    print("\nExiting.")
