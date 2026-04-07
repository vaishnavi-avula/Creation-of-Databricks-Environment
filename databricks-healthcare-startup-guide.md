# Databricks Environment Setup Guide for a Healthcare Startup (Australia)
### Azure | HIPAA-equivalent Australian Privacy Compliance | Budget-Conscious

---

## Document Overview

| Attribute | Value |
|---|---|
| Industry | Healthcare (Australia) |
| Cloud Provider | Microsoft Azure |
| Region | Australia East (Sydney) |
| Team | 2 Data Engineers, 1 Data Scientist, Data Platform Lead |
| Data Volume | Medium (100 GB – 1 TB/day) |
| Compliance | Australian Privacy Act 1988, My Health Records Act 2012 |
| Budget Phase | Azure Free Trial → Early Production |

---

## 1. Why Databricks for a Healthcare Startup?

### The Problem Without Databricks

Healthcare startups typically start with scattered data:
- Patient data coming from EHR/EMR systems, FHIR APIs, or flat file exports from clinics
- Streaming vitals from wearables or IoT devices
- Billing/claims CSVs exported from third-party systems
- Each data source in a different format, on different schedules

Without a unified platform, your team ends up with:
- Fragmented pipelines (scripts on VMs, Excel files, manual SQL queries)
- No single source of truth
- Compliance risk — no audit trail, data scattered across systems
- Data scientists blocked waiting for engineers to prepare data

### Why Databricks Solves This

Databricks provides a **unified data lakehouse** — one platform that handles:

| Capability | What it means for healthcare |
|---|---|
| **Delta Lake** | ACID transactions on your data lake — no corrupt patient records |
| **ETL Pipelines (Delta Live Tables)** | Reliable, tested pipelines from raw data → clean data |
| **SQL Analytics** | BI teams query cleaned data without touching raw PHI |
| **Streaming** | Process wearable/IoT data in near-real-time |
| **MLflow** | Track ML experiments — important for clinical model governance |
| **Unity Catalog** | Fine-grained access control — who can see which patient data |
| **Audit Logging** | Full audit trail — required for Privacy Act compliance |

### Why Azure Specifically (for Australian Healthcare)

- **Azure Australia East (Sydney)** — data never leaves Australia
- **Microsoft IRAP accreditation** — aligns with Australian government security standards
- **Azure Active Directory** — enterprise identity, MFA, RBAC built-in
- **Microsoft healthcare compliance portfolio** — BAA-equivalent agreements available
- **Databricks on Azure** — native integration, no extra networking complexity

---

## 2. Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        DATA SOURCES                             │
│  EHR/EMR APIs │ FHIR APIs │ Wearable Streams │ CSV Uploads      │
└──────────┬──────────┬──────────┬──────────────┬────────────────┘
           │          │          │              │
           ▼          ▼          ▼              ▼
