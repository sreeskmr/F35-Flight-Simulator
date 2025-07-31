# Custom Throttle for Microsoft Flight Simulator (MSFS) using Raspberry Pi + vJoy

This project connects a custom throttle and button interface (built using a Raspberry Pi) to Microsoft Flight Simulator by emulating a DirectInput joystick using the [vJoy](https://github.com/shauleiz/vJoy) driver on a Windows PC.

---

## 🧰 Project Overview

- **Throttle input**: Read from sensors (e.g., Hall Effect, potentiometer)
- **Button inputs**: Digital GPIO (momentary switches, toggles, etc.)
- **Raspberry Pi**: Reads input and sends over **UDP** to the PC
- **Windows PC**: Runs Python script to receive the data and inject it into **vJoy**
- **MSFS**: Reads vJoy as a DirectInput device (just like a joystick or throttle quadrant)

---

## 📦 Components Used

- Raspberry Pi (any model with Wi-Fi or Ethernet)
- Sensor for throttle (e.g., Hall Effect sensor, potentiometer)
- GPIO-connected buttons
- Windows 10/11 PC with:
  - Python 3.10+
  - vJoy (installed and configured)
  - Python libraries: `pyvjoy`, `socket`, `json`

---

## 🔌 Setup Instructions

### 1. 🖥️ Install vJoy on Windows

- Download and install from [vJoy GitHub Releases](https://github.com/shauleiz/vJoy/releases)
- Run **"Configure vJoy"**:
  - Enable only the `X` axis (or more if needed)
  - Set number of buttons (e.g., 12)
  - Disable POV/FFB if not used
- Click **Apply**

---

### 2. 🐍 Install Required Python Packages on Windows

```bash
pip install pyvjoy

---

### 3. 💻 Run the PC Receiver Script
On your Windows PC, run:

bash
Copy
Edit
python udp_to_vjoy.py

---

### 4. 🍓 Run the Raspberry Pi Sender Script
On your Raspberry Pi, run:

bash
Copy
Edit
python3 send_throttle.py

---

### 5. ✅ Confirm It’s Working
To verify the full system:

On the PC:
1. Open Monitor vJoy
2. The X-axis bar should move in response to throttle values
    Buttons 1–4 (or however many are configured) should light up when activated

In Microsoft Flight Simulator:
1. Go to Controls Options > vJoy Device
2. You should see it listed as a recognized DirectInput controller

---

Bind:
1. Throttle Axis → X-axis
2. Button 1, Button 2, etc. → Any function (gear, flaps, etc.)
    If everything moves and responds correctly, then you're fully connected and working!
