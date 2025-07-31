import socket
import json
import pyvjoy

j = pyvjoy.VJoyDevice(1)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("0.0.0.0", 49000))  # Listen on all interfaces, port 49000

print("Listening for throttle/button data...")

while True:
    try:
        data, _ = sock.recvfrom(1024)
        payload = json.loads(data.decode())

        throttle = payload["throttle"]
        buttons = payload["buttons"]

        # Scale throttle 0–100% → 0–32767
        scaled = int(throttle / 100 * 32767)
        j.set_axis(pyvjoy.HID_USAGE_X, scaled)

        for i, state in enumerate(buttons):
            j.set_button(i + 1, state)

    except Exception as e:
        print("Error:", e)