# Healthcare Data Platform on Azure Databricks
## Detailed Technical Guide + Interview Preparation
### Covering 6 Rounds of Senior Data Engineer Interviews

---

## Table of Contents
1. [Project Overview](#1-project-overview)
2. [Architecture Design](#2-architecture-design)
3. [Azure Infrastructure Setup](#3-azure-infrastructure-setup)
4. [Azure Databricks Setup](#4-azure-databricks-setup)
5. [Security & Credential Management](#5-security--credential-management)
6. [Delta Lake & Medallion Architecture](#6-delta-lake--medallion-architecture)
7. [Delta Live Tables (DLT)](#7-delta-live-tables-dlt)
8. [SQL Warehouse & Power BI](#8-sql-warehouse--power-bi)
9. [Compliance - Australian Privacy Act](#9-compliance---australian-privacy-act)
10. [Interview Questions & Answers](#10-interview-questions--answers)

---

## 1. Project Overview

### What we built
A production-grade healthcare data lakehouse on Azure Databricks that:
- Ingests raw patient records from clinic ERP systems
- Removes Personally Identifiable Information (PHI) automatically
- Produces clean, aggregated analytics tables for dashboards
- Complies with Australian Privacy Act 1988 and My Health Records Act 2012

### Technology Stack
| Component | Technology | Why chosen |
|-----------|-----------|------------|
| Cloud | Microsoft Azure | Free trial available, strong healthcare compliance certifications |
| Data Warehouse | Azure Databricks (Premium) | Best-in-class Spark engine, Delta Lake built-in, DLT for pipelines |
| Storage | Azure Data Lake Storage Gen2 | Hierarchical namespace, fine-grained RBAC, optimised for big data |
| Secret Management | Azure Key Vault | Industry standard, integrates natively with Databricks |
| Table Format | Delta Lake | ACID transactions, time travel, schema evolution |
| Pipeline Orchestration | Delta Live Tables (DLT) | Declarative pipelines, built-in data quality, automatic lineage |
| BI Dashboard | Power BI | Native Databricks connector, widely used in enterprises |
| Real-time Ingestion | Azure Event Hubs | Kafka-compatible, scales to millions of events/second |

---

## 2. Architecture Design

### Medallion Architecture (Bronze → Silver → Gold)

```
Source Systems (Clinic ERP)
         │
         ▼
┌─────────────────┐
│   BRONZE LAYER  │  Raw data, unchanged
│  Delta Table    │  Full audit trail
│  ADLS Gen2      │  Retain forever
└────────┬────────┘
         │
         ▼ DLT Pipeline
┌─────────────────┐
│   SILVER LAYER  │  PHI removed
│  Delta Table    │  Data quality checked
│  ADLS Gen2      │  Privacy Act compliant
└────────┬────────┘
         │
         ▼ DLT Pipeline
┌─────────────────┐
│    GOLD LAYER   │  Aggregated analytics
│  Delta Tables   │  Zero re-identification risk
│  ADLS Gen2      │  BI/Dashboard ready
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  SQL Warehouse  │  ANSI SQL endpoint
│  Power BI       │  Dashboards & reports
└─────────────────┘
```

### Why Medallion Architecture?

**Problem without it:**
- Analysts query raw data containing patient names and Medicare numbers
- One SQL mistake exposes PHI to everyone
- No audit trail of what data existed at what time
- Fixing a bug requires reprocessing from scratch

**With Medallion Architecture:**
- Bronze = immutable raw data (never query directly in analytics)
- Silver = safe data for data engineers/scientists
- Gold = safe data for business analysts and dashboards
- Each layer has clear ownership and access controls

### Alternative Architecture Approaches

| Approach | Pros | Cons | When to use |
|----------|------|------|-------------|
| **Medallion (chosen)** | Clear separation, reprocessable, compliant | More complex | Healthcare, finance, regulated industries |
| **Lambda Architecture** | Real-time + batch combined | Complex, two codebases | When sub-second latency needed |
| **Kappa Architecture** | Simple, stream-only | Hard to reprocess history | Event-driven systems |
| **Data Vault** | Extremely flexible schema | Very complex to query | Enterprise EDW with frequent source changes |
| **One Big Table** | Simple queries | No PHI separation, not scalable | Tiny datasets, no compliance needs |

---

## 3. Azure Infrastructure Setup

### 3.1 Resource Group

**What:** A logical container for all Azure resources in this project.

**Why:**
- Groups related resources together for easier management
- One-click delete entire project when done
- Cost tracking per project
- Apply security policies to all resources at once

**Command equivalent:**
```bash
az group create --name rg-healthstartup-prod --location australiaeast
```

**Naming convention used:** `{type}-{project}-{environment}`
- `rg` = resource group
- `healthstartup` = project name
- `prod` = environment

**Alternative approaches:**
- Multiple resource groups (e.g., one for data, one for compute) — better for large teams
- Management groups — for managing multiple Azure subscriptions

---

### 3.2 Azure Data Lake Storage Gen2 (ADLS Gen2)

**What:** Cloud object storage with hierarchical namespace, optimised for big data analytics.

**Why ADLS Gen2 over other options:**

| Storage Option | Use case | Why not for us |
|---------------|----------|----------------|
| **ADLS Gen2 (chosen)** | Big data analytics | Perfect fit |
| Azure Blob Storage | General file storage | No hierarchical namespace, slower for Spark |
| Azure SQL Database | Relational data | Not designed for big data, expensive at scale |
| Azure Cosmos DB | NoSQL, global distribution | Overkill, expensive |
| Azure Files | SMB file shares | Not optimised for Spark |

**Container structure:**
```
adlshealthstartupprod/
├── bronze/     # Raw data - restricted access
│   └── patients/
├── silver/     # Cleaned data - data engineer access
│   └── patients/
├── gold/       # Analytics data - analyst access
│   └── patients_by_postcode/
│   └── data_quality_summary/
└── ml/         # ML model training data
```

**Why separate containers per layer?**
- Different access controls (IAM roles) per container
- Bronze can be locked down completely after processing
- Gold can be opened to more users safely
- Cost allocation per layer

**ABFS path format:**
```
abfss://container@storageaccount.dfs.core.windows.net/path
```
The double `ss` = SSL/TLS encrypted. Always use `abfss://` (never `abfs://`) for sensitive data.

---

### 3.3 Azure Key Vault

**What:** Cloud-hosted secrets management service. Stores passwords, API keys, connection strings securely.

**Why Key Vault:**
- Never hardcode credentials in notebooks or code
- Automatic secret rotation support
- Audit log of every secret access
- Role-based access - Databricks can read secrets, developers cannot see raw values
- FIPS 140-2 Level 2 validated HSM backing

**Secrets stored:**

| Secret Name | Value | Why needed |
|-------------|-------|------------|
| `adls-storage-key` | Storage account access key | Databricks → ADLS Gen2 connection |
| `sp-client-id` | Service principal app ID | OAuth authentication |
| `sp-client-secret` | Service principal password | OAuth authentication |
| `tenant-id` | Azure AD tenant GUID | OAuth token endpoint |
| `eventhub-connection-string` | Event Hubs connection | Streaming ingestion |

**Access mode: RBAC (not Vault Access Policy)**

Why RBAC over Vault Access Policy?
- Vault Access Policy is being deprecated by Microsoft
- RBAC gives more granular control
- Consistent with Azure-wide permission model
- Supports Privileged Identity Management (just-in-time access)

**Roles assigned:**
- Your user account → `Key Vault Secrets Officer` (read/write secrets)
- AzureDatabricks service principal → `Key Vault Secrets User` (read secrets only)

---

### 3.4 Azure App Registration (Service Principal)

**What:** An identity for Databricks to authenticate to Azure services (like a "service account").

**Why service principal over user account:**
- User accounts have passwords that expire and change
- Service principals have long-lived credentials
- Follows principle of least privilege
- No MFA prompts interrupting automated pipelines
- Auditable — all actions logged under service identity

**OAuth 2.0 flow used:**
```
Databricks → Key Vault (get client_id + client_secret)
    → Azure AD token endpoint
    → Access token (valid 1 hour)
    → ADLS Gen2 (authenticated request)
```

**Alternative authentication methods:**

| Method | Security | Complexity | Use when |
|--------|----------|------------|----------|
| **OAuth Service Principal (chosen)** | High | Medium | Production pipelines |
| Storage Account Key | Low | Low | Development/testing only |
| Managed Identity | Very High | Low | When Databricks supports it natively |
| SAS Token | Medium | Low | Temporary, time-limited access |
| Azure AD Pass-through | High | Medium | User-level audit trail needed |

---

## 4. Azure Databricks Setup

### 4.1 Workspace — Premium SKU

**Why Premium over Standard:**

| Feature | Standard | Premium |
|---------|----------|---------|
| Delta Live Tables | No | Yes |
| Role-based access control | No | Yes |
| Audit logs | No | Yes |
| Table ACLs | No | Yes |
| Secret scopes (Key Vault backed) | No | Yes |
| Cost | Lower | ~$0.07/DBU more |

For healthcare compliance, Premium is mandatory — Standard lacks audit logging and access controls.

---

### 4.2 Cluster Design

**Cluster created: `etl-job-cluster`**

| Setting | Value | Reason |
|---------|-------|--------|
| Runtime | 14.3 LTS ML | LTS = Long Term Support, stable for production |
| Node type | Standard_D4ds_v5 | 4 cores, 16GB RAM — sufficient for medium data |
| Mode | Single Node | Reduces cost for development/small data |
| Auto-terminate | 20 minutes | Saves cost — no idle cluster charges |

**Cluster types comparison:**

| Type | Use case | Cost |
|------|----------|------|
| **Single Node (chosen)** | Development, small data | Lowest |
| Multi-node (fixed) | Production batch jobs | Fixed cost |
| Autoscaling | Variable workloads | Pay per use |
| Serverless (DLT) | Managed pipelines | Per DBU, no VM management |
| SQL Warehouse | SQL analytics/BI | Per DBU when active |

**Databricks Runtime versions:**
- LTS (Long Term Support) — stable, security patches for 2+ years → use for production
- ML — includes popular ML libraries (MLflow, TensorFlow, PyTorch)
- Photon — C++ vectorised query engine, 2-3x faster for SQL → use for analytics
- GPU — NVIDIA drivers pre-installed → use for deep learning

---

### 4.3 Databricks CLI Configuration

**What:** Command-line interface to manage Databricks resources programmatically.

**Configuration file:** `~/.databrickscfg`
```ini
[DEFAULT]
host = https://adb-7405607057216468.8.azuredatabricks.net
token = <personal-access-token>
```

**Why CLI over UI?**
- Automatable — can script repetitive tasks
- Version controllable — store config in git
- CI/CD pipelines use CLI to deploy notebooks/jobs
- Faster for bulk operations

---

### 4.4 Databricks Secret Scope

**What:** A named group of secrets accessible to notebooks and jobs.

**Type used: AZURE_KEYVAULT backed**

```python
# Access pattern in notebooks:
value = dbutils.secrets.get(scope="kv-healthstartup", key="adls-storage-key")
```

**Why Key Vault backed scope over Databricks-native scope:**

| Feature | Databricks Native | Azure Key Vault Backed |
|---------|------------------|----------------------|
| Secret storage | Databricks servers | Azure Key Vault |
| Audit log | Basic | Full Azure Monitor audit |
| Secret rotation | Manual | Supports auto-rotation |
| Access control | Databricks ACLs | Azure RBAC |
| Compliance | Limited | Full Azure compliance certifications |

For healthcare, Key Vault backed is the correct choice.

**Creation method:** Must use UI (not CLI) when using personal Microsoft accounts. The CLI requires AAD tokens for Key Vault-backed scopes.

---

## 5. Security & Credential Management

### 5.1 Why Never Hardcode Credentials

Bad practice (NEVER do this):
```python
# WRONG - credentials in code
spark.conf.set(
    "fs.azure.account.key.mystorageaccount.dfs.core.windows.net",
    "ABC123secretkeyXYZ"  # This gets committed to git!
)
```

Good practice:
```python
# CORRECT - credentials from Key Vault
spark.conf.set(
    "fs.azure.account.key.mystorageaccount.dfs.core.windows.net",
    dbutils.secrets.get(scope="kv-healthstartup", key="adls-storage-key")
)
```

**Risks of hardcoded credentials:**
- Git history exposes secrets forever (even after deletion)
- Anyone with notebook access can read the key
- Cannot rotate without code changes
- Violates ISO 27001, SOC 2, HIPAA, Privacy Act requirements

---

### 5.2 Table-Level Permissions

```sql
-- Grant read-only access to silver table
GRANT SELECT ON TABLE adb_healthstartup_prod.default.silver_patients
TO `analyst@company.com`;

-- Grant full access to data engineers
GRANT ALL PRIVILEGES ON TABLE adb_healthstartup_prod.default.bronze_patients
TO `dataengineer@company.com`;
```

**Access control matrix:**

| Role | Bronze | Silver | Gold |
|------|--------|--------|------|
| Data Engineer | Read/Write | Read/Write | Read/Write |
| Data Scientist | Read | Read | Read |
| Business Analyst | No access | No access | Read |
| Power BI Service | No access | No access | Read |

---

## 6. Delta Lake & Medallion Architecture

### 6.1 What is Delta Lake?

Delta Lake is an open-source storage layer that adds ACID transactions to Apache Spark and big data workloads. It stores data as Parquet files plus a `_delta_log` transaction log.

**Delta table structure on disk:**
```
patients/
├── _delta_log/
│   ├── 00000000000000000000.json  # Transaction 0 - table created
│   ├── 00000000000000000001.json  # Transaction 1 - data added
│   └── 00000000000000000002.json  # Transaction 2 - update
├── part-00000-abc123.parquet
├── part-00001-def456.parquet
└── part-00002-ghi789.parquet
```

### 6.2 Delta Lake vs Other Formats

| Format | ACID | Time Travel | Schema Evolution | Streaming | Use case |
|--------|------|-------------|-----------------|-----------|----------|
| **Delta Lake (chosen)** | Yes | Yes | Yes | Yes | All-purpose lakehouse |
| Apache Parquet | No | No | Limited | No | Read-heavy analytics |
| Apache Iceberg | Yes | Yes | Yes | Limited | Multi-engine compatibility |
| Apache Hudi | Yes | Limited | Yes | Yes | Record-level upserts |
| CSV/JSON | No | No | No | No | Raw ingestion only |

**Why Delta over Iceberg/Hudi?**
- Native Databricks support — fully optimised
- DLT only supports Delta
- Databricks wrote Delta — best integration
- Largest community on Azure

### 6.3 Delta Lake Key Features Used

**ACID Transactions:**
```python
# Two writers can't corrupt each other's data
df.write.format("delta").mode("overwrite").save(path)
# If this fails halfway, the table is unchanged (no partial writes)
```

**Time Travel:**
```python
# Query data as it was yesterday
df = spark.read.format("delta").option("versionAsOf", 0).load(path)

# Or by timestamp
df = spark.read.format("delta") \
    .option("timestampAsOf", "2026-03-29") \
    .load(path)
```

**Schema Enforcement:**
```python
# Delta rejects records that don't match the schema
# Bronze table has: patient_id, given_name, date_of_birth...
# If source sends a record missing patient_id → rejected, not silently dropped
```

**Merge (Upsert):**
```python
from delta.tables import DeltaTable

target = DeltaTable.forPath(spark, bronze_path)
target.alias("target").merge(
    source=new_data.alias("source"),
    condition="target.patient_id = source.patient_id"
).whenMatchedUpdateAll() \
 .whenNotMatchedInsertAll() \
 .execute()
```

---

## 7. Delta Live Tables (DLT)

### 7.1 What is DLT?

Delta Live Tables is a declarative pipeline framework built on top of Spark. Instead of writing procedural ETL code, you declare what you want the output table to look like.

**Traditional Spark ETL (imperative):**
```python
# You manage dependencies, error handling, retries manually
bronze_df = spark.read.format("delta").load(bronze_path)
silver_df = bronze_df.withColumn(...)
silver_df.write.format("delta").save(silver_path)
```

**DLT (declarative):**
```python
# DLT manages dependencies, retries, monitoring automatically
@dlt.table
def silver_patients():
    bronze = dlt.read("bronze_patients")  # DLT resolves dependency
    return bronze.withColumn(...)
# DLT handles writing, schema management, lineage tracking
```

### 7.2 DLT vs Alternatives

| Approach | Dependency Mgmt | Data Quality | Lineage | Cost |
|----------|----------------|-------------|---------|------|
| **DLT (chosen)** | Automatic | Built-in expectations | Automatic | DBU charges |
| Apache Airflow | Manual | None built-in | Manual | Infrastructure cost |
| Azure Data Factory | GUI-based | Limited | Partial | Per activity |
| dbt | SQL only | Tests | Yes | Free (open source) |
| Custom Spark jobs | Manual | Manual | Manual | Cluster cost |

**When to use DLT:**
- Multiple dependent tables (Bronze → Silver → Gold)
- Need built-in data quality enforcement
- Want automatic lineage/observability
- Team prefers declarative over imperative

**When NOT to use DLT:**
- Simple one-off data loads
- Need exact control over execution order
- Cross-workspace pipelines
- Budget constraints (DLT has overhead)

### 7.3 DLT Compute Options

| Type | Cold start | Cost | Auth method | Unity Catalog |
|------|-----------|------|-------------|---------------|
| **Serverless (used)** | ~30 sec | Per DBU | OAuth required | Required for storage |
| Classic | 5-10 min | VM + DBU | spark.conf works | Optional |

**Why Serverless for DLT?**
- No VM capacity issues (Databricks manages infrastructure)
- Faster startup than Classic
- No cluster size tuning
- Automatic scaling

**Storage auth for Serverless DLT:**
Classic compute: `spark.hadoop.fs.azure.account.key...` works
Serverless: Must use OAuth service principal via pipeline Configuration

```
# Pipeline Configuration (not in notebook code):
fs.azure.account.auth.type.storageaccount.dfs.core.windows.net = OAuth
fs.azure.account.oauth.provider.type.storageaccount.dfs.core.windows.net = org.apache.hadoop.fs.azurebfs.oauth2.ClientCredsTokenProvider
fs.azure.account.oauth2.client.id.storageaccount.dfs.core.windows.net = {{secrets/scope/sp-client-id}}
fs.azure.account.oauth2.client.secret.storageaccount.dfs.core.windows.net = {{secrets/scope/sp-client-secret}}
fs.azure.account.oauth2.client.endpoint.storageaccount.dfs.core.windows.net = https://login.microsoftonline.com/<tenant-id>/oauth2/token
```

### 7.4 DLT Data Quality — Expectations

```python
# Drop records that fail validation
@dlt.expect_or_drop("valid_gender", "gender IN ('M', 'F')")

# Warn but keep records
@dlt.expect("valid_postcode", "LENGTH(postcode) = 4")

# Fail entire pipeline if quality drops below threshold
@dlt.expect_or_fail("no_nulls", "patient_id IS NOT NULL")
```

**Important gotcha:** Expectations run on the RETURNED DataFrame (after all transformations). If you drop `patient_id` in the function body, you cannot reference `patient_id` in an expectation — use the derived column instead.

---

## 8. SQL Warehouse & Power BI

### 8.1 SQL Warehouse vs Spark Cluster

| Feature | SQL Warehouse | Interactive Cluster |
|---------|--------------|-------------------|
| **Interface** | ANSI SQL only | Python/SQL/R/Scala |
| **Users** | Analysts, BI tools | Data Engineers/Scientists |
| **Cold start** | ~15 sec (Serverless) | 3-5 min |
| **Auto-stop** | Configurable | Configurable |
| **Photon** | Always on | Optional |
| **Cost** | Per DBU | Per DBU + VM |

**Use SQL Warehouse when:**
- BI tools connecting (Power BI, Tableau, Looker)
- Analysts writing SQL queries
- Ad-hoc data exploration
- Need fast startup for infrequent queries

### 8.2 Power BI Connection

**Connection method used: Direct Query via Databricks Connector**

Connection details:
- Server: `adb-7405607057216468.8.azuredatabricks.net`
- HTTP Path: `/sql/1.0/warehouses/32798e2fd869fa6c`
- Authentication: Personal Access Token

**Import vs DirectQuery:**

| Mode | How it works | Best for |
|------|-------------|----------|
| Import | Copies data into Power BI | Small datasets, complex visuals |
| **DirectQuery (recommended)** | Queries Databricks live | Large datasets, always fresh data |
| Composite | Mix of both | Hybrid scenarios |

---

## 9. Compliance — Australian Privacy Act

### 9.1 Key Legislation

**Australian Privacy Act 1988 (Privacy Act):**
- Governs how personal information is collected, used, stored
- 13 Australian Privacy Principles (APPs)
- Applies to organisations with turnover > $3M (and all healthcare providers)
- Fines up to $50M for serious breaches (2022 amendment)

**My Health Records Act 2012:**
- Specific to electronic health records
- Strict rules on who can access medical records
- Criminal penalties for unauthorised access

### 9.2 How This Platform Addresses Compliance

| Requirement | Implementation |
|-------------|---------------|
| Data minimisation (APP 3) | Silver layer removes PHI — only keep what's needed for analytics |
| Purpose limitation (APP 6) | Gold layer aggregates — cannot identify individuals |
| Security safeguards (APP 11) | Key Vault for credentials, RBAC on all resources |
| Australian data residency | All resources in Australia East region |
| Audit trail | Delta Lake transaction log, Databricks audit logs |
| Access control | Table-level permissions, Secret scope restrictions |

### 9.3 PHI Removal Strategy

**Protected Health Information (PHI) removed at Silver layer:**
- `patient_id` → replaced with SHA-256 hash
- `given_name` → deleted
- `family_name` → deleted
- `medicare_number` → deleted

**Data retained (not PHI in aggregate context):**
- `date_of_birth` → needed for age-group analytics
- `gender` → needed for gender health disparity analysis
- `postcode` → needed for geographic health analysis
- `source_system` → needed for data lineage

**SHA-256 hashing rationale:**
```python
# SHA-256 is a one-way cryptographic hash
sha2("P001", 256) = "df1e40051eff4bcf9b4ebc93083bfcad..."
# Cannot reverse this to get "P001"
# But allows joining: P001 in dataset A = P001 in dataset B (same hash)
```

---

## 10. Interview Questions & Answers

### Round 1: Data Engineering Fundamentals

**Q1: What is the difference between a Data Lake, Data Warehouse, and Data Lakehouse?**

A:
- **Data Lake:** Stores raw data in any format (CSV, JSON, Parquet, images, logs). Cheap storage (S3/ADLS), no schema enforcement. Problem: becomes a "data swamp" — no quality control.
- **Data Warehouse:** Structured data only, enforced schema, optimised for SQL queries (Redshift, Snowflake, BigQuery). Fast queries but expensive, inflexible schema.
- **Data Lakehouse:** Combines both — cheap lake storage (Parquet files) + warehouse features (ACID, SQL, schema enforcement) via Delta Lake. Best of both worlds. Azure Databricks is a Lakehouse platform.

In this project, we built a **Lakehouse** — ADLS Gen2 (lake storage) + Delta Lake (warehouse features) + Databricks (compute engine).

---

**Q2: What is ACID in the context of Delta Lake?**

A:
- **Atomicity:** A transaction either fully succeeds or fully fails. No partial writes. If writing 1M rows fails at row 500K, Delta rolls back to the previous state.
- **Consistency:** Data always moves from one valid state to another. Schema constraints are never violated.
- **Isolation:** Concurrent readers and writers don't corrupt each other. Multiple notebooks can query while another is writing.
- **Durability:** Once committed, data survives crashes. The `_delta_log` acts as a write-ahead log.

Without ACID (e.g., plain Parquet): A failed write leaves partial files. Next read may return incomplete or corrupted data.

---

**Q3: Explain partitioning in Delta Lake. When would you use it?**

A: Partitioning physically organises files by column values.

```python
df.write.format("delta") \
  .partitionBy("year", "month") \
  .save(path)
# Creates: year=2026/month=01/part-00000.parquet
```

**Use partitioning when:**
- Querying always filters on that column (e.g., always filter by date)
- Column has medium cardinality (10-10,000 distinct values)
- Partitions are roughly equal in size (avoid skew)

**Don't partition when:**
- Column has high cardinality (patient_id = millions of tiny files)
- Queries don't filter on that column
- Dataset is small (< 1GB)

For our patient table: partition by `year` and `month` of `ingested_at` in production.

---

**Q4: What is Z-ordering in Delta Lake?**

A: Z-ordering co-locates related data in the same files to speed up queries that filter on multiple columns.

```python
spark.sql("OPTIMIZE patients ZORDER BY (postcode, date_of_birth)")
```

After Z-ordering, a query like `WHERE postcode = '2000' AND date_of_birth > '1980-01-01'` reads far fewer files because matching records are physically co-located.

Z-ordering vs Partitioning:
- Partitioning: Eliminates entire directories from scan
- Z-ordering: Reduces files read within a partition
- Use both together for maximum performance

---

### Round 2: Apache Spark & Distributed Computing

**Q5: What is a DataFrame in Spark? How is it different from an RDD?**

A:
- **RDD (Resilient Distributed Dataset):** Low-level, unstructured distributed collection. No schema, no optimisation. You control everything.
- **DataFrame:** Structured table with named columns and schema. Spark optimises execution via Catalyst query optimizer. 10-100x faster than RDD for most operations.
- **Dataset:** Strongly typed DataFrame (Scala/Java only). Best of both.

In practice: Always use DataFrames (or SQL) unless you need RDD-level control. DataFrames give you free optimisation.

```python
# RDD (avoid in modern Spark)
rdd = sc.parallelize([1, 2, 3])
rdd.map(lambda x: x * 2).collect()

# DataFrame (preferred)
df = spark.range(3)
df.withColumn("doubled", col("id") * 2).show()
```

---

**Q6: Explain Spark's lazy evaluation. Why does it matter?**

A: Spark doesn't execute transformations immediately — it builds a logical plan and only executes when an **action** is called.

```python
# These lines do NOT execute yet (lazy transformations):
df = spark.read.format("delta").load(path)      # 1
df2 = df.filter(col("postcode") == "2000")      # 2
df3 = df2.withColumn("upper_gender", upper(col("gender")))  # 3

# This triggers execution (action):
df3.show()  # Now Spark optimises and runs 1+2+3 together
```

**Why it matters:**
- Catalyst optimizer combines all transformations before running → avoids unnecessary data reads
- `filter` gets pushed down to the data source → read only matching rows
- Projection pushdown → read only needed columns

---

**Q7: What is a Spark shuffle? Why is it expensive?**

A: A shuffle is when data must be moved between partitions (and across network) to complete an operation.

Operations that trigger shuffles: `groupBy`, `join`, `distinct`, `orderBy`, `repartition`

Why expensive:
1. Data must be serialized, written to disk, transferred over network, deserialized
2. Can cause OOM (out of memory) errors on large datasets
3. Skew problem — if one partition has 10x more data, that executor becomes a bottleneck

**Optimisation techniques:**
```python
# 1. Broadcast join (avoid shuffle entirely for small table)
from pyspark.sql.functions import broadcast
df.join(broadcast(small_df), "postcode")  # small_df sent to all executors

# 2. Repartition before groupBy (distribute data evenly)
df.repartition(200, "postcode").groupBy("postcode").count()

# 3. Salting (fix skewed keys)
df.withColumn("salted_key", concat(col("postcode"), lit("_"), (rand() * 10).cast("int")))
```

---

**Q8: Explain the difference between `repartition` and `coalesce`.**

A:
- `repartition(n)`: Full shuffle — creates exactly n partitions, evenly distributed. Use when increasing partitions or fixing skew.
- `coalesce(n)`: Partial shuffle — combines existing partitions without full shuffle. Use when reducing partitions (e.g., before writing to fewer files). Much cheaper than repartition.

```python
# Writing to production — reduce to 1 file (small dataset)
df.coalesce(1).write.format("delta").save(path)

# Before groupBy on skewed data — redistribute evenly
df.repartition(200, "skewed_column").groupBy("skewed_column").count()
```

---

### Round 3: Cloud Architecture & Azure

**Q9: Explain Azure RBAC. What roles did you use in this project?**

A: RBAC (Role-Based Access Control) controls who can do what to which Azure resources.

Structure: `Who (Principal) can do What (Role) on Which (Scope)`

Roles used in this project:

| Principal | Role | Scope | Why |
|-----------|------|-------|-----|
| Your user account | Key Vault Secrets Officer | Key Vault | Read/write secrets |
| AzureDatabricks SP | Key Vault Secrets User | Key Vault | Read secrets (for secret scope) |
| databricks-storage-sp | Storage Blob Data Contributor | ADLS Gen2 | Read/write data |
| Your user account | Owner | Resource Group | Full control |

**Built-in roles commonly used in data platforms:**
- `Storage Blob Data Reader` — read-only storage access
- `Storage Blob Data Contributor` — read/write storage access
- `Key Vault Secrets User` — read secrets
- `Key Vault Secrets Officer` — manage secrets
- `Contributor` — manage resources (not assign permissions)
- `Owner` — full control including permission assignment

---

**Q10: What is a Service Principal? How is it different from a Managed Identity?**

A:
- **Service Principal:** Manual credential management. You create it, store the client_id and client_secret, and manage rotation. Used when the service (e.g., Databricks Serverless) is not Azure-native.
- **Managed Identity:** Azure automatically creates and rotates credentials. No secrets to manage. Only works for Azure-native services.

```
Service Principal: "I created a username/password for Databricks to use"
Managed Identity: "Azure automatically gives Databricks a credential that it manages"
```

**When to use each:**
- Managed Identity → Databricks workspace on dedicated VMs, Azure Functions, VMs
- Service Principal → Databricks Serverless, external tools, cross-cloud scenarios

For this project, we used Service Principal because the Serverless DLT compute doesn't support Managed Identity directly.

---

**Q11: What is the difference between Azure Databricks Premium and Standard SKU?**

A:

| Feature | Standard | Premium |
|---------|----------|---------|
| Delta Live Tables | No | Yes |
| Table Access Control | No | Yes |
| Row/Column Level Security | No | Yes |
| Audit Logs | No | Yes |
| Key Vault Secret Scopes | No | Yes |
| Single Sign-On (SSO) | No | Yes |
| IP Access Lists | No | Yes |
| Price | ~$0.20/DBU | ~$0.27/DBU |

For any production workload handling sensitive data (healthcare, finance), Premium is required.

---

### Round 4: Data Quality & Pipeline Design

**Q12: What are the different DLT expectation types and when do you use each?**

A:
```python
# 1. expect — warn only, keep all records
@dlt.expect("valid_postcode", "LENGTH(postcode) = 4")
# Use: non-critical quality checks, monitoring

# 2. expect_or_drop — drop invalid records
@dlt.expect_or_drop("valid_gender", "gender IN ('M', 'F')")
# Use: filter out bad records, continue processing good ones
# Dropped records counted in pipeline metrics

# 3. expect_or_fail — halt entire pipeline
@dlt.expect_or_fail("no_null_patient_id", "patient_id IS NOT NULL")
# Use: critical data — better to stop than process corrupt data
```

**Decision framework:**
- Patient ID null? → `expect_or_fail` (cannot process without it)
- Invalid gender value? → `expect_or_drop` (skip, process rest)
- Optional field missing? → `expect` (warn, keep record)

---

**Q13: How would you handle schema evolution in Delta Lake?**

A: Delta Lake supports several schema evolution strategies:

```python
# 1. Strict (default) — reject new columns
df.write.format("delta").save(path)  # Fails if new column added

# 2. mergeSchema — add new columns, keep old ones
df.write.format("delta") \
  .option("mergeSchema", "true") \
  .save(path)

# 3. overwriteSchema — replace entire schema
df.write.format("delta") \
  .option("overwriteSchema", "true") \
  .mode("overwrite") \
  .save(path)
```

**Healthcare scenario:**
Source adds new field `blood_type`. With `mergeSchema=true`:
- Existing records: `blood_type = null`
- New records: `blood_type = "A+"`
- No pipeline failure, backward compatible

---

**Q14: What is the difference between batch and streaming in Spark? What is Structured Streaming?**

A:
- **Batch:** Process a fixed dataset completely. Start, finish, done. (What we built with DLT)
- **Streaming:** Process continuous data as it arrives. Never "done". (Event Hubs use case)

**Structured Streaming** is Spark's streaming engine built on DataFrames — you write nearly identical code for batch and stream:

```python
# Batch
df = spark.read.format("delta").load(path)

# Streaming (same API, different read)
df = spark.readStream.format("cloudFiles") \
  .option("cloudFiles.format", "json") \
  .load(landing_zone)

# Both use same transformations
cleaned = df.withColumn("upper_gender", upper(col("gender")))

# Batch output
cleaned.write.format("delta").save(output_path)

# Streaming output
cleaned.writeStream.format("delta") \
  .option("checkpointLocation", checkpoint_path) \
  .start(output_path)
```

**Trigger modes for streaming:**
- `processingTime="1 minute"` — micro-batch every minute
- `once=True` — process all available data then stop (like batch)
- `availableNow=True` — same as once, but respects rate limits
- `continuous="1 second"` — near real-time (experimental)

---

### Round 5: Healthcare Domain & Compliance

**Q15: What is PHI and PII? What's the difference?**

A:
- **PII (Personally Identifiable Information):** Any data that can identify a person. Name, email, phone, IP address, passport number.
- **PHI (Protected Health Information):** PII specifically related to health. Medical records, diagnoses, prescriptions, Medicare numbers, appointment dates.

In healthcare data engineering, PHI is the highest sensitivity — regulated by both Privacy Act and My Health Records Act in Australia.

**De-identification techniques used:**

| Technique | How | Use case |
|-----------|-----|----------|
| **Hashing (used)** | SHA-256(patient_id) | Preserve linkability without exposing ID |
| Masking | Replace with `***` | Display only, cannot query |
| Tokenisation | Replace with random token, store mapping | Reversible, secure |
| Generalisation | 1985-03-15 → 1985 | Reduce precision, keep analytics value |
| Suppression | Delete field entirely | When field not needed |
| Synthetic data | Generate fake but realistic data | Testing/development |

---

**Q16: What is data residency and why does it matter for Australian healthcare?**

A: Data residency means data physically stays within a geographic boundary.

**Australian requirements:**
- My Health Records data must stay in Australia
- Some health departments require Australia-only processing
- Patients have a right to know where their data is stored

**Implementation in this project:**
- All Azure resources deployed to `Australia East` (Sydney)
- Data never leaves Australia East region
- No geo-redundancy to international regions configured

**Azure regions in Australia:**
- Australia East (Sydney) — primary
- Australia Southeast (Melbourne) — disaster recovery

For production, set up geo-redundancy between Sydney and Melbourne only.

---

### Round 6: System Design

**Q17: Design a real-time patient vitals monitoring system on Azure Databricks.**

A:

```
IoT Devices (vitals monitors)
         │
         ▼
Azure Event Hubs (kafka-compatible)
         │
         ▼
Databricks Structured Streaming
  - Parse JSON vitals
  - Apply anomaly detection
  - Alert if heart rate > 150 or < 40
         │
    ┌────┴────┐
    ▼         ▼
Bronze       Alerts
Delta        Azure
Table        Service Bus
             │
             ▼
         Nursing
         Station
         App
```

**Code pattern:**
```python
# Read from Event Hubs
df = spark.readStream \
  .format("eventhubs") \
  .options(**eventhubs_conf) \
  .load()

# Parse vitals
vitals = df.select(
    from_json(col("body").cast("string"), schema).alias("data")
).select("data.*")

# Alert on anomalies
alerts = vitals.filter(
    (col("heart_rate") > 150) | (col("heart_rate") < 40)
)

# Write alerts to Delta (for audit)
alerts.writeStream \
  .format("delta") \
  .outputMode("append") \
  .option("checkpointLocation", "/checkpoints/alerts") \
  .start("/data/gold/alerts")
```

---

**Q18: How would you handle late-arriving data in a streaming pipeline?**

A: Late data is a common real-world problem — network delays, offline devices, batched uploads.

**Watermarking in Structured Streaming:**
```python
# Allow data up to 2 hours late
vitals_with_watermark = vitals \
  .withWatermark("event_time", "2 hours")

# Window aggregation respects watermark
vitals_with_watermark \
  .groupBy(
    window(col("event_time"), "10 minutes"),
    col("patient_id_hash")
  ) \
  .agg(avg("heart_rate").alias("avg_heart_rate"))
```

How watermarking works:
- System tracks max event_time seen
- `max_event_time - 2 hours` = watermark threshold
- Records with event_time < threshold are dropped
- State is cleaned up for windows older than threshold

**For batch (DLT):**
```python
# Merge new data including late arrivals
@dlt.table
def silver_vitals():
    return spark.readStream.format("cloudFiles") \
      .option("cloudFiles.format", "json") \
      .load(landing_path) \
      .withColumn("arrival_time", current_timestamp())
# DLT handles incremental processing automatically
```

---

**Q19: How would you optimise a slow Delta Lake query?**

A: Step-by-step debugging approach:

```python
# 1. Check query plan
df.explain(extended=True)

# 2. Check table stats
spark.sql("DESCRIBE DETAIL delta.`/path/to/table`")
# Look at: numFiles, sizeInBytes

# 3. Run ANALYZE to collect stats
spark.sql("ANALYZE TABLE patients COMPUTE STATISTICS FOR ALL COLUMNS")

# 4. Optimize the table (compact small files)
spark.sql("OPTIMIZE patients")

# 5. Z-order on filter columns
spark.sql("OPTIMIZE patients ZORDER BY (postcode, date_of_birth)")

# 6. Check for data skew
df.groupBy(spark_partition_id()).count().show()

# 7. Use broadcast join for small dimension tables
result = large_df.join(broadcast(small_df), "postcode")

# 8. Tune shuffle partitions
spark.conf.set("spark.sql.shuffle.partitions", "200")  # Default is 200
# For small data, reduce this:
spark.conf.set("spark.sql.shuffle.partitions", "8")
```

---

**Q20: What would you do differently if this was a production system with 1TB/day?**

A:

| Area | Development (current) | Production |
|------|----------------------|------------|
| **Cluster** | Single node, D4ds_v5 | Multi-node autoscaling, Spot VMs for workers |
| **Storage** | No partitioning | Partition by ingested_at year/month |
| **Pipeline** | Triggered manually | Scheduled jobs via Databricks Workflows |
| **Data quality** | Basic DLT expectations | Great Expectations or dbt tests |
| **Monitoring** | Manual | Azure Monitor + Databricks alerts |
| **CI/CD** | Manual deployment | GitHub Actions → Databricks CLI |
| **Unity Catalog** | Hive metastore | Unity Catalog for fine-grained governance |
| **Disaster recovery** | None | Geo-redundant storage (Sydney + Melbourne) |
| **Cost** | Free trial | Reserved instances + Spot VMs (60% saving) |
| **Security** | Basic RBAC | Network isolation (VNet injection) |

**Estimated production architecture cost (Australia East, 1TB/day):**
- ADLS Gen2: ~$20/month (storage) + ~$5/month (transactions)
- Databricks: ~$500/month (DLT + SQL Warehouse + interactive)
- Event Hubs: ~$50/month (Standard tier)
- Key Vault: ~$5/month
- **Total: ~$580/month** for a medium data team

---

## Glossary of Key Terms

| Term | Definition |
|------|-----------|
| DBU | Databricks Unit — billing unit for Databricks compute |
| ADLS Gen2 | Azure Data Lake Storage Generation 2 |
| ABFS | Azure Blob File System — protocol for accessing ADLS Gen2 |
| DLT | Delta Live Tables — Databricks declarative pipeline framework |
| PHI | Protected Health Information |
| PII | Personally Identifiable Information |
| ACID | Atomicity, Consistency, Isolation, Durability |
| RBAC | Role-Based Access Control |
| OAuth | Open Authorization — token-based authentication protocol |
| Service Principal | Azure identity for automated services (like a service account) |
| Managed Identity | Azure-managed service principal (no credential management) |
| Medallion | Bronze/Silver/Gold layered data architecture |
| Z-ordering | Delta Lake file layout optimisation for multi-column queries |
| Watermarking | Structured Streaming mechanism to handle late-arriving data |
| Shuffle | Spark operation requiring data redistribution across partitions |
| Broadcast Join | Spark optimisation for joining large table with small table |
| Unity Catalog | Databricks centralised data governance (requires org account) |
| Hive Metastore | Default Databricks metadata store (per-workspace) |
| PAT | Personal Access Token — Databricks authentication credential |
| CDC | Change Data Capture — tracking row-level changes in source systems |
