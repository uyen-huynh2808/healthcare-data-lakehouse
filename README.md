# Real-Time Healthcare Lakehouse for Patient Monitoring (Synthea, Faker, Kafka, Spark, Delta Lake, BigQuery)

This project builds a **real-time healthcare data lake and analytics platform** for monitoring patient vitals from simulated **IoT wearable devices**, using a combination of **Synthea** for realistic synthetic patient histories and **Faker** for live streaming vitals. Vital signs like heart rate, temperature, and SpO₂ are streamed via **Apache Kafka**, processed in real time using **Spark Structured Streaming**, and stored in **Delta Lake** using a Bronze–Silver–Gold architecture. Cleaned and aggregated data is loaded into **BigQuery** for analysis and visualized using **Looker**. An **anomaly detection ML model** is integrated to identify abnormal vitals in real time, simulating how healthcare providers can respond to emergencies and monitor patient health at scale.

## Project Goals

- **Simulate realistic patient data using Synthea and Faker**

  Use Synthea to generate full synthetic EHR records and vitals distributions.

  Use Faker-guided scripts to simulate real-time streaming data from IoT devices based on Synthea trends.

- **Ingest real-time vitals from simulated IoT patient devices**

  Stream live patient vitals like heart rate, temperature, SpO₂, and blood pressure using Apache Kafka to mimic a hospital monitoring environment.

- **Stream and process data with Spark Structured Streaming**

  Process Kafka streams with schema enforcement, cleansing, timestamp alignment, and enrichment.

- **Store data in Delta Lake using Bronze, Silver, and Gold architecture**
  - Bronze: Raw Kafka ingestion
  - Silver: Parsed, cleaned, and enriched data
  - Gold: Aggregated metrics with anomaly flags

- **Load curated data into BigQuery for analytics**

  Transfer Gold-layer data into Google BigQuery for scalable querying and reporting.

- **Visualize trends and anomalies with Looker Studio**

  Build dashboards for hospital-wide monitoring, patient-level trends, and anomaly alerts.

- **Apply ML models for real-time anomaly detection**

  Train models on historical Synthea-based data and run inference on real-time streams.

## Architecture

![architecture](https://github.com/user-attachments/assets/ede4f777-bbdf-4bbe-ae99-bb977e99c4d0)

## Technology Stack

| Layer                   | Tools/Technologies                                         |
|------------------------|------------------------------------------------------------|
| Data Simulation         | Synthea (synthetic EHR), Faker, NumPy, JSON                             |
| Ingestion               | Apache Kafka                                               |
| Streaming               | Apache Spark (Structured Streaming)                        |
| Storage                 | Delta Lake (Parquet + Transaction Logs)                    |
| ML / Anomaly Detection  | PySpark ML, scikit-learn, MLflow |
| Orchestration           | Apache Airflow (ETL + ML workflows)            |
| Query Layer             | Google BigQuery                                            |
| Visualization           | Looker Studio                                              |

## Data Used

- **Synthea-generated data (static, high realism)**
  - Baseline reference for vitals ranges and disease progression.
  - Used for ML training and validation.

- **Faker-based streaming simulator**

  Each simulated patient device emits JSON-formatted vitals every few seconds:
  
  - `patient_id`: unique identifier
  - `timestamp`: ISO8601 format
  - `heart_rate`: integer
  - `temperature`: float
  - `spo2`: float (oxygen level)
  - `respiration_rate`: integer
  - `blood_pressure`: systolic/diastolic

## Data Model
**Delta Lake Tables**

`bronze_patient_vitals`
- Raw data ingested from Kafka
- Schema: unvalidated, JSON

`silver_patient_vitals`
- Cleaned and parsed records
- Derived fields and simple alert flags

`gold_patient_summary`
- Aggregated vitals per patient
- Includes real-time anomaly detection score
- Partitioned by date and patient_id

**BigQuery Tables**
- Mirrors Gold layer
- Materialized views:
  - `patient_risk_scores`
  - `ward_alert_counts`
  - `vital_signs_hourly_trend`
 
## ML Model

**Goal:**  

Detect abnormal vital patterns in real time to alert clinicians.

**Algorithms Explored:**  
- **Isolation Forest** – Efficient unsupervised anomaly detection  
- **AutoEncoder** – Neural-network-based scoring (optional)  
- **LSTM** – Time-series anomaly detection (if needed)

**Workflow:**  
1. Train models on Synthea-generated historical data
2. Register model using MLflow (optional)
3. Inference in Spark Streaming pipeline
4. Append anomaly scores to Gold table
5. Visualize using Looker dashboards

## Project Files

1. `synthea_data/` – Synthea patient records and vitals (CSV/JSON)
2. `data_simulator/` – Faker-based real-time vitals generator
3. `kafka_producer.py` – Streams vitals to Kafka
4. `delta_lake_setup/` – Delta Lake schema setup (Bronze/Silver/Gold)
5. `spark_streaming_job.py` – Spark job to process streams to Delta
6. `train_model.py` – Anomaly detection model training (Isolation Forest, etc.)
7. `ml_inference_stream.py` – Real-time model scoring
8. `bigquery_loader.py` – Transfer Gold layer to BigQuery
9. `dags/` – Airflow DAGs for ETL and ML workflows
10. `dashboards/` – Looker Studio templates and metrics
11. `pipeline_setup_guide.ipynb` – Jupyter notebook walkthrough for local setup, dependencies, and execution flow

## License

This project uses simulated patient data generated by Synthea, Faker, and custom scripts for educational and research purposes only. The data and dashboards are not based on real patients or real-world trends.

**Disclaimer:**

- The insights, trends, and anomalies presented in this project exist solely within the simulated environment. They should not be interpreted as medical findings, healthcare insights, or clinical recommendations. This project is intended to demonstrate a data engineering and analytics pipeline, not to represent real medical analysis.

- Do not use any of the generated reports, visualizations, or data for decision-making in real healthcare or diagnostics contexts.

---
