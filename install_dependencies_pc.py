import subprocess
import sys
import platform

# List of required packages
packages = [
    "pyvjoy",
    "paramiko",
    "requests",
    "Pillow",
]

# Add Pi-only packages if running on ARM
machine = platform.machine().lower()
if "arm" in machine or "aarch64" in machine:
    packages += ["RPi.GPIO", "spidev"]

def install(package):
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ Installed: {package}")
    except subprocess.CalledProcessError:
        print(f"❌ Failed to install: {package}")

print("📦 Installing required packages...\n")
for pkg in packages:
    install(pkg)

print("\n🎉 All done!")
