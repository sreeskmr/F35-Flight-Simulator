import tkinter as tk
from tkinter import ttk, messagebox
import csv
import socket
import json
import pyvjoy
import subprocess
import os
import webbrowser
import threading
import subprocess
import paramiko
import threading
import requests
import time
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import ttk, messagebox
import select
import sys

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller .exe """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

# === CONFIG ===
PORT = 49000
MAX_BUTTONS = 29
DEVICE_ID = 1
BUTTON_LABELS = [
    "T1 - Cage/Uncage",
    "T2 - Left", "T2 - Right", "T2 - Up", "T2 - Down", "T2 - Center",
    "T3 - Up", "T3 - Down", "T3 - Left", "T3 - Right",
    "T4 - Accel", "T4 - Decel",
    "T5 - Chaff", "T5 - Flare", "T5 - Auto",
    "T6 - AutoSTO",
    "T8 - Scroll Up", "T8 - Scroll Down",
    "T9 - Top", "T9 - Center", "T9 - Bottom",
    "T10 - Button",
    "T11 - Standard", "T11 - NVG", "T11 - Off",
    "T12 - PitchOverride"
]

def send_pc_ip_to_pi(pi_ip, my_local_ip):
        import requests
        try:
            response = requests.post(f"http://{pi_ip}:8000/ip", data=my_local_ip)
            if response.status_code == 200:
                print("✅ Sent PC IP to Pi successfully.")
            else:
                print(f"⚠️ Failed to send IP. Status: {response.status_code}")
        except Exception as e:
            print(f"❌ Error sending PC IP: {e}")

class F35ThrottleGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("F-35 Throttle Control Panel")
        self.geometry("900x800")
        self.configure(bg="#D6D2C4")
        self.state("zoomed")

        self.j = None
        try:
            self.j = pyvjoy.VJoyDevice(DEVICE_ID)
            print("✅ vJoy device initialized.")
        except Exception as e:
            print(f"❌ Failed to connect to vJoy device {DEVICE_ID}: {e}")

        self.prev_buttons = [0] * MAX_BUTTONS
        self.last_gui_update = 0
        self.prev_throttle_display = -1
        self.prev_display_buttons = [None] * MAX_BUTTONS
        self.pi_connected = tk.StringVar(value="❌ No signal from Pi")
        self.rpi_ip = tk.StringVar(value="")
        self.pc_ip = tk.StringVar(value=self.get_local_ip())
        self.active_pi_ip = None
        self.last_packet_time = time.time()

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(("", PORT))
        self.sock.setblocking(False)

        self.throttle_var = tk.DoubleVar()
        self.button_widgets = []
        self.last_gui_update = 0


        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill='both', expand=True)

        self.throttle_state = tk.StringVar(value="Throttle State: Unknown")

        self.create_button_map_tab()
        self.create_button_status_tab()
        self.create_game_integration_tab()

        threading.Thread(target=self.listen_udp_loop, daemon=True).start()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)


    def listen_udp_loop(self):
        while True:
            try:
                rlist, _, _ = select.select([self.sock], [], [], 0.05)
                if rlist:
                    data, _ = self.sock.recvfrom(1024)
                    payload = json.loads(data.decode())
                    throttle = payload.get("throttle", 0.0)
                    buttons = payload.get("buttons", [0]*MAX_BUTTONS)
                    self.after(0, lambda: self.update_display(throttle, buttons))
                    self.last_packet_time = time.time()
            except Exception as e:
                print(f"Error in listen_udp_loop: {e}")



    def launch_ip_receiver(self):
        # Only for LOCAL TESTING — don't use in production
        if socket.gethostname() == "raspberrypi":
            if not hasattr(self, "ip_receiver_process") or self.ip_receiver_process.poll() is not None:
                script_path = os.path.join(os.path.dirname(__file__), "ip_receiver.py")
                self.ip_receiver_process = subprocess.Popen(
                    ["python3", script_path],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )


    def get_local_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "Unknown"


    def create_button_map_tab(self):
        outer_frame = ttk.Frame(self.notebook)
        self.notebook.add(outer_frame, text="Throttle Button Map")

        frame = self.create_scrollable_inner_frame(outer_frame)

        ttk.Label(frame, text="Throttle Button Map", font=("Segoe UI", 15, "bold"), foreground="#000000").pack(anchor="center", padx=10, pady=(10, 0))

        # === Style setup ===
        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Segoe UI", 13, "bold"))
        style.configure("Treeview", rowheight=28, font=("Segoe UI", 10))

        columns = ("ID", "Label", "Control Type", "Ideal Function", "Target Sim(s)")
        tree = ttk.Treeview(frame, columns=columns, show='headings', height=26)
        tree.pack(fill='both', expand=True)

        # Set up column headers and widths
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=180, anchor="center")

        # Tag styles
        tree.tag_configure("evenrow", background="#f0f0f0")  # Light gray
        tree.tag_configure("oddrow", background="#ffffff")   # White

        # === Set smaller font for Treeview ===
        style = ttk.Style()
        style.configure("Treeview", font=("Segoe UI", 8))
        style.configure("Treeview.Heading", font=("Segoe UI", 9, "bold"))

        # Load CSV
        try:
            with open(resource_path("F35_Throttle_Button_Map.csv"), newline='', encoding="utf-8-sig") as csvfile:
                reader = csv.reader(csvfile)
                next(reader)  # Skip header
                for i, row in enumerate(reader):
                    tag = "evenrow" if i % 2 == 0 else "oddrow"
                    tree.insert("", "end", values=row, tags=(tag,))
        except Exception as e:
            print(f"Error loading button map: {e}")


    def connect_and_run_on_pi(self):
        pi_ip = self.rpi_ip.get()
        if not pi_ip.strip():
            messagebox.showerror("Missing IP", "Please enter the Raspberry Pi's IP address.")
            return

        pi_user = "pi"
        pi_password = "pleasework"

        # Start IP receiver locally before connecting
        # self.launch_ip_receiver()

        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(pi_ip, username=pi_user, password=pi_password)

            # Kill any leftover Python scripts using GPIO
            ssh.exec_command("pkill -f send_inputs.py")
            ssh.exec_command("pkill -f ip_receiver.py")

            # Reset GPIO safely before rerunning
            ssh.exec_command("python3 -c 'import RPi.GPIO as GPIO; GPIO.setwarnings(False); GPIO.cleanup()'")

            ssh.exec_command("nohup python3 /home/pi/Desktop/F35-FS/testing/ip_receiver.py &")

            # Launch ip_receiver on the Pi first
            ssh.exec_command("nohup python3 /home/pi/Desktop/F35-FS/testing/ip_receiver.py &")

            # Send PC IP to Pi (via HTTP POST)
            my_local_ip = self.get_local_ip()
            send_pc_ip_to_pi(pi_ip, my_local_ip)

            # Now launch your script
            cmd = "python3 /home/pi/Desktop/F35-FS/testing/send_inputs.py"
            stdin, stdout, stderr = ssh.exec_command(cmd)
            errors = stderr.read().decode()

            if errors.strip():
                self.after(0, lambda: messagebox.showerror("Pi Error", f"Failed to run script:\n{errors}"))
            else:
                self.after(0, lambda: messagebox.showinfo("Success", "Script launched on Pi!"))
                self.active_pi_ip = pi_ip  # Remember Pi IP for use in on_closing()

            ssh.close()

        except Exception as e:
            import traceback
            traceback.print_exc()
            err_msg = str(e)
            self.after(0, lambda: messagebox.showerror("Connection Failed", f"Could not connect to Pi:\n{err_msg}"))


    def create_scrollable_inner_frame(self, parent):
        # Canvas inside the tab
        canvas = tk.Canvas(parent, background="#FFFFFF", highlightthickness=0)
        canvas.pack(side="left", fill="both", expand=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Actual content frame
        inner_frame = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=inner_frame, anchor="nw")

        # Resize scroll region as needed
        def on_config(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        inner_frame.bind("<Configure>", on_config)

        # Enable mousewheel
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        return inner_frame



    def create_button_status_tab(self):
        outer_frame = ttk.Frame(self.notebook)
        self.notebook.add(outer_frame, text="Button Status")

        frame = self.create_scrollable_inner_frame(outer_frame)
        ttk.Label(frame, text="Button Status Monitor", font=("Segoe UI", 12, "bold"), foreground="#000000").pack(anchor="w", padx=10, pady=(10, 0))

        default_font = ("Segoe UI", 10)

        # === IP CONFIG FRAME ===
        ip_frame = ttk.LabelFrame(frame, text="Network Configuration", padding=10)
        ip_frame.pack(pady=10, padx=10, fill="x")

        # --- Raspberry Pi IP ---
        ttk.Label(ip_frame, text="Raspberry Pi IP:", font=default_font).grid(row=0, column=0, sticky="e", padx=5, pady=2)
        self.rpi_ip_entry = ttk.Entry(ip_frame, textvariable=self.rpi_ip, width=18, font=default_font)
        self.rpi_ip_entry.grid(row=0, column=1, padx=5)
        self.rpi_ip_entry.bind("<Return>", lambda event: self.set_ips())

        ttk.Button(ip_frame, text="Set Pi IP", command=self.set_ips).grid(row=0, column=2, padx=5)

        # --- PC IP ---
        ttk.Label(ip_frame, text="PC IP (Receiver):", font=default_font).grid(row=1, column=0, sticky="e", padx=5, pady=2)
        self.pc_ip_entry = ttk.Entry(ip_frame, textvariable=self.pc_ip, width=18, font=default_font)
        self.pc_ip_entry.grid(row=1, column=1, padx=5)
        self.pc_ip_entry.bind("<Return>", lambda event: self.set_ips())

        ttk.Button(ip_frame, text="Set PC IP", command=self.set_ips).grid(row=1, column=2, padx=5)

        # --- Status Label ---
        self.status_label = ttk.Label(ip_frame, textvariable=self.pi_connected, font=default_font, foreground="green")
        self.status_label.grid(row=2, column=0, columnspan=3, pady=(5, 0))

        self.throttle_state_label = ttk.Label(frame, textvariable=self.throttle_state, font=default_font)
        self.throttle_state_label.pack(pady=(0, 10))


        # === GPIO RESET BUTTON ===
        ttk.Button(frame, text="🔄 Reset GPIO on Pi", command=self.reset_gpio_on_pi).pack(pady=10)

        # === THROTTLE BAR ===
        self.throttle_var = tk.DoubleVar()
        ttk.Label(frame, text="Throttle (%)", font=default_font).pack(pady=(10, 0))
        self.throttle_bar = ttk.Progressbar(frame, orient="horizontal", length=400, mode="determinate", variable=self.throttle_var, maximum=100)
        self.throttle_bar.pack(pady=(0, 20))

        # === BUTTON STATUS DISPLAY ===
        self.button_frame = ttk.Frame(frame)
        self.button_frame.pack()

        self.button_widgets = []
        for i, label in enumerate(BUTTON_LABELS):
            row, col = divmod(i, 2)
            lbl = ttk.Label(self.button_frame, text=label, background="gray", foreground="white", padding=5, width=28, anchor="w", font=default_font)
            lbl.grid(row=row, column=col, padx=5, pady=2, sticky="w")
            self.button_widgets.append(lbl)

        # === SOCKET SETUP ===
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(("", PORT))
        self.sock.setblocking(False)

        # self.poll_udp()


    def set_ips(self):
        if not self.rpi_ip.get().strip() or not self.pc_ip.get().strip():
            messagebox.showwarning("Missing IP", "Please enter both the Raspberry Pi IP and the PC Receiver IP.")
            return

        # Run the connection process in a background thread
        threading.Thread(target=self.connect_and_run_on_pi, daemon=True).start()


    def reset_gpio_on_pi(self):
        pi_ip = self.rpi_ip.get()
        pi_user = "pi"  # Adjust if needed
        pi_password = "pleasework"  # Adjust if needed

        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(pi_ip, username=pi_user, password=pi_password)

            # Send command to safely clean up GPIOs
            cleanup_cmd = (
                "python3 -c 'import RPi.GPIO as GPIO; GPIO.setwarnings(False); GPIO.cleanup()'"
            )
            stdin, stdout, stderr = ssh.exec_command(cleanup_cmd)
            errors = stderr.read().decode()
            if errors:
                self.after(0, lambda: messagebox.showerror("GPIO Reset Failed", errors))
            else:
                self.after(0, lambda: messagebox.showinfo("GPIO Reset", "✅ GPIO pins cleaned on Pi!"))
            ssh.close()
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.after(0, lambda: messagebox.showerror("Connection Error", f"Could not connect to Pi:\n{e}"))


    def on_closing(self):
        pi_ip = self.active_pi_ip or self.rpi_ip.get()
        pi_user = "pi"
        pi_password = "pleasework"

        if not pi_ip.strip():
            print("⚠️ No Pi IP set — skipping Pi cleanup.")
            self.destroy()
            return

        try:
            print(f"🔌 Connecting to Pi at {pi_ip} for cleanup...")
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(pi_ip, username=pi_user, password=pi_password)

            # Step 1: Check if scripts are running
            print("🔍 Checking for running scripts...")
            stdin, stdout, stderr = ssh.exec_command("pgrep -af send_inputs.py")
            running_scripts = stdout.read().decode().strip()
            print(f"send_inputs.py: {running_scripts or 'Not running'}")

            stdin, stdout, stderr = ssh.exec_command("pgrep -af ip_receiver.py")
            running_receiver = stdout.read().decode().strip()
            print(f"ip_receiver.py: {running_receiver or 'Not running'}")

            # Step 2: Kill scripts
            print("🛑 Killing scripts...")
            ssh.exec_command("pkill -f send_inputs.py")[1].channel.recv_exit_status()
            ssh.exec_command("pkill -f ip_receiver.py")[1].channel.recv_exit_status()

            # Step 3: Clean GPIOs
            print("🧹 Cleaning up GPIO...")
            stdin, stdout, stderr = ssh.exec_command("python3 -c 'import RPi.GPIO as GPIO; GPIO.setwarnings(False); GPIO.cleanup()'")
            gpio_errors = stderr.read().decode().strip()
            if gpio_errors:
                print(f"⚠️ GPIO cleanup error: {gpio_errors}")
            else:
                print("✅ GPIO cleanup complete.")

            ssh.close()
            print("✅ SSH session closed. Cleanup complete.")

        except Exception as e:
            print(f"❌ Exception during cleanup: {e}")

        # Always destroy the GUI
        self.destroy()


    def update_display(self, throttle, buttons):
        now = time.time()
        if now - self.last_gui_update < 0.03:
            return
        self.last_gui_update = now

        if throttle != self.prev_throttle_display:
            self.throttle_var.set(throttle)
            self.prev_throttle_display = throttle
            # Update throttle state text
            if throttle < 5:
                self.throttle_state.set("Throttle State: IDLE")
            elif 5 <= throttle < 80:
                self.throttle_state.set(f"Throttle State: {int(throttle)}% - Cruise")
            elif 80 <= throttle < 95:
                self.throttle_state.set("Throttle State: MIL POWER")
            else:
                self.throttle_state.set("Throttle State: AFTERBURNER")


        for i, state in enumerate(buttons[:MAX_BUTTONS]):
            new_color = "green" if state else "gray"
            if self.prev_display_buttons[i] != state:
                self.button_widgets[i].configure(background=new_color)
                self.prev_display_buttons[i] = state

        self.set_vjoy_throttle(throttle)
        self.set_vjoy_buttons(buttons)

        self.pi_connected.set("✅ Receiving from Pi" if now - self.last_packet_time <= 1 else "❌ No signal from Pi")


    def set_vjoy_buttons(self, buttons):
        if not self.j:
            return
        for i, state in enumerate(buttons[:MAX_BUTTONS]):
            if state != self.prev_buttons[i]:
                self.j.set_button(i + 1, state)
                self.prev_buttons[i] = state

    def set_vjoy_throttle(self, throttle_percent):
        if not self.j:
            return
        value = int((throttle_percent / 100.0) * 32768)
        self.j.set_axis(pyvjoy.HID_USAGE_Z, value)


    def create_game_integration_tab(self):
        outer_frame = ttk.Frame(self.notebook)
        self.notebook.add(outer_frame, text="Game Integration")

        frame = self.create_scrollable_inner_frame(outer_frame)

        # Font and style setup
        body_font = ("Segoe UI", 10)
        heading_font = ("Segoe UI", 12, "bold")
        title_font = ("Segoe UI", 13, "bold")

        style = ttk.Style()
        style.configure("Custom.TButton", font=body_font, padding=8)
        style.map("Custom.TButton",
            background=[("!disabled", "#e0e0e0"), ("active", "#c8c8c8")],
            foreground=[("!disabled", "#000000")]
        )

        # Info Frame
        info_frame = ttk.Frame(frame, padding=10)
        info_frame.pack(fill="both", expand=True)

        # Section Title
        ttk.Label(info_frame, text="Simulator Setup Guide", font=title_font).pack(anchor="w", pady=(0, 5))

        # Instructions block
        text_lines = [
            ("Your F-35 Throttle is automatically recognized as a standard joystick by most simulators.\n"
             "You can bind buttons and the throttle axis using the in-game control menus.\n\n"
             "Step 1: Install vJoy by clicking the button below.\n"
             "Step 2: Open the vJoy Configuration Tool and match your settings to the example shown.\n"
             "Step 3: Enter the Raspberry Pi's IP address in the Button Status tab (PC's IP should be automatically entered).\n\n"
             "Open a simulation software and bind the buttons to the appropriate buttons/switches!\n", body_font),

            ("\nMicrosoft Flight Simulator 2020:", heading_font),
            ("Go to Options → Controls → vJoy Device\n", body_font),

            ("\nDCS World:", heading_font),
            ("Go to Options → Controls and search for JOY_BTNx bindings\n", body_font),

            ("\nX-Plane:", heading_font),
            ("Go to Settings → Joystick and configure vJoy as a joystick input\n", body_font),

            ("\nNo SimConnect, Lua scripts, or SDK integration is required for button/axis input.", body_font),
        ]

        for text, font in text_lines:
            ttk.Label(info_frame, text=text, font=font, wraplength=800, justify="left").pack(anchor="w", pady=(0, 4))

        # Buttons
        button_frame = ttk.Frame(info_frame)
        button_frame.pack(pady=(10, 0))

        def launch_vjoy_config():
            path = r"C:\Program Files\vJoy\x64\vJoyConf.exe"
            if os.path.exists(path):
                subprocess.Popen([path], shell=True)
            else:
                messagebox.showerror("Error", f"vJoy configuration tool not found at:\n{path}")

        def open_vjoy_download():
            webbrowser.open("https://sourceforge.net/projects/vjoystick/")

        ttk.Button(button_frame, text="Open vJoy Configuration Tool", command=launch_vjoy_config, style="Custom.TButton").grid(row=0, column=1, padx=10)
        ttk.Button(button_frame, text="Download vJoy from SourceForge", command=open_vjoy_download, style="Custom.TButton").grid(row=0, column=0, padx=10)

        # === vJoy Settings Image and Caption ===
        image_frame = ttk.Frame(info_frame)
        image_frame.pack(pady=35)

        try:
            vjoy_img = Image.open(resource_path("vjoy-config.png"))
            vjoy_img = vjoy_img.resize((320, 425), Image.Resampling.LANCZOS)
            self.vjoy_photo = ImageTk.PhotoImage(vjoy_img)
            ttk.Label(image_frame, image=self.vjoy_photo).pack()
        except Exception as e:
            print("⚠️ Failed to load vjoy image:", e)



if __name__ == "__main__":
    app = F35ThrottleGUI()
    app.mainloop()