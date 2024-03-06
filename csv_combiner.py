import os
import csv
import random

# Path to the folder containing CSV files
folder_path = "data"

# List to store data from all CSV files
combined_data = []

# Iterate through all files in the folder
for file_name in os.listdir(folder_path):
    if file_name.endswith('.csv'):
        file_path = os.path.join(folder_path, file_name)
        # Open each CSV file and append its data to combined_data
        with open(file_path, 'r', newline='') as csvfile:
            reader = csv.reader(csvfile)
            # Skip the header row
            next(reader)
            # Append data from the current file to combined_data
            combined_data.extend(list(reader))

# Shuffle the combined data randomly
random.shuffle(combined_data)

# Write the shuffled data to a new CSV file
output_file = "labeled_data.csv"
with open(output_file, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    # Write a header row with column names (assuming the first file has the correct column names)
    writer.writerow(combined_data[0])
    # Write the shuffled data to the file
    writer.writerows(combined_data[1:])

print("Combined data saved to:", output_file)
