import socket
import json
import time

PC_IP = "192.168.1.66"  # ← replace this with your PC's IP address
PORT = 49000

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

while True:
    # Simulate throttle + button presses
    throttle = 42.0  # percent (replace with real sensor value later)
    buttons = [1, 0, 1, 0]  # simulated button presses

    data = {"throttle": throttle, "buttons": buttons}
    sock.sendto(json.dumps(data).encode(), (PC_IP, PORT))
    time.sleep(0.01)  # Send every 10 ms