┌─────────────────────────────────────────────────────────────────┐
│              AZURE INGESTION LAYER                              │
│   Azure Event Hubs (streaming)  │  Azure Data Factory (batch)   │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│         AZURE DATA LAKE STORAGE GEN2 (ADLS Gen2)               │
│                                                                 │
│  /raw/         /cleansed/        /curated/        /ml-ready/   │
│  (Bronze)      (Silver)          (Gold)           (Feature)    │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│              AZURE DATABRICKS WORKSPACE                         │
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌──────────────────────┐   │
│  │ ETL Cluster │  │ SQL Cluster │  │  ML / DS Cluster     │   │
│  │ (Jobs)      │  │ (Analytics) │  │  (Interactive)       │   │
│  └─────────────┘  └─────────────┘  └──────────────────────┘   │
│                                                                 │
│  Delta Live Tables │ Unity Catalog │ MLflow │ SQL Warehouse     │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│              CONSUMPTION LAYER                                  │
│   Power BI (dashboards) │ Tableau │ REST APIs │ ML Endpoints    │
└─────────────────────────────────────────────────────────────────┘
```

### Medallion Architecture (Bronze → Silver → Gold)

This is the standard lakehouse pattern. Think of it as 3 layers of data quality:

| Layer | Folder | Contents | Who touches it |
|---|---|---|---|
| **Bronze** | `/raw/` | Raw, unmodified data as received | Data Engineers only |
| **Silver** | `/cleansed/` | Deduplicated, validated, standardised | Data Engineers |
| **Gold** | `/curated/` | Business-ready aggregates, joined tables | Data Engineers + Analysts |
| **ML-Ready** | `/ml-features/` | Feature store for model training | Data Scientists |

**Why this matters in healthcare:** You always have a copy of the original data (Bronze). If a regulation requires you to prove what data you received and when, it's there. No data is ever overwritten.

---

## 3. Assumptions & Requirements Summary

### Business Assumptions

| Requirement | Assumption |
|---|---|
| Patient data (PHI) will be processed | Yes — anonymisation/pseudonymisation pipeline required |
| Real-time monitoring needed | Yes — wearables or clinical device streams |
| BI dashboards for clinical/ops teams | Yes — Power BI or similar |
| ML models for clinical insights | Yes — starting with 1 data scientist |
| Multi-environment (Dev/Prod) | Yes — even on free trial, design for this |
| Data retention policy | 7 years (aligned with Australian health records law) |

### Technical Assumptions

| Area | Assumption |
|---|---|
| Batch ingestion frequency | Every 1-4 hours |
| Streaming latency requirement | < 5 minutes (near-real-time, not millisecond) |
| Peak concurrent users | 5-10 (analysts + engineers + data scientist) |
| BI tool | Power BI (native Azure integration) |
| Source system APIs | FHIR R4 / HL7 v2 / flat file uploads |
| Identity provider | Azure Active Directory (Azure AD) |

---

## 4. Azure Prerequisites Setup

### Step 1: Create Your Azure Subscription

1. Go to [portal.azure.com](https://portal.azure.com) and sign up for a free trial
2. You get **$200 USD credit (≈ $310 AUD) for 30 days**
3. Set your **region to Australia East (Sydney)** — this ensures data residency

> **Free Trial Tip:** The $200 credit goes fast with Databricks clusters. Use it to test architecture, not to run 24/7 workloads. We'll design clusters that auto-terminate.

### Step 2: Create a Resource Group

A resource group is a logical container for all your Azure resources.

```bash
# Using Azure CLI
az group create \
  --name rg-healthstartup-prod \
  --location australiaeast
```

Or in the Azure Portal: **Resource Groups → Create → Name: rg-healthstartup-prod → Region: Australia East**

**Naming convention we'll use throughout:**
```
rg-{company}-{env}         # Resource Group
adls-{company}-{env}       # Storage Account
adb-{company}-{env}        # Databricks Workspace
kv-{company}-{env}         # Key Vault
```

### Step 3: Create Azure Data Lake Storage Gen2 (ADLS Gen2)

ADLS Gen2 is your data lake — all patient data, raw files, and Delta tables live here.

```bash
# Create storage account with hierarchical namespace (required for ADLS Gen2)
az storage account create \
  --name adlshealthstartupprod \
  --resource-group rg-healthstartup-prod \
  --location australiaeast \
  --sku Standard_LRS \
  --kind StorageV2 \
  --enable-hierarchical-namespace true \
  --min-tls-version TLS1_2
```

**Create your container structure:**
```bash
az storage fs create --name bronze --account-name adlshealthstartupprod
az storage fs create --name silver --account-name adlshealthstartupprod
az storage fs create --name gold   --account-name adlshealthstartupprod
az storage fs create --name ml     --account-name adlshealthstartupprod
```

### Step 4: Create Azure Key Vault

Secrets (storage keys, API tokens, database passwords) must NEVER be hardcoded. Key Vault stores them securely.

```bash
az keyvault create \
  --name kv-healthstartup-prod \
  --resource-group rg-healthstartup-prod \
  --location australiaeast \
  --sku standard \
  --enable-purge-protection true \
  --retention-days 90
