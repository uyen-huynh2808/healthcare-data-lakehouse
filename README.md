# Real-Time Healthcare Data Lakehouse for Illness Prediction (Synthea, Faker, Kafka, Spark, Delta Lake, BigQuery)

## Project Overview

This project implements a real-time healthcare data lakehouse system to **predict whether a patient is ill or not** based on simulated medical test data. It uses a combination of **synthetic training data** (static) and **real-time simulated input** to apply machine learning in a streaming context.

- **Synthea** generates **static patient records** for model training.
- **Faker** simulates **real-time medical test results** to mimic streaming patient records.
- **Apache Kafka** handles the real-time ingestion of records.
- **Apache Spark Structured Streaming** processes streaming data and applies a trained ML model to classify each record as "ill" or "healthy".
- **Delta Lake** stores the processed data in a structured multi-layered format (Bronze → Silver → Gold).
- **Google BigQuery** supports querying and visualization.
- **Looker Studio** is used for analytics dashboards and reporting.

## Project Goals

- Generate realistic training data using **Synthea**.
- Simulate real-time patient test results using **Faker** and ingest via **Kafka**.
- Build a **real-time illness prediction pipeline** using **Spark Streaming** and a pre-trained model.
- Store data in **Delta Lake** with a **multi-stage architecture**.
- Push final results to **BigQuery** for analysis and reporting.


## Architecture

