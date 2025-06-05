import tkinter as tk
from tkinter import scrolledtext, filedialog
import RPi.GPIO as GPIO
import spidev
import time
from threading import Thread
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

digital_pins = {
    "T1_Button1": 0,
    "T1_Button2": 1,
    "T2_Dir1": 12,
    "T2_Dir2": 13,
    "T2_Dir3": 14,
    "T2_Dir4": 15,
    "T2_Center": 16,
    "T6": 2,
    "T7_Button1": 17,
    "T7_Button2": 18,
    "T7_Button3": 19,
    "T7_Button4": 20,
    "T7_Button5": 21,
    "T10_Button1": 3,
    "T10_Button2": 4,
    "T11": 5,
    "T12": 6,
    "T8": 7
}

analog_channels = {
    "T3_X": 0,
    "T3_Y": 1,
    "T4": 4,
    "T3_Z": 7
}

class LoggerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Enhanced Button & Analog Monitor")

        self.running = False
        self.log_to_file = tk.BooleanVar(value=False)
        self.analog_history = {key: [] for key in analog_channels}
        self.max_points = 50

        self.log_filename = "enhanced_log.csv"

        self.status_label = tk.Label(root, text="Status: Stopped", fg="red", font=("Arial", 12, "bold"))
        self.status_label.pack()

        controls = tk.Frame(root)
        controls.pack()

        self.start_button = tk.Button(controls, text="Start", command=self.start_monitoring, bg="green", fg="white", width=10)
        self.start_button.grid(row=0, column=0, padx=5)

        self.stop_button = tk.Button(controls, text="Stop", command=self.stop_monitoring, bg="red", fg="white", width=10)
        self.stop_button.grid(row=0, column=1, padx=5)

        self.log_check = tk.Checkbutton(controls, text="Log to file", variable=self.log_to_file)
        self.log_check.grid(row=0, column=2, padx=5)

        self.analog_frame = tk.LabelFrame(root, text="Analog Readings")
        self.analog_frame.pack(padx=10, pady=5, fill="x")

        self.analog_labels = {}
        for name in analog_channels:
            label = tk.Label(self.analog_frame, text=f"{name}: 0")
            label.pack(anchor="w")
            self.analog_labels[name] = label

        self.log_box = scrolledtext.ScrolledText(root, width=60, height=12, state="disabled")
        self.log_box.pack(padx=10, pady=5)

        self.fig, self.ax = plt.subplots(figsize=(5, 2.5))
        self.canvas = FigureCanvasTkAgg(self.fig, master=root)
        self.canvas.get_tk_widget().pack(pady=5)
        self.lines = {key: self.ax.plot([], [], label=key)[0] for key in analog_channels}
        self.ax.legend(loc='upper right')
        self.ax.set_ylim(0, 1023)
        self.ax.set_xlim(0, self.max_points)

        self.setup_gpio()
        self.last_states = {name: GPIO.input(pin) for name, pin in digital_pins.items()}

    def setup_gpio(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        for pin in digital_pins.values():
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        self.spi = spidev.SpiDev()
        self.spi.open(0, 0)
        self.spi.max_speed_hz = 1350000

    def read_adc(self, channel):
        result = self.spi.xfer2([1, (8 + channel) << 4, 0])
        return ((result[1] & 3) << 8) + result[2]

    def start_monitoring(self):
        if not self.running:
            self.running = True
            self.status_label.config(text="Status: Running", fg="green")
            self.monitor_thread = Thread(target=self.monitor_loop, daemon=True)
            self.monitor_thread.start()

    def stop_monitoring(self):
        self.running = False
        self.status_label.config(text="Status: Stopped", fg="red")

    def monitor_loop(self):
        while self.running:
            timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]

            for name, pin in digital_pins.items():
                current = GPIO.input(pin)
                if current != self.last_states[name]:
                    self.last_states[name] = current
                    if current == GPIO.LOW:
                        self.flash_button(name)
                        self.log_event(f"[{timestamp}] {name} pressed", log_file=True)

            for name, ch in analog_channels.items():
                val = self.read_adc(ch)
                self.analog_labels[name].config(text=f"{name}: {val}")
                self.analog_history[name].append(val)
                if len(self.analog_history[name]) > self.max_points:
                    self.analog_history[name].pop(0)
                self.log_event(f"[{timestamp}] {name}: {val}", log_file=True)

            self.update_graph()
            time.sleep(0.2)

    def update_graph(self):
        for name, line in self.lines.items():
            y_data = self.analog_history[name]
            x_data = list(range(len(y_data)))
            line.set_data(x_data, y_data)
        self.ax.relim()
        self.ax.autoscale_view(True, True, True)
        self.canvas.draw()

    def flash_button(self, name):
        self.log_event(f"{name} flash!", log_file=False)

    def log_event(self, message, log_file=True):
        self.log_box.config(state="normal")
        self.log_box.insert(tk.END, message + "\n")
        self.log_box.see(tk.END)
        self.log_box.config(state="disabled")

        if self.log_to_file.get() and log_file:
            with open(self.log_filename, "a") as file:
                file.write(message + "\n")

    def on_close(self):
        self.stop_monitoring()
        self.spi.close()
        GPIO.cleanup()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    gui = LoggerGUI(root)
    root.protocol("WM_DELETE_WINDOW", gui.on_close)
    root.mainloop()