# Healthcare Data Platform — Azure Databricks

A production-grade healthcare data lakehouse built on Azure Databricks, implementing the **Medallion Architecture** (Bronze → Silver → Gold) with full compliance for the **Australian Privacy Act 1988** and **My Health Records Act 2012**.

## Architecture Overview

```
Clinic ERP Systems
        │
        ▼
┌───────────────────────────────────────────────────────────┐
│                    Azure Data Lake Gen2                    │
│                                                           │
│  ┌──────────┐    ┌──────────┐    ┌──────────────────────┐ │
│  │  BRONZE  │───▶│  SILVER  │───▶│         GOLD         │ │
│  │ Raw data │    │ PHI      │    │ Aggregated analytics  │ │
│  │ Delta    │    │ removed  │    │ Power BI ready        │ │
│  └──────────┘    └──────────┘    └──────────────────────┘ │
└───────────────────────────────────────────────────────────┘
        │                                      │
        ▼                                      ▼
Azure Databricks                         SQL Warehouse
Delta Live Tables                         + Power BI
(DLT Pipeline)                           Dashboard
```

## What This Project Demonstrates

| Skill | Implementation |
|-------|---------------|
| Cloud Architecture | Azure resource design, RBAC, Key Vault |
| Data Engineering | Delta Lake, Medallion Architecture, DLT pipelines |
| Security | PHI removal, OAuth authentication, table permissions |
| Compliance | Australian Privacy Act, data residency |
| Analytics | SQL Warehouse, Power BI integration |
| Streaming | Azure Event Hubs setup |

## Technology Stack

- **Cloud:** Microsoft Azure (Australia East)
- **Compute:** Azure Databricks Premium
- **Storage:** Azure Data Lake Storage Gen2
- **Table Format:** Delta Lake
- **Pipeline:** Delta Live Tables (DLT)
- **Secrets:** Azure Key Vault
- **Authentication:** OAuth 2.0 Service Principal
- **BI:** Power BI Desktop
- **Streaming:** Azure Event Hubs

## Repository Structure

```
healthcare-databricks-platform/
├── README.md                          # This file
├── notebooks/
│   ├── 01_bronze_ingest.py            # Raw data ingestion to bronze layer
│   └── 02_verify_silver_gold.py       # Data verification notebook
├── pipelines/
│   └── patient_etl_pipeline.py        # DLT pipeline: Bronze → Silver → Gold
├── infrastructure/
│   └── azure-setup-guide.md           # Step-by-step Azure setup
├── docs/
│   └── detailed-guide-and-interview-prep.md  # Full technical guide + 20 interview Q&As
└── scripts/
    └── create-secret-scope.ps1        # Databricks secret scope creation
```

## Data Flow

### Bronze Layer — Raw Ingestion
- Stores patient records exactly as received from clinic ERP
- Schema: `patient_id, given_name, family_name, date_of_birth, gender, medicare_number, postcode, ingested_at, source_system`
- No transformations — full audit trail

### Silver Layer — PHI Removed
- Removes: `patient_id` (hashed with SHA-256), `given_name`, `family_name`, `medicare_number`
- Retains: `patient_id_hash`, `date_of_birth`, `gender`, `postcode`, `source_system`
- Adds: `silver_processed_at`, `data_quality` flag
- Compliant with Australian Privacy Act APP 3 (data minimisation)

### Gold Layer — Analytics Ready
**gold_patients_by_postcode:**
```
postcode | patient_count | female_count | male_count
2000     | 1             | 1            | 0
3000     | 1             | 0            | 1
```

**gold_data_quality_summary:**
```
data_quality | source_system | record_count
OK           | clinic-erp    | 2
```

## Key Design Decisions

### Why Medallion Architecture?
Separates raw data (Bronze) from analytics (Gold) via a compliance layer (Silver). Analysts never touch PHI. Data can be reprocessed from Bronze if Silver/Gold logic changes.

### Why Delta Live Tables?
Declarative pipelines with automatic dependency resolution, built-in data quality expectations, and pipeline lineage tracking — reducing boilerplate ETL code by ~70%.

### Why OAuth over Storage Keys for DLT?
Databricks Serverless DLT blocks storage account keys (security policy). OAuth service principal provides auditable, role-scoped access with short-lived tokens.

### Why SHA-256 for Patient ID?
One-way hash allows cross-dataset record linking without exposing real patient IDs. Cannot be reversed. Consistent — same input always produces same output.

## Azure Resources Created

| Resource | Name | SKU/Tier |
|----------|------|---------|
| Resource Group | rg-healthstartup-prod | - |
| ADLS Gen2 | adlshealthstartupprod | Standard LRS |
| Key Vault | kv-healthstartup-prod | Standard |
| Databricks Workspace | adb-healthstartup-prod | Premium |
| SQL Warehouse | sql-healthstartup | 2X-Small Serverless |
| Event Hubs Namespace | evhns-healthstartup-prod | Basic |

## Compliance

| Regulation | Status | Implementation |
|-----------|--------|---------------|
| Australian Privacy Act 1988 | Implemented | PHI removal at silver, data minimisation, access controls |
| My Health Records Act 2012 | Implemented | Data residency in Australia East, audit trail via Delta log |
| Table Access Control | Enabled | SELECT-only on silver/gold for analysts |
| Data Residency | Australia East | All resources in Sydney region |

## Setup Instructions

See [infrastructure/azure-setup-guide.md](infrastructure/azure-setup-guide.md) for full step-by-step setup.

## Interview Preparation

See [docs/detailed-guide-and-interview-prep.md](docs/detailed-guide-and-interview-prep.md) for:
- 20 senior data engineer interview questions with detailed answers
- Architecture decision rationale
- Comparison of alternative approaches
- System design questions

## Author

Vaishnavi Avula
- Healthcare Data Platform built on Azure Databricks (Free Trial)
- Location: Australia
- Compliance: Australian Privacy Act 1988
