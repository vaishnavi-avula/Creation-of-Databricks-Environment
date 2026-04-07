# Databricks notebook source
# Verify Silver and Gold Tables
# ==============================
# Run this after the DLT pipeline completes to verify data quality
# Run on: etl-job-cluster

# COMMAND ----------

# Configure storage
spark.conf.set(
    "fs.azure.account.key.adlshealthstartupprod.dfs.core.windows.net",
    dbutils.secrets.get(scope="kv-healthstartup", key="adls-storage-key")
)

# COMMAND ----------

# Verify Silver - confirm PHI is removed
print("=== SILVER PATIENTS ===")
print("Expected: NO patient_id, NO given_name, NO family_name, NO medicare_number")
display(spark.sql("SELECT * FROM adb_healthstartup_prod.default.silver_patients"))

# COMMAND ----------

# Verify Gold - patient counts by postcode
print("=== GOLD: PATIENTS BY POSTCODE ===")
display(spark.sql("SELECT * FROM adb_healthstartup_prod.default.gold_patients_by_postcode"))

# COMMAND ----------

# Verify Gold - data quality summary
print("=== GOLD: DATA QUALITY SUMMARY ===")
display(spark.sql("SELECT * FROM adb_healthstartup_prod.default.gold_data_quality_summary"))

# COMMAND ----------

# Data quality check - ensure no PHI columns exist in silver
silver_columns = spark.sql("SELECT * FROM adb_healthstartup_prod.default.silver_patients LIMIT 1").columns
phi_columns = ["patient_id", "given_name", "family_name", "medicare_number"]
leaked_phi = [c for c in phi_columns if c in silver_columns]

if leaked_phi:
    raise Exception(f"PHI LEAK DETECTED in silver table: {leaked_phi}")
else:
    print("PHI check PASSED - no personally identifiable information in silver table")