```

### Step 5: Set Up Azure Active Directory Groups

Create AD groups to manage access:

| Group Name | Members | Purpose |
|---|---|---|
| `grp-databricks-admins` | Data Platform Lead | Full workspace admin |
| `grp-databricks-engineers` | 2 Data Engineers | Can create/manage clusters and jobs |
| `grp-databricks-scientists` | Data Scientist | Can create interactive clusters, access ML features |
| `grp-databricks-analysts` | BI/SQL Analysts | SQL Warehouse access only, no cluster management |

---

## 5. Databricks Workspace Configuration

### Step 1: Create the Databricks Workspace

```bash
az databricks workspace create \
  --name adb-healthstartup-prod \
  --resource-group rg-healthstartup-prod \
  --location australiaeast \
  --sku premium
```

> **Why Premium SKU?** Premium is required for:
> - Unity Catalog (data governance — essential for PHI access control)
> - Role-Based Access Control (RBAC) at table/column level
> - Audit logging (compliance requirement)
>
> Cost difference: ~20-30% more than Standard, but non-negotiable for healthcare.

### Step 2: Configure Databricks Secret Scope (backed by Key Vault)

Instead of storing credentials in notebooks, use secret scopes:

```bash
# In Databricks CLI
databricks secrets create-scope \
  --scope kv-healthstartup \
  --scope-backend-type AZURE_KEYVAULT \
  --resource-id /subscriptions/{sub-id}/resourceGroups/rg-healthstartup-prod/providers/Microsoft.KeyVault/vaults/kv-healthstartup-prod \
  --dns-name https://kv-healthstartup-prod.vault.azure.net/
```

In your notebooks, access secrets like this:
```python
# Never hardcode credentials — always use secret scope
storage_key = dbutils.secrets.get(scope="kv-healthstartup", key="adls-storage-key")
```

### Step 3: Enable Unity Catalog

Unity Catalog is Databricks' data governance layer — it controls who can see which data across your workspace.

1. In Databricks Account Console → **Catalog → Enable Unity Catalog**
2. Create a metastore in **Australia East**
3. Assign the metastore to your workspace

**Catalog structure for healthcare:**
```
healthstartup_catalog/
├── bronze_db/          # Raw ingested data
│   ├── fhir_patients   # Raw FHIR patient resources
│   ├── hl7_messages    # Raw HL7 messages
│   └── device_streams  # Raw wearable data
├── silver_db/          # Cleansed data
│   ├── patients        # Validated patient records
│   ├── encounters      # Clinical encounters
│   └── observations    # Lab results, vitals
├── gold_db/            # Business-ready
│   ├── patient_summary # Aggregated patient view
│   └── ops_dashboard   # Operational metrics
└── ml_db/              # ML features
    └── patient_features
