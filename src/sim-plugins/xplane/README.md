# X-Plane Throttle Plugin (UDP Receiver)

This plugin receives throttle values from your Raspberry Pi over UDP and applies them to X-Plane via the dataref `sim/flightmodel/engine/ENGN_thro[0]`.

### 📦 Build Instructions

1. Download and extract the [X-Plane SDK](https://developer.x-plane.com/sdk/)
2. Place the `CHeaders/XPLM` folder in `XPLM-SDK/` inside this folder
3. Run:
   ```bash
   mkdir build && cd build
   cmake ..
   cmake --build . --config Release