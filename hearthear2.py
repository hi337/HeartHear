import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import serial

# Global buffers for data
red_values = []
ir_values = []

# Function to calculate SpO2 based on red and IR signal amplitudes
def calculate_spo2():
    global red_values, ir_values
    
    # Check if there is enough data
    if len(red_values) < 150 or len(ir_values) < 150:
        return 100  # Return 100 when not enough data

    # get the mean of the Red and IR
    red_dc = sum(red_values[:150]) / 150
    ir_dc = sum(ir_values[:150]) / 150

    # get the ac content
    red_ac = max(red_values[:150]) - min(red_values[:150])
    ir_ac = max(ir_values[:150]) - min(ir_values[:150])

    # Calculate R and SpO2
    R = (red_ac / red_dc) / (ir_ac / ir_dc)
    spo2 = 110 - 25 * R
    
    return spo2

# Function to read data from serial and update GUI
def update_data():
    global red_values, ir_values
    try:
        if ser.in_waiting > 0:
            line = ser.readline().decode().strip().split()
            signal = float(line[0])
            drowsiness = int(line[1])
            irValue = float(line[2])
            redValue = float(line[3])
            heartRate = str(line[4])
            
            # ecgbpm = int(line[4])

            # eog signal
            eog_signal.config(text="EOG signal: " + str(signal))

            # Update drowsiness status
            if drowsiness == 1:
                drowsiness_label.config(text="Drowsy")
            elif drowsiness == 0:
                drowsiness_label.config(text="Awake")

            # Append red and IR values to global arrays only if glasses are on
            if int(irValue) > 50000:
                red_values.append(redValue)
                ir_values.append(irValue)
                # Keep the array length to a maximum of 150
                if len(red_values) > 150:
                    red_values.pop(0)
                if len(ir_values) > 150:
                    ir_values.pop(0)
            
            # Calculate SpO2
            spo2_value = calculate_spo2()

            # Update GUI
            if int(irValue) > 50000:
                ppg_signal.config(text="Ir Value: " + str(irValue) + ", Heart Rate (BPM): " + heartRate + ", SpO2: " + str(spo2_value))
            else:
                drowsiness_label.config(text="Glasses are Off!")
                ppg_signal.config(text="Glasses are Off!")
                eog_signal.config(text="Glasses are Off!")

            # ecg_signal.config(text=ecgbpm)


    except Exception as e:
        print("Error:", e)

    root.after(10, update_data)  # Read serial data every 10 milliseconds

# Create serial connection
ser = serial.Serial('COM3', baudrate=115200)

# Create GUI window
root = tk.Tk()
root.title("EOG Signal and Drowsiness Detection")

# Create label to display drowsiness status
eog_signal = tk.Label(root, text="", font=("Helvetica", 40))
eog_signal.pack(pady=10)

drowsiness_label = tk.Label(root, text="", font=("Helvetica", 40))
drowsiness_label.pack(pady=10)

ppg_signal = tk.Label(root, text="", font=("Helvetica", 40))
ppg_signal.pack(pady=10)

ecg_signal = tk.Label(root, text="", font=("Helvetica", 40))
ecg_signal.pack(pady=10)

# Start updating data
update_data()

# Run the GUI
root.mainloop()

# Close serial connection when GUI is closed
ser.close()