```

---

## 6. Cluster Design

This is the most important section for cost control. We design **purpose-specific clusters** rather than one large shared cluster.

### Cluster 1: ETL Job Cluster (Data Engineers)

Used for running scheduled data pipelines. **Auto-terminates after each job** — you only pay while the job runs.

| Setting | Value | Reason |
|---|---|---|
| Cluster type | **Job Cluster** | Spins up for a job, terminates after — cheapest option |
| Runtime | Databricks Runtime 14.x LTS | LTS = Long-Term Support, stable for production |
| Worker type | `Standard_DS3_v2` (14 GB, 4 cores) | Good balance of memory/CPU for ETL at medium volume |
| Min workers | 2 | Handles baseline load |
| Max workers | 6 | Autoscales for peak ingestion |
| Auto-terminate | After job completion | Critical for cost — never leave a job cluster idle |
| Spot instances | **Yes (for dev/test)** | 60-80% cheaper; acceptable if jobs can retry |
| Spot instances | **No (for production)** | Production jobs need reliability |

**Monthly cost estimate (production):** ~$400-600 AUD/month (running 4-6 hours/day for pipelines)

### Cluster 2: SQL Warehouse (Analytics / BI Team)

SQL Warehouses are optimised for SQL queries and Power BI connections. They are **serverless-like** — scale to zero when idle.

| Setting | Value | Reason |
|---|---|---|
| Type | **Serverless SQL Warehouse** | Auto-scales, scales to zero — no idle costs |
| Size | **Small (2X-Small to Small)** | Start small; upgrade if queries are slow |
| Auto-stop | **10 minutes** of inactivity | Eliminates idle costs |
| Channel | **Current** | Latest stable SQL engine |
| Concurrent queries | Up to 10 | Sufficient for your team size |

**Monthly cost estimate:** ~$200-400 AUD/month (usage-based, scales to zero)

> **Why SQL Warehouse instead of a regular cluster for SQL?**
> SQL Warehouses are optimised for concurrent BI workloads (Power BI, Tableau). They handle multiple analysts querying simultaneously without performance degradation.

### Cluster 3: Interactive ML Cluster (Data Scientist)

Used for exploratory analysis, model training, and notebook development.

| Setting | Value | Reason |
|---|---|---|
| Cluster type | **All-purpose cluster** | Persistent, interactive — needed for notebooks |
| Runtime | **Databricks Runtime ML 14.x LTS** | Pre-installed: scikit-learn, TensorFlow, PyTorch, MLflow |
| Worker type | `Standard_DS4_v2` (28 GB, 8 cores) | More memory for ML workloads and large DataFrames |
| Workers | 1-3 (autoscaling) | Single worker often enough for exploration |
| Auto-terminate | **60 minutes** idle | Data scientist may leave notebooks open |
| Spot instances | Yes (acceptable for ML experiments) | Experiments can be retried if interrupted |
| Photon | Disabled | Photon optimises SQL; ML workloads don't benefit |

**Monthly cost estimate:** ~$300-500 AUD/month (assuming 6-8 hours/day usage)

### Cluster 4: Streaming Cluster (Real-time Ingestion)

For processing wearable/device data streams via Azure Event Hubs + Spark Structured Streaming.

| Setting | Value | Reason |
|---|---|---|
| Cluster type | **Job Cluster (long-running)** | Streaming jobs run continuously |
| Runtime | Databricks Runtime 14.x LTS | Standard runtime sufficient for streaming |
| Worker type | `Standard_DS3_v2` | Streaming is I/O bound, not compute heavy |
| Workers | 2 (fixed) | Fixed for predictable throughput |
| Auto-terminate | **Off** | Streaming must run 24/7 |
| Spot instances | **No** | Spot interruptions break streaming pipelines |

**Monthly cost estimate:** ~$500-800 AUD/month (24/7 operation)

### Cost Summary (Early Production Phase)

| Cluster | Purpose | Est. Monthly (AUD) |
|---|---|---|
| ETL Job Cluster | Data pipelines | $400-600 |
| SQL Warehouse | BI / Analytics | $200-400 |
| ML Interactive | Data science | $300-500 |
| Streaming Cluster | Real-time ingestion | $500-800 |
| **ADLS Gen2 storage** | Data lake (1 TB) | ~$50-80 |
| **Total estimate** | | **$1,450-2,380/month** |

> **Free Trial Strategy:** Use your $200 credit to test ETL pipelines and the SQL Warehouse. Avoid running the streaming cluster 24/7 during the trial. Use `dbutils.fs` and small sample datasets to validate your architecture before going live.

---

## 7. Data Lakehouse Setup (Delta Lake)

All data in your lake is stored in **Delta format** — not raw CSV or Parquet. Delta gives you:
- **ACID transactions** — no partial writes corrupting patient data
- **Schema enforcement** — rejects data that doesn't match expected structure
- **Time travel** — query data as it was at any point in the past (critical for audits)
- **MERGE** operations — upsert records efficiently

### Creating Your First Delta Table (Patient Records)

```python
# In a Databricks notebook

# Define schema explicitly — never infer schema for PHI data
from pyspark.sql.types import *

patient_schema = StructType([
    StructField("patient_id", StringType(), False),       # NOT nullable
    StructField("given_name", StringType(), True),
    StructField("family_name", StringType(), True),
    StructField("date_of_birth", DateType(), True),
    StructField("gender", StringType(), True),
    StructField("medicare_number", StringType(), True),   # Australian Medicare
    StructField("postcode", StringType(), True),
    StructField("ingested_at", TimestampType(), False),
    StructField("source_system", StringType(), False)
])

