import csv
import random

# Define the number of data entries
num_entries = 500

# Define the healthy ranges for BPM and SpO2
bpm_range = (200, 500)
spo2_range = (0, 93)

# Open a CSV file for writing
with open('cardiac_arrest.csv', 'w', newline='') as csvfile:
    # Define column names
    fieldnames = ['BPM', 'SpO2', 'drowsiness', 'label']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    
    # Write the header row
    writer.writeheader()
    
    # Generate and write data entries
    for _ in range(num_entries):
        # Generate random values within healthy ranges
        bpm = random.randint(bpm_range[0], bpm_range[1])
        spo2 = random.randint(spo2_range[0], spo2_range[1])
        
        # Set drowsiness to 0 for healthy person
        drowsiness = 1
        
        # Set label to 0 for healthy person
        label = 2
        
        # Write the data entry to the CSV file
        writer.writerow({'BPM': bpm, 'SpO2': spo2, 'drowsiness': drowsiness, 'label': label})
