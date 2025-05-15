import tkinter as tk
from tkinter import messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import threading
import time
from sensor_reader import (
    get_throttle_position,
    get_force_reading,
    zero_load_cell,
    reset_throttle_range,
    init_sensors
)
from logger import start_logging, stop_logging

class F35GUI:
    def __init__(self, root):
        self.root = root
        self.root.title("F-35 Throttle Interface")
        self.root.geometry("600x600")
        self.running = True
        self.logging = False

        init_sensors()

        # Labels
        self.throttle_label = tk.Label(root, text="Throttle Position: --", font=("Arial", 14))
        self.throttle_label.pack(pady=5)

        self.force_label = tk.Label(root, text="Load Cell Reading: --", font=("Arial", 14))
        self.force_label.pack(pady=5)

        # Buttons
        tk.Button(root, text="Zero Load Cell", command=zero_load_cell).pack(pady=5)
        tk.Button(root, text="Reset Throttle Range", command=reset_throttle_range).pack(pady=5)

        self.log_btn = tk.Button(root, text="Start Logging", command=self.toggle_logging)
        self.log_btn.pack(pady=5)

        self.status_label = tk.Label(root, text="Status: Initializing", fg="orange", font=("Arial", 12))
        self.status_label.pack(pady=5)

        # Plotting
        self.fig, self.ax = plt.subplots()
        self.ax.set_title("Real-Time Sensor Plot")
        self.ax.set_xlabel("Time (s)")
        self.ax.set_ylabel("Sensor Value")

        self.plot_throttle, = self.ax.plot([], [], label="Throttle (%)")
        self.plot_force, = self.ax.plot([], [], label="Force (kg/N)")
        self.ax.legend()

        self.canvas = FigureCanvasTkAgg(self.fig, master=root)
        self.canvas.get_tk_widget().pack(pady=10)

        self.timestamps = []
        self.throttle_data = []
        self.force_data = []
        self.start_time = time.time()

        # Background thread
        self.update_thread = threading.Thread(target=self.update_loop)
        self.update_thread.daemon = True
        self.update_thread.start()

    def update_loop(self):
        while self.running:
            try:
                throttle = get_throttle_position()
                force = get_force_reading()

                self.throttle_label.config(text=f"Throttle Position: {throttle:.2f}")
                self.force_label.config(text=f"Load Cell Reading: {force:.2f}")
                self.status_label.config(text="Status: Connected", fg="green")

                if self.logging:
                    start_logging(throttle, force)

                t = time.time() - self.start_time
                self.timestamps.append(t)
                self.throttle_data.append(throttle)
                self.force_data.append(force)

                self.plot_throttle.set_data(self.timestamps, self.throttle_data)
                self.plot_force.set_data(self.timestamps, self.force_data)
                self.ax.relim()
                self.ax.autoscale_view()
                self.canvas.draw()

            except Exception as e:
                self.status_label.config(text=f"Status: Error - {str(e)}", fg="red")
                init_sensors()  # Try reconnecting

            time.sleep(0.1)

    def toggle_logging(self):
        self.logging = not self.logging
        self.log_btn.config(text="Stop Logging" if self.logging else "Start Logging")
        if not self.logging:
            stop_logging()

    def on_close(self):
        self.running = False
        stop_logging()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    gui = F35GUI(root)
    root.protocol("WM_DELETE_WINDOW", gui.on_close)
    root.mainloop()
