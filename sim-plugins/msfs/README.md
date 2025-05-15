# MSFS SimConnect Throttle Bridge

This C# Windows Forms app receives throttle values from your Raspberry Pi over UDP and sends them to Microsoft Flight Simulator using SimConnect.

### 💻 Requirements

- .NET Framework 4.7.2
- Microsoft Flight Simulator
- SimConnect.dll from the MSFS SDK

### 📡 Usage

1. Replace `PATH_TO_SDK` in the `.csproj` with the actual location of `SimConnect.dll`
2. Run the app
3. Pi should send messages like:
   ```python
   sock.sendto(b"0.75", ("<PC_IP>", 49005))