# Write to Bronze (raw layer) with Delta format
df_raw_patients.write \
    .format("delta") \
    .mode("append") \
    .option("mergeSchema", "false") \   # Reject schema changes — strict in healthcare
    .save("abfss://bronze@adlshealthstartupprod.dfs.core.windows.net/patients/")
```

### Delta Live Tables (DLT) — Recommended for ETL Pipelines

Instead of writing Spark jobs manually, use **Delta Live Tables** for your pipelines. DLT handles:
- Dependency management between tables
- Data quality checks (quarantine bad records)
- Automatic retries and error handling
- Built-in lineage tracking

```python
# DLT Pipeline definition — bronze_to_silver.py
import dlt
from pyspark.sql.functions import col, current_timestamp, sha2, concat_ws

# Bronze table — raw data as received
@dlt.table(
    name="bronze_patients",
    comment="Raw patient data from FHIR API — do not modify",
    table_properties={"quality": "bronze"}
)
def bronze_patients():
    return (
        spark.readStream
            .format("cloudFiles")              # Auto Loader — efficient incremental ingest
            .option("cloudFiles.format", "json")
            .option("cloudFiles.schemaLocation", "/checkpoints/patients/schema")
            .load("abfss://bronze@adlshealthstartupprod.dfs.core.windows.net/fhir/patients/")
    )

# Silver table — validated and pseudonymised
@dlt.expect_or_drop("valid_patient_id", "patient_id IS NOT NULL")
@dlt.expect_or_drop("valid_dob", "date_of_birth <= current_date()")
@dlt.table(
    name="silver_patients",
    comment="Validated patient records with pseudonymised identifiers",
    table_properties={"quality": "silver", "contains_phi": "true"}
)
def silver_patients():
    return (
        dlt.read_stream("bronze_patients")
            .withColumn(
                "patient_id_hash",
                sha2(col("patient_id"), 256)   # Pseudonymise — never expose raw IDs in Silver
            )
            .withColumn("processed_at", current_timestamp())
            .drop("medicare_number")            # Strip direct identifiers in Silver
    )
```

---

## 8. ETL Pipeline Design

### Ingestion Pattern: Auto Loader (Recommended)

Auto Loader (`cloudFiles`) is the recommended way to ingest files from ADLS into Delta tables. It:
- Tracks which files have been processed (no duplicates)
- Handles schema evolution
- Scales to millions of files

```python
# Example: Ingest HL7/CSV files dropped into ADLS by clinic systems
df = (
    spark.readStream
        .format("cloudFiles")
        .option("cloudFiles.format", "csv")
        .option("cloudFiles.schemaLocation", "/checkpoints/hl7/schema")
        .option("header", "true")
        .load("abfss://bronze@adlshealthstartupprod.dfs.core.windows.net/hl7-drops/")
)

df.writeStream \
    .format("delta") \
    .option("checkpointLocation", "/checkpoints/hl7/data") \
    .trigger(availableNow=True) \               # Process all available files, then stop
    .start("abfss://bronze@adlshealthstartupprod.dfs.core.windows.net/hl7/")
```

### Pipeline Schedule

| Pipeline | Trigger | Cluster |
|---|---|---|
| Raw ingestion (FHIR/HL7 → Bronze) | Every 1 hour | ETL Job Cluster |
| Bronze → Silver transformation | Every 2 hours | ETL Job Cluster |
| Silver → Gold aggregation | Every 4 hours | ETL Job Cluster |
| ML feature engineering | Daily at 2am | ETL Job Cluster |
| Streaming (wearables) | Continuous | Streaming Cluster |

---

## 9. Real-time Streaming Setup

### Azure Event Hubs → Databricks Structured Streaming

**Step 1: Create Azure Event Hubs Namespace**

```bash
az eventhubs namespace create \
  --name evhns-healthstartup-prod \
  --resource-group rg-healthstartup-prod \
  --location australiaeast \
  --sku Standard \
  --capacity 1
