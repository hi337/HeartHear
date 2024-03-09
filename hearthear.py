import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import serial
import pandas as pd
import joblib
import numpy as np

# Global buffers for data
red_values = []
ir_values = []

# Import and load decision tree classifier
tree_model = joblib.load("decision_tree_model.joblib")

# Map predicted label to corresponding diagnosis
diagnosis_map = {
    0: "healthy",
    1: "heart attack",
    2: "cardiac arrest",
    3: "hypothyroidism/bradycardia"
}

# Function to calculate SpO2 based on red and IR signal amplitudes
def calculate_spo2():
    global red_values, ir_values
    
    # Check if there is enough data
    if len(red_values) < 200 or len(ir_values) < 200:
        return 100  # Return 100 when not enough data

    # get the mean of the Red and IR
    red_dc = np.mean(red_values[:200])
    ir_dc = np.mean(ir_values[:200])

    # get the ac content
    red_ac = max(red_values[:200]) - min(red_values[:200])
    ir_ac = max(ir_values[:200]) - min(ir_values[:200])

    # Calculate R and SpO2
    R = (red_ac / red_dc) / (ir_ac / ir_dc)
    spo2 = 110 - 25 * R
    
    return (spo2 if spo2 <= 100 and spo2 >= 0 else 100)

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
                

            # Update GUI only when glasses are on
            if int(irValue) > 50000:
                # Update arrays for spo2 calculation
                red_values.append(redValue)
                ir_values.append(irValue)
                # Keep the array length to a maximum of 200
                if len(red_values) > 200:
                    red_values.pop(0)
                if len(ir_values) > 200:
                    ir_values.pop(0)

                # Calculate SpO2
                spo2_value = int(calculate_spo2())

                # Update PPG
                ppg_signal.config(text="Ir Value: " + str(irValue) + ", Red Value: " + str(redValue) + ", SpO2: " + str(spo2_value))

                # update eog signal
                eog_signal.config(text="EOG signal: " + str(signal) + ", Awake or Drowsy?: " + ("Drowsy" if drowsiness == 1 else "Awake"))

                # Update ECG signal
                ecg_signal.config(text="Heart Rate (BPM): " + heartRate)

                # Make predictions using the loaded model
                predicted_label = tree_model.predict(pd.DataFrame({
                    'BPM': [heartRate],
                    'SpO2': [spo2_value],
                    'drowsiness': [drowsiness]
                }))

                #Update predicted outcome
                predicted_outcome.config(text="Predicted outcome: " + diagnosis_map[int(predicted_label.item())])

            else:
                ppg_signal.config(text="Glasses are Off!")
                eog_signal.config(text="Glasses are Off!")
                ecg_signal.config(text="Glasses are Off!")
                predicted_outcome.config(text="Glasses are Off!")


    except Exception as e:
        print("Error:", e)

    root.after(10, update_data)  # Read serial data every 10 milliseconds

# Create serial connection
ser = serial.Serial('COM3', baudrate=115200)

# Create GUI window
root = tk.Tk()
root.title("EOG Signal and Drowsiness Detection")

# Configure background color
root.configure(bg="white")

# Add logo image at the top
logo_image = tk.PhotoImage(file=".//pics//logo.png")
logo_label = tk.Label(root, image=logo_image, bg="white")
logo_label.pack(pady=10)

# Create labels to display sensory data and results
eog_signal = tk.Label(root, text="", font=("Helvetica", 40), fg="#1654b8", bg="#ff7573")
eog_signal.pack(pady=10)

ppg_signal = tk.Label(root, text="", font=("Helvetica", 40), fg="#1654b8", bg="#ff7573")
ppg_signal.pack(pady=10)

ecg_signal = tk.Label(root, text="", font=("Helvetica", 40), fg="#1654b8", bg="#ff7573")
ecg_signal.pack(pady=10)

predicted_outcome = tk.Label(root, text="", font=("Helvetica", 40), fg="#1654b8", bg="#ff7573")
predicted_outcome.pack(pady=10)

# Start updating data
update_data()

# Run the GUI
root.mainloop()

# Close serial connection when GUI is closed
ser.close()
