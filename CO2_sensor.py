import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import serial
import serial.tools.list_ports
import threading
import time
import csv
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collections import deque

# todo : =============================================< Serial Read Data >=============================================
# * --------------------------------------------< Config >--------------------------------------------
baudrate = 9600
data_queue = deque(maxlen=150)
ser = None
running = False
recording = False

#  ____________________________< Serial read >____________________________
def list_serial_ports():
    ports = serial.tools.list_ports.comports()
    return [port.device for port in ports]

def connect_serial():
    global ser
    try:
        if ser and ser.is_open:
            ser.close()
        ser = serial.Serial(selected_port.get(), baudrate)
    except Exception as e:
        print(f"Error: {e}")

def read_serial():
    global running
    while running:
        try:
            if ser and ser.in_waiting:
                line = ser.readline().decode().strip()
                value = int(line)
                data_queue.append(value)
        except:
            pass

# todo : =============================================< GUI elements >=============================================
# * --------------------------------------------< Initail >--------------------------------------------
root = tk.Tk()
root.title("Real Time CO2 Measuring")
root.geometry("1920x1080")  # ✅ Fix screen size
root.configure(bg="#f5f5f5")

selected_port = tk.StringVar()
interval_var = tk.StringVar(value="1 second")
latest_value = tk.StringVar(value="--- PPM")

#  ____________________________< Title >____________________________
tk.Label(root, text="Real Time CO2 measuring", font=("poppins", 27, "bold"), bg="#f5f5f5").place(x=50, y=30)

#  ____________________________< Graph container >____________________________
graph_frame = tk.Frame(root, width=600, height=430, bg="white", highlightbackground="gray", highlightthickness=0)
graph_frame.place(x=50, y=110)

fig, ax = plt.subplots(figsize=(6, 4.3))  # ✅ Fit to frame
line, = ax.plot([], [], 'm.-')
ax.set_ylim(0, 120)  # ✅ y-axis 0–120
ax.set_xlim(0, 150)
ax.set_ylabel("PPM")
ax.set_xlabel("Time")
ax.grid(True)

canvas = FigureCanvasTkAgg(fig, master=graph_frame)
canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
dt = 50

def update_plot():
    if data_queue:
        y = list(data_queue)
        x = list(range(len(y)))
        line.set_data(x, y)
        ax.set_xlim(0, max(150, len(y)))
        ax.set_ylim(0, 120)
        canvas.draw()
        latest_value.set(f"{y[-1]} PPM")
    root.after(dt, update_plot)

#  ____________________________< Select serial port >____________________________
tk.Label(root, text="• Select Device:", font=("poppins", 18), bg="#f5f5f5").place(x=870, y=63)

ports = list_serial_ports()
port_menu = ttk.Combobox(root, textvariable=selected_port, values=ports, width=22, state="readonly")
port_menu.place(x=1025, y=70)
port_menu.set("Select serial port ...")
port_menu.bind("<<ComboboxSelected>>", lambda e: connect_serial())

#  ____________________________< Real time value >____________________________
tk.Label(root, text="Real time parameter", font=("poppins", 28), bg="#f5f5f5").place(x=1290, y=100)
ppm_label = tk.Label(
    root,
    textvariable=latest_value,
    font=("poppins", 76),
    bg="white",
    width=12,
    height=1,         # ✅ เพิ่มความสูงของกรอบ (หน่วย = บรรทัด)
    anchor="center"   # ✅ จัดให้อยู่กึ่งกลางทั้งแนวตั้งและแนวนอน
)
ppm_label.place(x=1290, y=160)

# Record interval label + dropdown
tk.Label(root, text="Record time stamp", font=("Helvetica", 14), bg="#f5f5f5").place(x=850, y=260)
interval_menu = ttk.Combobox(root, textvariable=interval_var, values=["1 second", "2 seconds", "3 seconds"], width=12, state="readonly")
interval_menu.place(x=850, y=300)

# Record Button
tk.Button(root, text="Record", font=("Helvetica", 16), bg="lime green", command=lambda: threading.Thread(target=record_data_delay, daemon=True).start()).place(x=980, y=295)

# CSV hint
tk.Label(root, text="The recorded data will be exported in CSV file format.", font=("Helvetica", 10), bg="#f5f5f5", fg="gray").place(x=850, y=340)

# ===================== RECORD FUNCTION =====================
def record_data_delay():
    global recording
    recording = True
    try:
        delay_sec = int(interval_var.get().split()[0])
        messagebox.showinfo("Recording", f"Recording... Please wait {delay_sec} seconds.")
        time.sleep(delay_sec)

        if not data_queue:
            messagebox.showwarning("No data", "No data available to record.")
            return

        val = data_queue[-1]
        filename = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if not filename:
            return

        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Timestamp", "PPM"])
            writer.writerow([time.strftime('%Y-%m-%d %H:%M:%S'), val])

        messagebox.showinfo("Saved", f"Data saved successfully:\n{filename}")

    except Exception as e:
        messagebox.showerror("Error", str(e))
    finally:
        recording = False

# ===================== START LOOP =====================
running = True
threading.Thread(target=read_serial, daemon=True).start()
update_plot()
root.mainloop()