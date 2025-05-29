import json
import time
import random
from datetime import datetime, timezone
from faker import Faker
from kafka import KafkaProducer
from dateutil.relativedelta import relativedelta

fake = Faker()

# Kafka configuration
KAFKA_BROKER = 'localhost:9092'
TOPIC_NAME = 'patient_data'

# Kafka producer setup
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def generate_patient_data():
    """Simulate real-time patient data aligned with model training features"""
    patient_id = fake.uuid4()
    birthday = fake.date_of_birth(minimum_age=1, maximum_age=90)
    
    # Validate birthday is not in the future
    today = datetime.now(timezone.utc).date()
    assert birthday <= today, "Birthday cannot be in the future"
    
    # Calculate age precisely
    age = relativedelta(today, birthday).years
    assert 0 <= age <= 90, "Age is out of expected range"
    
    timestamp = datetime.now(timezone.utc).isoformat()

    # Gender (0 = female, 1 = male)
    gender_text = random.choice(["male", "female"])
    gender = 1 if gender_text == "male" else 0

    data = {
        "patient_id": patient_id,
        "timestamp": timestamp,
        "birthday": birthday.isoformat(),
        "gender": gender,                                                 # binary: 1=male, 0=female
        "body_mass_index": round(random.uniform(14.0, 50.0), 1),          # kg/m2
        "body_temperature": round(random.uniform(36.0, 39.0), 1),         # Celsius
        "heart_rate": random.randint(60, 120),                            # beats per minute (bpm)
        "systolic_blood_pressure": random.randint(90, 200),               # mmHg
        "creatinine": round(random.uniform(0.4, 7.9), 2),                 # mg/dL
        "alanine_aminotransferase_[enzymatic_activity/volume]_in_serum_or_plasma": round(random.uniform(20, 60), 1),  # U/L
        "glucose": round(random.uniform(60, 190), 1),                     # mg/dL
        "hemoglobin_[mass/volume]_in_blood": round(random.uniform(10, 18), 1),  # g/dL
        "leukocytes_[#/volume]_in_blood_by_automated_count": round(random.uniform(1.0, 11.0), 1),  # 10*3/uL
        "oxygen_saturation_in_arterial_blood": random.randint(50, 100)    # percentage (%)
    }
    return data

def stream_to_kafka(interval_sec=1):
    """Stream simulated data to Kafka topic"""
    print(f"Streaming real-time data to Kafka topic: {TOPIC_NAME}")
    try:
        while True:
            patient_data = generate_patient_data()
            producer.send(TOPIC_NAME, value=patient_data)
            print(f"Produced: {patient_data}")
            time.sleep(interval_sec)
    except KeyboardInterrupt:
        print("\nStopped streaming.")
    finally:
        producer.close()

if __name__ == "__main__":
    stream_to_kafka(interval_sec=1)