```

**Step 2: Create an Event Hub for device data**

```bash
az eventhubs eventhub create \
  --name evh-wearables \
  --namespace-name evhns-healthstartup-prod \
  --resource-group rg-healthstartup-prod \
  --partition-count 4 \
  --message-retention 1
```

**Step 3: Stream from Event Hubs in Databricks**

```python
# Stream wearable data from Event Hubs into Delta
connection_string = dbutils.secrets.get(scope="kv-healthstartup", key="eventhub-connection-string")

df_stream = (
    spark.readStream
        .format("eventhubs")
        .option("eventhubs.connectionString", sc._jvm.org.apache.spark.eventhubs.EventHubsUtils.encrypt(connection_string))
        .load()
)

# Parse the JSON payload from the wearable device
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import *

device_schema = StructType([
    StructField("device_id", StringType()),
    StructField("patient_id_hash", StringType()),   # Only hashed ID from device
    StructField("heart_rate", IntegerType()),
    StructField("spo2", DoubleType()),
    StructField("timestamp", TimestampType())
])

df_parsed = (
    df_stream
        .select(from_json(col("body").cast("string"), device_schema).alias("data"), "enqueuedTime")
        .select("data.*", "enqueuedTime")
)

# Write to Bronze Delta table
df_parsed.writeStream \
    .format("delta") \
    .option("checkpointLocation", "/checkpoints/wearables/") \
    .outputMode("append") \
    .start("abfss://bronze@adlshealthstartupprod.dfs.core.windows.net/wearables/")
```

---

## 10. Security & Australian Privacy Compliance

### Data Classification

Label all tables in Unity Catalog:

| Classification | Examples | Access |
|---|---|---|
| **PHI (Protected Health Info)** | Patient names, DOB, Medicare number | Data Engineers only (Bronze) |
| **Pseudonymised** | Hashed patient IDs, clinical data | Engineers + Data Scientist (Silver) |
| **De-identified** | Aggregated cohort data, no individuals | All teams (Gold) |

### Unity Catalog — Column-Level Security (PHI Masking)

```sql
-- Mask Medicare number for analysts — they see XXX-XXX-X only
CREATE MASK mask_medicare ON COLUMN silver_db.patients.medicare_number
  USING COLUMNS (medicare_number)
  RETURN CASE
    WHEN IS_MEMBER('grp-databricks-admins') THEN medicare_number
    ELSE REGEXP_REPLACE(medicare_number, '[0-9]', 'X')
  END;
```

### Encryption Requirements (Australian Privacy Act)

| Requirement | Azure/Databricks Configuration |
|---|---|
| Encryption at rest | ADLS Gen2 with Azure-managed keys (default) or Customer-Managed Keys (CMK) |
| Encryption in transit | TLS 1.2 enforced (set on storage account) |
| Key management | Azure Key Vault with RBAC — rotate keys annually |
| Cluster storage encryption | Enable in Databricks cluster config: `spark.databricks.delta.encrypt.enable true` |

### Audit Logging (My Health Records Act Requirement)

Enable Databricks audit logging to track all data access:

1. In Databricks workspace settings → **Audit Logs → Enable**
2. Route logs to **Azure Monitor / Log Analytics Workspace**
3. Set retention to **7 years** (Australian health records requirement)

```bash
# Create Log Analytics Workspace for audit logs
az monitor log-analytics workspace create \
  --resource-group rg-healthstartup-prod \
  --workspace-name law-healthstartup-audit \
  --location australiaeast \
  --retention-time 2557  # 7 years in days
