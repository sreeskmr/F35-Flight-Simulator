import pyvjoy
import time

j = pyvjoy.VJoyDevice(1)

# Move throttle (X axis) from 0 to 100% over time
for i in range(0, 32768, 1024):
    j.set_axis(pyvjoy.HID_USAGE_X, i)
    print(f"Throttle set to {i / 327.67:.1f}%")
    time.sleep(0.05)

# Press and release buttons 1 to 4
for i in range(1, 5):
    j.set_button(i, 1)  # Press
    time.sleep(0.2)
    j.set_button(i, 0)  # Release
    time.sleep(0.1)