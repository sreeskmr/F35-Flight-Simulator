# 🛩️ F-35 Flight Simulator – Throttle Control System

This repository contains the complete hardware/software stack for a custom throttle control system used in an F-35 flight simulator. It includes:

- A physical throttle with a **Hall effect sensor** and **load cell**
- A **Python GUI** for calibration, live plotting, and logging
- **Raspberry Pi integration**
- Real-time simulator control for both **X-Plane** and **Microsoft Flight Simulator (MSFS)**

---

## 📁 Project Structure

```
F35-Flight-Simulator/
├── src/              # Python GUI, sensor code, and UDP sender
├── config/           # Throttle calibration and logging settings
├── testing/          # Hardware-free test tools for development
├── sim-plugins/      # Plugins for X-Plane and MSFS integration
```

---

## 💻 Features

### ✅ Raspberry Pi (Python)
- Real-time GUI with live throttle and force display
- Zero/load cell calibration + throttle calibration buttons
- CSV logging with configurable interval
- UDP throttle sender to PC

### ✅ X-Plane Plugin (C++)
- Receives throttle percentage over UDP
- Sets engine throttle via `sim/flightmodel/engine/ENGN_thro[0]`

### ✅ MSFS Plugin (C# SimConnect)
- Windows Forms app with live throttle UI
- Listens to UDP from Pi
- Reconnects automatically if MSFS closes
- Logs errors and runtime messages

---

## ⚙️ Setup

### 🔌 Hardware
- **Raspberry Pi 4 or 5**
- **Hall effect sensor** connected via ADC (e.g., MCP3008)
- **Load cell + HX711 amplifier**

### 🐍 Raspberry Pi (Python)
```bash
pip install matplotlib RPi.GPIO spidev
```

Then run:
```bash
python3 src/gui/main_gui.py
```

### ✈️ X-Plane Plugin
1. Download the X-Plane SDK and place `CHeaders/XPLM` in `XPLM-SDK/`
2. Build using CMake:
   ```bash
   mkdir build && cd build
   cmake ..
   cmake --build . --config Release
   ```
3. Copy the `.xpl` plugin to:
   ```
   <X-Plane>/Resources/plugins/ThrottleUDPPlugin/win_x64/
   ```

### 🛬 MSFS SimConnect App
1. Open `ThrottleBridge.csproj` in Visual Studio
2. Update the path to `SimConnect.dll` in the `.csproj`
3. Build + run — the GUI will show live throttle values

---

## 🔧 Configuration

Edit these files as needed:

- `config/throttle_config.json` – ADC calibration, axis direction
- `config/logging_config.json` – CSV logging behavior

---

## 🧪 Testing Without Hardware

Use the `testing/` folder:

- `fake_throttle_sender.py` – Sends simulated throttle over UDP
- `test_logger_output.py` – Validates CSV logger output

---

## 🧱 Potential Future Additions

- Detent mapping + throttle zones
- MSFS rudder/brake support
- GUI-based config editor
- Touchscreen-optimized Pi UI
- Force feedback modeling

---

## 👨‍💻 Maintained By

**Sreelekshmi Sreekumar**  
University of Central Florida  
Mechanical Engineering + Computer Science