```

### Network Security

| Control | Setting |
|---|---|
| Databricks VNet injection | Deploy workspace inside your own Azure VNet |
| No public cluster IPs | Enable "No Public IP" in workspace config |
| Private endpoints | ADLS Gen2 and Key Vault accessible only via private endpoint |
| IP allowlisting | Restrict Databricks UI access to office IP / VPN |

---

## 11. Cost Optimisation Strategy

### 1. Cluster Auto-Termination (Most Impactful)

Set auto-termination on every interactive cluster. A forgotten cluster running overnight:
- `Standard_DS4_v2` × 2 workers = ~$4-6 AUD/hour
- 8 hours forgotten = $32-48 wasted

### 2. Use Spot Instances for Dev/Test

Apply 60-80% savings on non-critical workloads:
- ETL development runs → Spot OK
- ML training experiments → Spot OK (checkpoint frequently)
- Production ETL jobs → On-demand
- Streaming cluster → On-demand (Spot will interrupt your stream)

### 3. Use Job Clusters, Not All-Purpose Clusters for Production

Job clusters start fresh for each run and terminate immediately after.
All-purpose clusters stay running (good for interactive work, costly if left idle).

### 4. SQL Warehouse Auto-Stop

Power BI reports often run on a schedule. Ensure SQL Warehouse auto-stops after 10 minutes of inactivity — saves ~70% of SQL compute costs.

### 5. Delta Table Optimisation (Reduces Compute Time)

```python
# Run weekly — compacts small files, speeds up queries
spark.sql("OPTIMIZE healthstartup_catalog.silver_db.patients ZORDER BY (patient_id_hash)")

# Remove old versions (keeps 7 years for compliance but removes daily noise)
spark.sql("VACUUM healthstartup_catalog.silver_db.patients RETAIN 2160 HOURS")  # 90 days minimum; adjust for compliance
```

### 6. Azure Reserved Instances (After 3 Months)

Once you know your baseline usage, buy 1-year Azure Reserved VM Instances for your streaming cluster — saves up to 40% on compute.

---

## 12. Free Trial Roadmap

### Week 1 — Foundation (Free Trial)
- [ ] Create Azure subscription, resource group, ADLS Gen2
- [ ] Create Databricks workspace (Premium SKU)
- [ ] Configure Unity Catalog and secret scope
- [ ] Create Bronze/Silver/Gold containers
- [ ] Ingest one sample dataset (e.g., synthetic patient CSV)

### Week 2 — Pipelines (Free Trial)
- [ ] Build first DLT pipeline (Bronze → Silver)
- [ ] Create SQL Warehouse, connect Power BI
- [ ] Ingest streaming data from a simulated Event Hub
- [ ] Test audit logging

### Week 3 — Security & Governance (Free Trial)
- [ ] Apply column masking on PHI fields
- [ ] Set up Azure AD groups and RBAC in Unity Catalog
- [ ] Enable private endpoints for storage
- [ ] Document your data flows (required for Privacy Act compliance)

### Month 2 — Production Readiness (Paid)
- [ ] Move to pay-as-you-go or reserved pricing
- [ ] Set up Dev and Prod workspaces
- [ ] Implement CI/CD for notebooks (Azure DevOps or GitHub Actions)
- [ ] Schedule production ETL jobs via Databricks Workflows
- [ ] Engage a privacy/legal consultant to review your data handling

---

## 13. Next Steps & Growth Path

| Stage | When | What to add |
|---|---|---|
| **MVP** | Month 1-2 | Core lakehouse, basic ETL, SQL dashboard |
| **Growth** | Month 3-6 | ML models (readmission risk, patient cohorts), FHIR API integration |
| **Scale** | Month 6-12 | Separate Dev/Staging/Prod workspaces, CI/CD, data contracts |
| **Enterprise** | Year 2+ | Multi-region (disaster recovery), real-time ML inference, data mesh |

---

## Appendix: Key Azure Resources Reference

| Resource | Name Pattern | Purpose |
|---|---|---|
| Resource Group | `rg-healthstartup-{env}` | Container for all resources |
| Storage Account | `adlshealthstartup{env}` | ADLS Gen2 data lake |
| Databricks Workspace | `adb-healthstartup-{env}` | Databricks environment |
| Key Vault | `kv-healthstartup-{env}` | Secrets management |
| Event Hubs Namespace | `evhns-healthstartup-{env}` | Streaming ingestion |
| Log Analytics Workspace | `law-healthstartup-audit` | Audit logs (7-year retention) |

---

*Document version: 1.0 | Created: 2026-03-27 | Region: Australia East | Compliance: Australian Privacy Act 1988*
