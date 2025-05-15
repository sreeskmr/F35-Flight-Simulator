import socket
import time
import math

PC_IP = "192.168.1.X"  # Replace with your PC IP
PORT = 49005
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

while True:
    # Sine wave throttle test (0 to 1)
    throttle = (math.sin(time.time()) + 1) / 2
    sock.sendto(f"{throttle:.2f}".encode(), (PC_IP, PORT))
    time.sleep(0.05)