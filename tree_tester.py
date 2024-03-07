import pandas as pd
import joblib

# Load the trained model from the file
tree_model = joblib.load("decision_tree_model.joblib")

# Prompt the user for input values
print("Please enter the following input values:")
bpm = float(input("Enter BPM (heart rate): "))
spo2 = float(input("Enter SpO2 (blood oxygen saturation): "))
drowsiness = float(input("Enter drowsiness level (0 for awake, 1 for drowsy): "))

# Create a DataFrame with input values and feature names
input_data = pd.DataFrame({
    'BPM': [bpm],
    'SpO2': [spo2],
    'drowsiness': [drowsiness]
})

# Make predictions using the loaded model
predicted_label = tree_model.predict(input_data)

# Map predicted label to corresponding diagnosis
diagnosis_map = {
    0: "healthy",
    1: "heart attack",
    2: "cardiac arrest",
    3: "hypothyroidism"
}

# Output the corresponding diagnosis based on the predicted label
print("Predicted diagnosis:", diagnosis_map[int(predicted_label.item())])
