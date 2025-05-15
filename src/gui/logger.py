import csv
import time

log_file = None
csv_writer = None

def start_logging(throttle, force):
    global log_file, csv_writer
    if log_file is None:
        filename = f"log_{int(time.time())}.csv"
        log_file = open(filename, "w", newline="")
        csv_writer = csv.writer(log_file)
        csv_writer.writerow(["Time", "Throttle (%)", "Force (kg/N)"])

    timestamp = time.strftime("%H:%M:%S")
    csv_writer.writerow([timestamp, throttle, force])

def stop_logging():
    global log_file
    if log_file:
        log_file.close()
        log_file = None
