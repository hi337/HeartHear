# Drowsy detection interface with visual representation of EOG signals coming from Ardunio as well as printing result 

import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import serial

# Function to calculate SpO2 based on red and IR signal amplitudes
def calculate_spo2(red_ratio, ir_ratio):
    # Coefficients for the empirical formula
    a = -45.060
    d = 30.354
    
    # Calculate SpO2 using the formula
    spo2 = (a * (red_ratio) / (ir_ratio) * (red_ratio) / (ir_ratio)) + (d*(red_ratio) / (ir_ratio)) + 94.845

    return str(spo2)

# Function to read data from serial and update GUI
def update_data():
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

            
            # print ppg values
            if (int(irValue) > 50000):
                ppg_signal.config(text="Ir Value: " + str(irValue) + ", Heart Rate (BPM): " + heartRate + ", SpO2: " + calculate_spo2(redValue, irValue))
            else:
                ppg_signal.config(text="Glasses are Off!")
            

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
