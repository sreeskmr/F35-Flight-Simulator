# Enhanced Live Input Logger for Raspberry Pi

This project is a real-time GUI application for monitoring digital and analog inputs on a Raspberry Pi. It interfaces with various buttons and joystick sensors connected via GPIO and MCP3008 (SPI-based ADC). Designed to be interactive and hardware-aware, it provides both visual feedback and optional logging.

---

## 🧰 Features

- 🖱️ Real-time button press detection
- 📈 Live graphing of analog sensor data (e.g., joystick axes)
- 🕹️ MCP3008 integration for analog input via SPI
- 🔘 Start/Stop control for monitoring session
- 📁 Optional file logging (toggleable in GUI)
- ✨ Visual feedback when a button is pressed
- ✅ Clean shutdown and GPIO cleanup

---

## 🖼️ GUI Preview

```
+-----------------------------+
| Status: Running             |
| [Start] [Stop] [Log to File]|
+-----------------------------+
| T3_X: 658                  |
| T3_Y: 314                  |
| T4:   459                  |
| T3_Z: 877                  |
+-----------------------------+
| [12:01:05] T1_Button1 pressed |
| [12:01:06] T3_X: 658        |
+-----------------------------+
|     [Live Analog Graph]    |
+-----------------------------+
```

---

## 🚀 Running the App

### On Raspberry Pi:

1. Make sure Python 3 is installed.
2. Install required packages:
    ```bash
    sudo apt install python3-tk python3-matplotlib
    pip3 install spidev RPi.GPIO
    ```
3. Run the script:
    ```bash
    python3 enhanced_live_gui_logger.py
    ```

---

## 💻 Converting to Executable (Windows)

To build a `.exe`:
1. On a Windows PC, install:
    ```bash
    pip install pyinstaller
    ```
2. Create the executable:
    ```bash
    pyinstaller --onefile --noconsole enhanced_live_gui_logger.py
    ```

Note: `.exe` files do **not** run on Raspberry Pi — they are for Windows only.

---

## 📦 Project Structure

- `enhanced_live_gui_logger.py` – Main GUI and hardware interface script
- `button_log.csv` (optional) – Output log file (when enabled)

---

## 📄 License

MIT License

---

## 👤 Author

Developed by Sree for a hardware-interfacing flight simulator panel and logging application.