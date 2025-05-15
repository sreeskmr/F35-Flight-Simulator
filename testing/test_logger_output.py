from logger import start_logging, stop_logging
import time

for i in range(10):
    throttle = i * 10
    force = 100 - i * 5
    start_logging(throttle, force)
    time.sleep(0.1)

stop_logging()
print("Test log file written.")