![architecture](https://github.com/user-attachments/assets/f62024fd-ccbb-4c17-866b-e402937a4043)

## Technology Stack

| Layer             | Tools/Technologies                            |
|-------------------|-----------------------------------------------|
| Static Data   | Synthea                                        |
| Data Simulation | Faker                                       |
| Ingestion     | Apache Kafka                                  |
| Stream Processing | Apache Spark Structured Streaming         |
| Storage       | Delta Lake (Bronze, Silver, Gold)             |
| Machine Learning | pandas, scikit-learn, SMOTE         |
| Analytics     | Google BigQuery                               |
| Visualization | Looker Studio                                 |

## Data Used

### 1. **Synthea-Generated Static Dataset**

- **Source:** `synthea_data/training_data.csv`
- **Description:** High-quality synthetic patient data generated by Synthea, representing realistic vitals and clinical conditions.
- **Usage:** Machine learning model training (`RandomForestClassifier`)

**Key Features Used in Training:**

| Feature Name                                                                                  | Description                                             | Type    |
|-----------------------------------------------------------------------------------------------|---------------------------------------------------------|---------|
| `age_group_0-17`                                                                              | One-hot encoded: 1 if age is 0–17, else 0               | Integer |
| `age_group_18-34`                                                                             | One-hot encoded: 1 if age is 18–34, else 0              | Integer |
| `age_group_35-49`                                                                             | One-hot encoded: 1 if age is 35–49, else 0              | Integer |
| `age_group_50-64`                                                                             | One-hot encoded: 1 if age is 50–64, else 0              | Integer |
| `age_group_65-79`                                                                             | One-hot encoded: 1 if age is 65–79, else 0              | Integer |
| `age_group_80+`                                                                               | One-hot encoded: 1 if age is 80+, else 0                | Integer |
| `gender`                                                                                      | Binary encoded gender (0 = Female, 1 = Male)            | Integer |
| `body_mass_index`                                                                             | Body mass index (BMI) in kg/m²                          | Float   |
| `body_temperature`                                                                            | Body temperature in °C                                  | Float   |
| `heart_rate`                                                                                  | Heart rate in beats per minute (bpm)                    | Integer |
| `systolic_blood_pressure`                                                                     | Systolic blood pressure (mmHg)                          | Integer |
| `creatinine`                                                                                  | Creatinine level in mg/dL                               | Float   |
| `alanine_aminotransferase_[enzymatic_activity/volume]_in_serum_or_plasma`                    | Liver enzyme (ALT) level in U/L                         | Float   |
| `glucose`                                                                                     | Blood glucose level in mg/dL                            | Float   |
| `hemoglobin_[mass/volume]_in_blood`                                                           | Hemoglobin concentration in g/dL                        | Float   |
| `leukocytes_[#/volume]_in_blood_by_automated_count`                                           | White blood cell count (10³/μL)                         | Float   |
| `oxygen_saturation_in_arterial_blood`                                                         | Oxygen saturation (SpO₂) percentage                     | Integer |
| `is_ill`                                                                                      | Target label (0 = Healthy, 1 = Ill)                     | Integer |

### 2. **Faker-Based Streaming Simulator**

- **Source:** `src/streaming_data_producer.py`
- **Description:** Simulates real-time patient medical test results and publishes them as JSON records to a Kafka topic (`patient_data`), emitting one record per second.
- **Purpose:**
  - Emulates a live feed of new patient records arriving in real time
  - Feeds Spark Structured Streaming for ingestion, transformation, and ML-based illness prediction

**Fields in Each Streamed JSON Record:**

| Field Name                                                                                   | Description                                             | Type    |
|----------------------------------------------------------------------------------------------|---------------------------------------------------------|---------|
| `patient_id`                                                                                 | Unique patient identifier (UUID)                        | String  |
| `timestamp`                                                                                  | Event timestamp in ISO 8601 (UTC)                       | String  |
| `birthday`                                                                                   | Patient date of birth (used to calculate age)           | String  |
| `gender`                                                                                     | Binary encoded gender (0 = Female, 1 = Male)            | Integer |
| `body_mass_index`                                                                            | BMI in kg/m²                                            | Float   |
| `body_temperature`                                                                           | Body temperature in °C                                  | Float   |
| `heart_rate`                                                                                 | Heart rate in beats per minute                          | Integer |
| `systolic_blood_pressure`                                                                    | Systolic blood pressure (mmHg)                          | Integer |
| `creatinine`                                                                                 | Creatinine level in mg/dL                               | Float   |
| `alanine_aminotransferase_[enzymatic_activity/volume]_in_serum_or_plasma`                   | ALT enzyme level in U/L                                 | Float   |
| `glucose`                                                                                    | Blood glucose level in mg/dL                            | Float   |
| `hemoglobin_[mass/volume]_in_blood`                                                          | Hemoglobin concentration in g/dL                        | Float   |
| `leukocytes_[#/volume]_in_blood_by_automated_count`                                          | White blood cell count (10³/μL)                         | Float   |
| `oxygen_saturation_in_arterial_blood`                                                        | Oxygen saturation percentage                            | Integer |

## Data Model

### Delta Lake Tables

| Layer  | Description                        |
|--------|------------------------------------|
| Bronze | Raw JSON stream from Kafka         |
| Silver | Cleaned and transformed patient records  |
| Gold   | Final records with `is_ill` label  |

### BigQuery Tables

- Table: `patient_data.gold_patient_data`
- Mirror of the Delta Lake Gold table
- Used for analytics and dashboards

| Column Name               | Description                                             | Type    |
|--------------------------|---------------------------------------------------------|---------|
| `patient_id`             | Unique identifier for the patient                       | String  |
| `age_group`              | Age group of the patient (e.g., 0-17, 18-34, ...)       | String  |
| `gender`                 | Binary encoded gender (0 = Female, 1 = Male)            | Integer |
| `body_mass_index`        | Body mass index (BMI) in kg/m²                          | Float   |
| `body_temperature`       | Body temperature in °C                                  | Float   |
| `heart_rate`             | Heart rate in beats per minute (bpm)                    | Integer |
| `systolic_blood_pressure`| Systolic blood pressure in mmHg                        | Integer |
| `creatinine`             | Creatinine level in mg/dL                               | Float   |
| `alt`                    | Alanine aminotransferase (ALT) level in U/L            | Float   |
| `glucose`                | Blood glucose level in mg/dL                            | Float   |
| `hemoglobin`             | Hemoglobin concentration in g/dL                        | Float   |
| `leukocytes`             | White blood cell count (10³/μL)                         | Float   |
| `oxygen_saturation`      | Oxygen saturation (SpO₂) percentage                     | Integer |
| `prediction`             | Predicted health status (0 = Healthy, 1 = Ill)          | Integer |

### Looker Studio Views
- Patient Age Overview
- Lab Tests by Age Group
- Gender-Based Differences
 
## ML Model

### Purpose
Predict illness status of a patient based on medical test results.

### Modeling Steps
1. Preprocess data using `prepare_training_data.py`
2. Handle class imbalance using **SMOTE**
3. Train a **Random Forest classifier** (`train_model.py`)
4. Save the trained model using `joblib`

## Project Files

1. `synthea_data/` – Static Synthea-generated patient data used for model training (`training_data.csv`).
2. `src/prepare_training_data.py` – Cleans and transforms static data for training.
3. `src/train_model.py` – Trains the classification model and saves it.
4. `models/illness_predictor.pkl` – Serialized trained model for real-time inference.
5. `src/streaming_data_producer.py` – Simulates real-time patient test records using Faker.
6. `delta_lake_setup/schema_bronze.json` – Schema for Bronze (raw) layer.
7. `delta_lake_setup/schema_silver.json` – Schema for Silver (cleaned) layer.
8. `delta_lake_setup/schema_gold.json` – Schema for Gold (classified) layer.
9. `src/streaming_inference_job.py` – Spark job that ingests from Kafka, writes to Bronze → Silver → Gold layers, and loads curated Gold data into BigQuery for reporting.
10. `notebooks/project_walkthrough.ipynb` – Interactive setup guide and walkthrough of key components.
11. `notebooks/reporting.md` – Visualization and reporting examples.

## Disclaimer

- This project is for **educational purposes only**.  
- All data is **synthetically generated** using **Synthea** and **Faker**.  
- It is not intended for clinical or medical use in any real-world setting.

## Limitations
- Synthetic Data Only: All input is generated with Synthea and Faker, which may lack the complexity, variability, and edge cases of real clinical data.
- Offline Model Retraining: The ML model is trained offline and used as-is during streaming. There is no online learning or adaptive update mechanism.
- Basic Feature Set: The current feature set doesn’t account for patient history, comorbidities, or longitudinal trends.
- No Model Monitoring: There is no performance monitoring or drift detection in the live prediction phase.
- Latency Not Optimized: The streaming job is batch-based and may not achieve true low-latency performance in all configurations.

## Future Developments
- Incorporate Longitudinal Data: Enhance predictions using patient history and temporal trends from repeated visits.
- Introduce Model Monitoring: Integrate tools like MLflow, Prometheus, or custom drift detection to monitor prediction quality over time.
- Online or Incremental Learning: Explore real-time model updates using streaming-compatible frameworks like River.
- Real-Time Alerting: Push prediction results to alerting platforms (e.g., Slack, PagerDuty) for operational simulation.
- Enhanced Visualization: Create interactive dashboards in Looker Studio for patient-level drilldowns, anomaly detection, and model performance summaries.
- Governance & Metadata Tracking: Add Apache Atlas or Data Catalog for lineage, schema versioning, and audit readiness.

## Conclusion

This project showcases a real-time healthcare data lakehouse architecture for illness prediction using a modern big data stack. By combining Synthea-generated training data with real-time simulated patient vitals, it demonstrates how machine learning can be applied to streaming medical data in a scalable and modular fashion.

Key highlights include:

- Real-time ingestion and processing using Kafka and Spark Structured Streaming.
- Delta Lake multi-layered architecture (Bronze, Silver, Gold) for efficient and reliable data storage.
- Integration with BigQuery and Looker Studio for real-time analytics and visualizations.
- Application of a Random Forest classifier to predict patient health status based on clinical vitals.

This end-to-end pipeline represents a foundational blueprint for future real-world healthcare streaming systems — balancing engineering, machine learning, and analytics in one solution.

---
