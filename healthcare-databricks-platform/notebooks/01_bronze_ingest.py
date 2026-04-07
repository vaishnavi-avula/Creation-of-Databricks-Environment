# Databricks notebook source
# Healthcare Bronze Layer - Patient Data Ingestion
# =================================================
# Purpose: Write sample patient records to Bronze Delta table
# Run on: etl-job-cluster (Standard_D4ds_v5, Single Node)
# Storage: ADLS Gen2 - bronze container

# COMMAND ----------

# Step 1: Configure storage authentication using Key Vault secret
# Why use Key Vault? Never hardcode credentials in notebooks.
# Key Vault = Azure's secure credential store (like a password manager for cloud)

spark.conf.set(
    "fs.azure.account.key.adlshealthstartupprod.dfs.core.windows.net",
    dbutils.secrets.get(scope="kv-healthstartup", key="adls-storage-key")
)

# COMMAND ----------

# Step 2: Define the bronze storage path
# ABFS (Azure Blob File System) format: abfss://container@storage.dfs.core.windows.net/path
# Why abfss:// (with double s)? The 's' means SSL/TLS encrypted - always use this for healthcare data

bronze_path = "abfss://bronze@adlshealthstartupprod.dfs.core.windows.net/patients"

# COMMAND ----------

# Step 3: Create sample patient data
# In production, this would be replaced by an auto-loader reading from source systems

from pyspark.sql.types import StructType, StructField, StringType, TimestampType
from pyspark.sql.functions import current_timestamp, lit
from datetime import datetime

# Sample patient records (simulating clinic ERP export)
data = [
    ("P001", "Jane",   "Smith", "1985-03-15", "F", "123456789", "2000", datetime.now(), "clinic-erp"),
    ("P002", "John",   "Doe",   "1962-07-22", "M", "987654321", "3000", datetime.now(), "clinic-erp"),
]

schema = StructType([
    StructField("patient_id",      StringType(), False),
    StructField("given_name",      StringType(), True),
    StructField("family_name",     StringType(), True),
    StructField("date_of_birth",   StringType(), True),
    StructField("gender",          StringType(), True),
    StructField("medicare_number", StringType(), True),
    StructField("postcode",        StringType(), True),
    StructField("ingested_at",     TimestampType(), True),
    StructField("source_system",   StringType(), True),
])

df = spark.createDataFrame(data, schema)

# COMMAND ----------

# Step 4: Write to Delta format in bronze container
# Why Delta format?
# - ACID transactions (no partial writes)
# - Time travel (query historical versions)
# - Schema enforcement (rejects bad data)
# - Compaction and Z-ordering for performance

df.write \
  .format("delta") \
  .mode("overwrite") \
  .save(bronze_path)

print(f"Successfully written {df.count()} records to bronze layer")

# COMMAND ----------

# Step 5: Verify the data was written correctly
display(spark.read.format("delta").load(bronze_path))
