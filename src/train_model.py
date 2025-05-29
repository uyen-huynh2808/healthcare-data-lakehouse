import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from imblearn.over_sampling import SMOTE
import joblib

# Load data
data = pd.read_csv("synthea_data/training_data.csv")

# Create age group from age column
bins = [0, 18, 35, 50, 65, 80, 120]
labels = ['0-17', '18-34', '35-49', '50-64', '65-79', '80+']
data['age_group'] = pd.cut(data['age'], bins=bins, labels=labels, right=False)

# One-hot encode age_group
age_group_cols = pd.get_dummies(data['age_group'], prefix='age_group')

# Combine one-hot columns with original data
data = pd.concat([data, age_group_cols], axis=1)

# Define the full feature list
feature_cols = list(age_group_cols.columns) + [
    'gender', 'body_mass_index', 'body_temperature', 'heart_rate',
    'systolic_blood_pressure', 'creatinine',
    'alanine_aminotransferase_[enzymatic_activity/volume]_in_serum_or_plasma',
    'glucose', 'hemoglobin_[mass/volume]_in_blood',
    'leukocytes_[#/volume]_in_blood_by_automated_count',
    'oxygen_saturation_in_arterial_blood'
]

# Fill gender and all other features with normal/placeholder values
data['gender'] = 0  # or 1, or better you can randomly assign if needed

normal_values = {
    'body_mass_index': 22.0,
    'body_temperature': 36.6,
    'heart_rate': 80,
    'systolic_blood_pressure': 120,
    'creatinine': 1.0,
    'alanine_aminotransferase_[enzymatic_activity/volume]_in_serum_or_plasma': 30,
    'glucose': 90,
    'hemoglobin_[mass/volume]_in_blood': 14.0,
    'leukocytes_[#/volume]_in_blood_by_automated_count': 7.0,
    'oxygen_saturation_in_arterial_blood': 98.0
}

for col, val in normal_values.items():
    data[col] = val

# Features and target
X = data[feature_cols]
y = data['is_ill']

print("Original label distribution:")
print(y.value_counts())

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# SMOTE only on training data
sm = SMOTE(random_state=42)
X_train_resampled, y_train_resampled = sm.fit_resample(X_train, y_train)

print("\nResampled label distribution (training only):")
print(pd.Series(y_train_resampled).value_counts())

# Train Random Forest
clf = RandomForestClassifier(random_state=42)
clf.fit(X_train_resampled, y_train_resampled)

# Predict and evaluate
y_pred = clf.predict(X_test)

print("\nModel Evaluation After SMOTE:")
print(classification_report(y_test, y_pred, digits=4))
print("Confusion Matrix:\n", confusion_matrix(y_test, y_pred))
print("Accuracy:", accuracy_score(y_test, y_pred))

# Save model
joblib.dump(clf, "models/illness_predictor.pkl")
print("Model saved as illness_predictor.pkl")
