import subprocess
import sys

# Raspberry Pi–specific and shared packages
packages = [
    "RPi.GPIO",
    "spidev",
    "requests"
]

def install(package):
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ Installed: {package}")
    except subprocess.CalledProcessError:
        print(f"❌ Failed to install: {package}")

print("📦 Installing Raspberry Pi dependencies...\n")
for pkg in packages:
    install(pkg)

print("\n🎉 Raspberry Pi setup complete!")
