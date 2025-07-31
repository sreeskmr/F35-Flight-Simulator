# 🛩️ F35 Throttle System

This is the complete software suite for the **F-35 custom throttle controller**, built for Windows and Raspberry Pi. It handles communication between your hardware and PC-based flight simulators like **Microsoft Flight Simulator** and **DCS World**, using **UDP** and **vJoy** for button and throttle inputs.

---

## 🔧 Features

- Live throttle tracking and button states
- Raspberry Pi → PC communication over Wi-Fi
- vJoy integration for simulator control
- CSV-based button map
- GUI with step-by-step setup tabs

---

## 🛫 How to Use the F35 Throttle System

### 1. ⚙️ Set Up the Raspberry Pi (First Time Only)

#### What You Need:
- Raspberry Pi 4 or 5
- Monitor, HDMI, keyboard, mouse
- Pre-installed Raspberry Pi OS

#### 🧪 Connect to Wi-Fi

1. Boot the Pi
2. Press `Ctrl + T` to open a terminal
3. Run the following commands:

```bash
nmcli dev wifi list  # Find your network name (SSID)

nmcli connection add type wifi ifname wlan0 con-name mywifi ssid "YOUR_WIFI_NAME"
nmcli connection modify mywifi wifi-sec.key-mgmt wpa-psk
nmcli connection modify mywifi wifi-sec.psk "YOUR_WIFI_PASSWORD"
nmcli connection modify mywifi connection.autoconnect yes

sudo reboot
```

4. After rebooting, find the Pi’s IP address:

```bash
hostname -I
```

Copy this IP (e.g., `192.168.1.42`) — you’ll enter it into the GUI on your PC.

---

### 2. 🖥️ Install the F35 Software on Your PC

1. Download `F35_Installer.exe` from the [GitHub Releases](https://github.com/YOUR_USERNAME/YOUR_REPO_NAME/releases)
2. Run the installer
3. Launch the program via the desktop or Start Menu

---

### 3. 🔍 Explore the Tabs

#### 📋 Tab 1: Throttle Button Map
- Displays all buttons (T1–T26) with labels, control types, and ideal functions
- Use this for reference while binding buttons in your sim

#### 🔘 Tab 2: Button Status
- Real-time display of pressed buttons
- Useful for debugging GPIO inputs and confirming Pi-to-PC communication
- Input your Pi's IP address here to begin receiving throttle and button data

#### 🎮 Tab 3: Game Integration
- Instructions for:
  - Installing [vJoy](https://sourceforge.net/projects/vjoystick/)
  - Opening the vJoy configuration tool
  - Setting up button count, axes, and enabling force feedback (optional)

---

### 4. 🎮 Open Your Simulator and Bind Controls

- Launch **Microsoft Flight Simulator**, **DCS**, or any sim that recognizes vJoy
- Bind buttons (T1–T26) and throttle axis from the vJoy device to in-game functions
- Use the **Throttle Button Map** tab to match hardware labels with simulator bindings

---

## 🧰 Requirements

- Windows 10/11
- Raspberry Pi (with Python 3)
- vJoy driver (from SourceForge)

---

## 🧱 Potential Future Additions

* Detent mapping + throttle zone LEDs
* Rudder and brake input support
* Full hardware calibration GUI tab
* Touchscreen Pi support
* Multi-device throttle (dual-engine)
* Realistic force feedback motorization

---

## 👨‍💼 Maintained By

**Sreelekshmi Sreekumar**
University of Central Florida
Mechanical Engineering + Computer Science

---

## 📄 License

This project is licensed under the MIT License. See [`LICENSE`](LICENSE) for details.