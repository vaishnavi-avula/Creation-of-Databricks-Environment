"""
Healthcare Patient ETL Pipeline - Delta Live Tables (DLT)
=========================================================
Medallion Architecture: Bronze -> Silver -> Gold

Author: Vaishnavi Avula
Platform: Azure Databricks (Premium)
Storage: Azure Data Lake Storage Gen2
Compliance: Australian Privacy Act 1988 + My Health Records Act 2012

Pipeline Configuration (set in DLT pipeline settings):
-------------------------------------------------------
fs.azure.account.auth.type.adlshealthstartupprod.dfs.core.windows.net = OAuth
fs.azure.account.oauth.provider.type.adlshealthstartupprod.dfs.core.windows.net = org.apache.hadoop.fs.azurebfs.oauth2.ClientCredsTokenProvider
fs.azure.account.oauth2.client.id.adlshealthstartupprod.dfs.core.windows.net = {{secrets/kv-healthstartup/sp-client-id}}
fs.azure.account.oauth2.client.secret.adlshealthstartupprod.dfs.core.windows.net = {{secrets/kv-healthstartup/sp-client-secret}}
fs.azure.account.oauth2.client.endpoint.adlshealthstartupprod.dfs.core.windows.net = https://login.microsoftonline.com/<tenant-id>/oauth2/token
"""

import dlt
from pyspark.sql.functions import (
    sha2, col, current_timestamp, upper, trim, when, count
)

# Storage path for raw bronze data
bronze_path = "abfss://bronze@adlshealthstartupprod.dfs.core.windows.net/patients"


# =============================================================================
# BRONZE LAYER - Raw data ingestion
# Purpose: Store raw, unmodified patient records exactly as received from source
# Why Delta format: ACID transactions, time travel, schema enforcement
# =============================================================================
@dlt.table(
    name="bronze_patients",
    comment="Raw patient records ingested from clinic ERP system - no transformations applied"
)
def bronze_patients():
    """
    Reads raw patient data from ADLS Gen2 bronze container.

    Why bronze layer?
    - Keeps original data intact for reprocessing
    - Acts as source of truth / audit trail
    - Allows replaying history if silver/gold logic changes
    """
    return spark.read.format("delta").load(bronze_path)


# =============================================================================
# SILVER LAYER - Cleaned data with PHI removed
# Purpose: Remove Personally Identifiable Information (PII/PHI) for compliance
# Why PHI removal: Australian Privacy Act 1988 requires minimising personal data exposure
# =============================================================================
@dlt.table(
    name="silver_patients",
    comment="Cleaned patient records - PHI removed for Australian Privacy Act compliance"
)
def silver_patients():
    """
    Transforms bronze data:
    1. Hashes patient_id using SHA-256 (one-way, irreversible)
    2. Removes: patient_id, medicare_number, given_name, family_name
    3. Standardises gender (uppercase, trimmed)
    4. Adds data quality flags
    5. Adds processing timestamp

    Why SHA-256 for patient_id?
    - Allows linking records across datasets without exposing real ID
    - One-way hash - cannot be reversed to get original ID
    - 256-bit output - collision resistant

    Why keep date_of_birth?
    - Needed for age-based analytics (e.g. chronic disease prevalence by age group)
    - Not sufficient alone to identify a person
    """
    bronze = dlt.read("bronze_patients")

    step1 = bronze.withColumn("patient_id_hash", sha2(col("patient_id"), 256))
    step2 = step1.withColumn("gender", upper(trim(col("gender"))))
    step3 = step2.withColumn("postcode", trim(col("postcode")))
    step4 = step3.withColumn("silver_processed_at", current_timestamp())
    step5 = step4.withColumn(
        "data_quality",
        when(col("date_of_birth").isNull(), "INCOMPLETE").otherwise("OK")
    )
    step6 = step5.drop("patient_id", "medicare_number", "given_name", "family_name")

    return step6


# =============================================================================
# GOLD LAYER - Aggregated analytics tables
# Purpose: Pre-aggregated tables safe for analysts and dashboards
# Why gold layer: Zero PHI, fast queries, BI-ready
# =============================================================================
@dlt.table(
    name="gold_patients_by_postcode",
    comment="Patient counts by postcode - safe for analytics dashboards, zero PHI"
)
def gold_patients_by_postcode():
    """
    Aggregates patient counts by postcode and gender.

    Why aggregate at gold layer?
    - Analysts only need counts, not individual records
    - Removes any remaining re-identification risk
    - Optimised for dashboard queries (pre-aggregated = fast)
    - Power BI connects directly to this table
    """
    silver = dlt.read("silver_patients")
    return silver.groupBy("postcode").agg(
        count("*").alias("patient_count"),
        count(when(col("gender") == "F", 1)).alias("female_count"),
        count(when(col("gender") == "M", 1)).alias("male_count")
    )


@dlt.table(
    name="gold_data_quality_summary",
    comment="Data quality overview by source system - for monitoring and alerting"
)
def gold_data_quality_summary():
    """
    Summarises data quality metrics by source system.

    Why track data quality at gold layer?
    - Identifies problematic source systems early
    - Supports SLA reporting for data engineering team
    - Feeds into monitoring dashboards
    - Required for healthcare data governance
    """
    silver = dlt.read("silver_patients")
    return silver.groupBy("data_quality", "source_system").agg(
        count("*").alias("record_count")
    )
