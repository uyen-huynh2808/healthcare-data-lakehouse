from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, to_timestamp, to_date, udf, datediff, current_date, when
from pyspark.sql.types import StructType, IntegerType
import json
import joblib
import os

# Load schemas
with open("/PATH_TO/delta_lake_setup/schema_bronze.json") as f:
    bronze_schema = StructType.fromJson(json.load(f))

# Spark Session
spark = SparkSession.builder \
    .appName("PatientDataStreaming") \
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
    .config("spark.hadoop.fs.gs.impl", "com.google.cloud.hadoop.fs.gcs.GoogleHadoopFileSystem") \
    .config("spark.hadoop.google.cloud.auth.service.account.enable", "true") \
    .config("spark.hadoop.google.cloud.auth.service.account.json.keyfile", "PATH_TO_KEY") \
    .config("spark.hadoop.google.cloud.project.id", "YOUR_PROJECT_ID") \
    .config("parentProject", "YOUR_PROJECT_ID") \
    .getOrCreate()


# Define UDF that loads model inside the function (avoid serialization issues)
def predict(*args):
    from joblib import load
    model_path = "/PATH_TO/models/illness_predictor.pkl"
    if not hasattr(predict, "model"):
        predict.model = load(model_path)
    input_data = [float(a) if a is not None else 0.0 for a in args]
    return int(predict.model.predict([input_data])[0])

predict_udf = udf(predict, IntegerType())

# Read from Kafka
df_kafka = spark.readStream.format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("subscribe", "patient_data") \
    .option("startingOffsets", "latest") \
    .load()

# Parse JSON with bronze schema
df_bronze = df_kafka.selectExpr("CAST(value AS STRING)").select(
    from_json(col("value"), bronze_schema).alias("data")
).select("data.*")

# Transform and clean (Silver step)
df_silver = df_bronze.select(
    col("patient_id"),
    to_timestamp("timestamp").alias("timestamp"),
    to_date("birthday").alias("birthday"),
    col("gender").cast("int"),
    col("body_mass_index").cast("double"),
    col("body_temperature").cast("double"),
    col("heart_rate").cast("int"),
    col("systolic_blood_pressure").cast("int"),
    col("creatinine").cast("double"),
    col("alanine_aminotransferase_[enzymatic_activity/volume]_in_serum_or_plasma").cast("double"),
    col("glucose").cast("double"),
    col("hemoglobin_[mass/volume]_in_blood").cast("double"),
    col("leukocytes_[#/volume]_in_blood_by_automated_count").cast("double"),
    col("oxygen_saturation_in_arterial_blood").cast("int"),
    (datediff(current_date(), to_date("birthday")) / 365).cast("int").alias("age")
)

# Add age_group column
df_silver = df_silver.withColumn(
    "age_group",
    when(col("age") < 0, None)
    .when((col("age") >= 0) & (col("age") < 18), "0-17")
    .when((col("age") >= 18) & (col("age") < 35), "18-34")
    .when((col("age") >= 35) & (col("age") < 50), "35-49")
    .when((col("age") >= 50) & (col("age") < 65), "50-64")
    .when((col("age") >= 65) & (col("age") < 80), "65-79")
    .when(col("age") >= 80, "80+")
    .otherwise(None)
)

# One-hot encode age_group to match train_model.py (prefix = 'age_group')
df_silver = df_silver \
    .withColumn("age_group_0-17", when(col("age_group") == "0-17", 1).otherwise(0)) \
    .withColumn("age_group_18-34", when(col("age_group") == "18-34", 1).otherwise(0)) \
    .withColumn("age_group_35-49", when(col("age_group") == "35-49", 1).otherwise(0)) \
    .withColumn("age_group_50-64", when(col("age_group") == "50-64", 1).otherwise(0)) \
    .withColumn("age_group_65-79", when(col("age_group") == "65-79", 1).otherwise(0)) \
    .withColumn("age_group_80+", when(col("age_group") == "80+", 1).otherwise(0))

# Apply model to generate predictions (Gold step)
feature_cols = [
    "gender", "body_mass_index", "body_temperature", "heart_rate", "systolic_blood_pressure",
    "creatinine", "alanine_aminotransferase_[enzymatic_activity/volume]_in_serum_or_plasma",
    "glucose", "hemoglobin_[mass/volume]_in_blood", "leukocytes_[#/volume]_in_blood_by_automated_count",
    "oxygen_saturation_in_arterial_blood",
    "age_group_0-17", "age_group_18-34", "age_group_35-49",
    "age_group_50-64", "age_group_65-79", "age_group_80+"
]

df_gold = df_silver.withColumn("prediction", predict_udf(*[col(c) for c in feature_cols]))

# Write to Delta Lake Gold and use foreachBatch to write to BigQuery
def write_to_bq(batch_df, batch_id):
    batch_df.select(
        "patient_id", "age_group", "gender", "body_mass_index", "body_temperature", "heart_rate",
        "systolic_blood_pressure", "creatinine",
        col("alanine_aminotransferase_[enzymatic_activity/volume]_in_serum_or_plasma").alias("alt"),
        "glucose",
        col("hemoglobin_[mass/volume]_in_blood").alias("hemoglobin"),
        col("leukocytes_[#/volume]_in_blood_by_automated_count").alias("leukocytes"),
        col("oxygen_saturation_in_arterial_blood").alias("oxygen_saturation"),
        "prediction"
    ).write \
     .format("bigquery") \
     .option("table", "YOUR_DATASET.YOUR_TABLE") \
     .option("project", "YOUR_PROJECT_ID") \
     .option("temporaryGcsBucket", "YOUR_BUCKET") \
     .option("credentialsFile", "/PATH_TO_KEY") \
     .mode("append") \
     .save()

query = df_gold.writeStream \
    .format("delta") \
    .option("checkpointLocation", "/PATH_TO/checkpoints/gold") \
    .outputMode("append") \
    .option("path", "/PATH_TO/delta/gold") \
    .foreachBatch(write_to_bq) \
    .start()

query.awaitTermination()
