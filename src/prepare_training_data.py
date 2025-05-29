import pandas as pd

# Load datasets
patients = pd.read_csv("synthea_data/patients.csv")
conditions = pd.read_csv("synthea_data/conditions.csv")
observations = pd.read_csv("synthea_data/observations.csv")

# Convert dates to datetime
patients['BIRTHDATE'] = pd.to_datetime(patients['BIRTHDATE'])
observations['DATE'] = pd.to_datetime(observations['DATE'])

# Extract and pivot numeric observations
numeric_obs = observations[observations['TYPE'] == 'numeric'].copy()
numeric_obs['VALUE'] = pd.to_numeric(numeric_obs['VALUE'], errors='coerce')
numeric_obs = numeric_obs.dropna(subset=['VALUE'])

pivoted_obs = numeric_obs.pivot_table(
    index=['PATIENT', 'DATE'],
    columns='DESCRIPTION',
    values='VALUE',
    aggfunc='first'
).reset_index()

# Clean column names (lowercase, underscores)
pivoted_obs.columns = ['PATIENT', 'DATE'] + [col.replace(" ", "_").lower() for col in pivoted_obs.columns[2:]]

# Get latest exam date per patient for numeric observations
latest_exam = pivoted_obs.groupby('PATIENT')['DATE'].max().reset_index()
latest_exam.columns = ['Id', 'latest_exam_date']

# Get latest observation date per patient (all observations)
latest_obs = observations.groupby('PATIENT')['DATE'].max().reset_index()
latest_obs.rename(columns={'PATIENT': 'Id', 'DATE': 'latest_obs_date'}, inplace=True)

# Merge latest observation date into patients
patients = patients.merge(latest_obs, on='Id', how='left')

# Merge latest numeric exam date and pivoted numeric observations into patients
patients = patients.merge(latest_exam, on='Id', how='left')
patients = patients.merge(pivoted_obs, left_on=['Id', 'latest_exam_date'], right_on=['PATIENT', 'DATE'], how='left')

# Fill missing observation date with today
patients['latest_obs_date'] = patients['latest_obs_date'].fillna(pd.Timestamp('today'))

# Convert to timezone-naive
patients['latest_obs_date'] = pd.to_datetime(patients['latest_obs_date']).dt.tz_localize(None)
patients['latest_exam_date'] = pd.to_datetime(patients['latest_exam_date']).dt.tz_localize(None)
patients['BIRTHDATE'] = pd.to_datetime(patients['BIRTHDATE']).dt.tz_localize(None)

# Calculate age
patients['age'] = (patients['latest_obs_date'] - patients['BIRTHDATE']).dt.days // 365

# Drop unnecessary columns
patients = patients.drop(columns=[
    'DEATHDATE', 'SSN', 'DRIVERS', 'PASSPORT', 'PREFIX', 'FIRST', 'LAST',
    'SUFFIX', 'MAIDEN', 'MARITAL', 'RACE', 'ETHNICITY', 'BIRTHPLACE',
    'ADDRESS', 'CITY', 'STATE', 'COUNTY', 'ZIP', 'LAT', 'LON',
    'PATIENT', 'DATE', 'latest_obs_date', 'latest_exam_date'
], errors='ignore')

# Keep only PATIENT in conditions
conditions = conditions[['PATIENT']]

# Create binary condition flag per patient
condition_flags = conditions.groupby('PATIENT').size().reset_index(name='has_condition')
condition_flags['has_condition'] = 1

# Merge condition flag into patients
merged = patients.copy()
merged = merged.merge(condition_flags.rename(columns={'PATIENT': 'Id'}), on='Id', how='left')

# Fill missing flag with 0
merged['has_condition'] = merged['has_condition'].fillna(0)

# Label creation based on condition flag only
merged['is_ill'] = (merged['has_condition'] > 0).astype(int)

# Encode gender
merged['gender'] = merged['GENDER'].map({'M': 0, 'F': 1})
merged = merged.drop(columns=['GENDER'])

# Feature columns
feature_cols = [
    'age',
    'gender',
    'body_mass_index',
    'body_temperature',
    'heart_rate',
    'systolic_blood_pressure',
    'creatinine',
    'alanine_aminotransferase_[enzymatic_activity/volume]_in_serum_or_plasma',
    'glucose',
    'hemoglobin_[mass/volume]_in_blood',
    'leukocytes_[#/volume]_in_blood_by_automated_count',
    'oxygen_saturation_in_arterial_blood'
]

# Define minimum number of required valid features for ill patients only
min_valid_features = 5

# Count valid features per patient (non-null and not zero)
valid_feature_counts = merged[feature_cols].apply(lambda x: x.notnull() & (x != 0)).sum(axis=1)

# Filter:
# - Keep all healthy patients (is_ill == 0)
# - For ill patients (is_ill == 1), keep only if valid features >= min_valid_features
merged_filtered = merged[
    (merged['is_ill'] == 0) |
    ((merged['is_ill'] == 1) & (valid_feature_counts >= min_valid_features))
].copy()

print(f"Dropped {len(merged) - len(merged_filtered)} patients due to insufficient feature data (only ill patients filtered).")

# Normal healthy average values for missing features
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

# Fill NaNs for features with normal values after filtering
for col, normal in normal_values.items():
    if col in merged_filtered.columns:
        merged_filtered[col] = merged_filtered[col].fillna(normal)

# Final dataset
final_data = merged_filtered[['Id', 'is_ill'] + feature_cols]

# Save to CSV
final_data.to_csv("synthea_data/training_data.csv", index=False)
print("Filtered data prepared and saved as training_data.csv")