import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
import joblib

# Load the combined data from the CSV file
combined_data = pd.read_csv("labeled_data.csv")

# Separate features (X) and target variable (y)
X = combined_data.drop(columns=['label'])  # Exclude the 'label' column
y = combined_data['label']

# Split the data into training and testing sets (80% train, 20% test)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Initialize and train the Decision Tree Classifier model
dt_model = DecisionTreeClassifier(random_state=42)
dt_model.fit(X_train, y_train)

# Evaluate model performance (accuracy)
accuracy = dt_model.score(X_test, y_test)
print("Accuracy of Decision Tree Classifier:", accuracy)

# Save the trained model to a file
model_file = "decision_tree_model.joblib"
joblib.dump(dt_model, model_file)
print("Trained Decision Tree Classifier model saved to:", model_file)
