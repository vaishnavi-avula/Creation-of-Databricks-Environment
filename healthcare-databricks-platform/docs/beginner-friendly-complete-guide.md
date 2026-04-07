# Healthcare Data Platform on Azure Databricks
## Complete Beginner's Guide — Every Step Explained Simply

**Who is this for?** Someone who has never used Azure or Databricks before and wants to understand WHAT they built, WHY each decision was made, and HOW to explain it in job interviews.

---

## PART 1: UNDERSTANDING WHAT WE BUILT

### The Big Picture — What Problem Are We Solving?

Imagine you work at a healthcare startup in Australia. Doctors use a clinic software (ERP) that stores patient records — names, Medicare numbers, birth dates, medical history.

Your company needs to:
1. **Analyse patterns** — How many patients in Sydney vs Melbourne? What age groups visit most?
2. **Build dashboards** — Show doctors and managers useful charts and reports
3. **Stay legal** — Australian Privacy Act says you CANNOT share patient names and Medicare numbers with analysts

**The problem:** Raw patient data has sensitive information (names, Medicare numbers). But analysts need the data to do their job. How do you give analysts useful data WITHOUT exposing private patient information?

**Our solution:** Build a pipeline that:
- Takes in raw patient data (with names, Medicare numbers)
- Automatically removes sensitive information
- Produces clean, safe data for analysts

This is what we built. Let's understand each piece.

---

### Real-World Analogy for the Whole System

Think of it like a **hospital records department**:

```
📋 Doctor's notes (raw data with patient names)
        ↓
🔒 Medical records room (Bronze layer - locked, original files)
        ↓
✂️  Anonymisation desk (Silver layer - names removed, ID numbers replaced)
        ↓
📊 Statistics office (Gold layer - just numbers, no patient details)
        ↓
💻 Manager's dashboard (Power BI - charts and graphs)
```

The doctor's notes never leave the locked room. Analysts only ever see the statistics — no patient names, no Medicare numbers.

---

## PART 2: MICROSOFT AZURE — THE CLOUD PLATFORM

### What is Cloud Computing?

**Old way:** Companies bought physical servers, put them in a room, hired people to maintain them. Cost: $100,000+ upfront.

**Cloud way:** Microsoft owns millions of servers in big data centres around the world. You "rent" computing power, storage, and services from them. You pay only for what you use, like paying for electricity — you don't buy a power plant, you just pay your monthly bill.

**Azure** is Microsoft's cloud platform. Think of it as a giant supermarket of computing services — storage, databases, security tools, AI services — all available on demand.

### Why Azure for Healthcare in Australia?

1. **Australian data centres** — Azure has data centres in Sydney (Australia East). Australian Privacy Act requires patient data to stay in Australia. Azure lets us ensure that.
2. **Healthcare compliance** — Azure is certified for healthcare workloads (HIPAA, ISO 27001)
3. **Free trial** — $200 free credit to learn and experiment
4. **Databricks partnership** — Azure has the best Databricks integration

---

## PART 3: AZURE RESOURCES WE CREATED

### 3.1 Resource Group: `rg-healthstartup-prod`

**What is it?**
A folder for all your Azure resources. When you create storage, databases, and services in Azure, they need to live somewhere. A Resource Group is that "somewhere" — it groups related things together.

**Real-world analogy:** Like a physical filing cabinet drawer labelled "Health Startup Project" — everything for this project goes in this drawer.

**Why we created one:**
- Easy to find all project resources in one place
- Delete everything at once when done (delete the resource group = delete everything inside it)
- See the total cost for this project specifically
- Apply security rules to everything at once

**What we named it:** `rg-healthstartup-prod`
- `rg` = resource group (standard abbreviation)
- `healthstartup` = our project
- `prod` = production environment

**Alternative approaches:**
- Multiple resource groups (one for storage, one for compute) — used by large teams
- We used one because it's a small project and easier to manage

---

### 3.2 Azure Data Lake Storage Gen2 (ADLS Gen2): `adlshealthstartupprod`

**What is it?**
Cloud storage — like a massive hard drive in the cloud where we store our data files. "Gen2" means the second generation, which added features specifically for big data analytics.

**Real-world analogy:** Like a filing cabinet with infinite drawers, accessible from anywhere in the world, with no risk of losing files.

**Why not just use a normal database (like SQL Server)?**

| Option | Good for | Bad for |
|--------|----------|---------|
| SQL Server | Small structured data, fast queries | Very expensive at large scale, can't store files |
| ADLS Gen2 (our choice) | Large files, big data, Spark | Not good for single-record lookups |
| Hard drive on laptop | Personal files | Everyone else can't access it, no backup |

For analytics on 100GB-1TB/day of patient records, cloud storage like ADLS Gen2 is the right choice.

**The 4 containers we created:**

Think of containers like folders:

```
adlshealthstartupprod (the big filing cabinet)
├── bronze/     📂 Raw patient records — LOCKED, only engineers can access
├── silver/     📂 Cleaned records, PHI removed — engineers and scientists
├── gold/       📂 Statistics only — analysts and managers can access
└── ml/         📂 Machine learning training data — data scientists only
```

**Why separate containers?**
Different people should see different things. A business analyst should never be able to open the bronze folder and see real patient names. Separate containers = separate security rules.

**The path format (ABFS):**
```
abfss://bronze@adlshealthstartupprod.dfs.core.windows.net/patients
```
Breaking this down:
- `abfss://` = Azure Blob File System Secure (the `s` at the end means encrypted/SSL)
- `bronze` = which container
- `adlshealthstartupprod` = storage account name
- `.dfs.core.windows.net` = Azure's domain for data lake storage
- `/patients` = the folder inside the container

**Why `abfss` and not `abfs`?** Always use the double-s version. It encrypts data in transit. For healthcare data, unencrypted transfer is illegal.

---

### 3.3 Azure Key Vault: `kv-healthstartup-prod`

**What is it?**
A secure digital safe in the cloud where you store passwords, API keys, and connection strings. Only people (and services) you explicitly authorise can read these secrets.

**Real-world analogy:** Like a bank vault for passwords. You don't carry all your valuables in your pocket — you put them in a vault and only take out what you need, when you need it.

**Why not just put passwords in the code?**

Bad example (NEVER do this):
```python
# WRONG! This password is now visible to everyone who reads the code
# If you save this to GitHub, your storage account is hacked
spark.conf.set("fs.azure.account.key.mystorage.dfs.core.windows.net",
               "ABC123secretpassword!")
```

Good example (what we do):
```python
# CORRECT! The actual password never appears in code
# Databricks fetches it from Key Vault securely
spark.conf.set("fs.azure.account.key.mystorage.dfs.core.windows.net",
               dbutils.secrets.get(scope="kv-healthstartup", key="adls-storage-key"))
```

**The 5 secrets we stored:**

| Secret Name | What it contains | Why we need it |
|-------------|-----------------|----------------|
| `adls-storage-key` | Password to access our storage account | So Databricks can read/write files |
| `sp-client-id` | Username of our service account | For OAuth login |
| `sp-client-secret` | Password of our service account | For OAuth login |
| `tenant-id` | Our Azure organisation's unique ID | For OAuth login |
| `eventhub-connection-string` | Connection string for Event Hubs | For streaming data |

**Access mode we chose: RBAC (Role-Based Access Control)**
This means we control WHO can do WHAT using "roles" rather than individual permission lists. Like giving someone a "Manager" badge that automatically gives them access to certain rooms, rather than giving them keys to individual doors.

**Two roles we assigned:**
1. Our user account → `Key Vault Secrets Officer` — can read AND write secrets
2. AzureDatabricks application → `Key Vault Secrets User` — can only READ secrets (not create or delete)

**Why give AzureDatabricks read-only?** Principle of least privilege — only give access to what's needed. Databricks needs to read secrets, not create them.

---

### 3.4 App Registration (Service Principal): `databricks-storage-sp`

**What is it?**
An identity (account) for an application — in this case, for our Databricks pipelines. Instead of using a human's login, we create a dedicated "service account" with its own username and password.

**Real-world analogy:** Like creating a separate staff ID card for the cleaning robot. The robot needs to enter the building at night, but you don't give it the CEO's personal keycard. You give it its own keycard with access only to the areas it needs.

**Why not use a human account for this?**

| Human Account | Service Principal |
|---------------|------------------|
| Password expires, needs changing | Long-lived, managed credentials |
| Requires MFA (multi-factor auth) | No MFA — automated pipelines can't do MFA |
| Tied to one person — leaves company | Exists independently of any person |
| Hard to audit what the pipeline did | All actions logged under service identity |

**OAuth 2.0 — How authentication works:**

```
1. DLT Pipeline says: "I need to access storage"
2. Databricks goes to Key Vault: "Give me the service principal credentials"
3. Key Vault returns: client_id + client_secret
4. Databricks sends these to Azure Active Directory: "Please give me a token"
5. Azure AD returns: a temporary access token (valid for 1 hour)
6. Databricks uses this token to access storage
7. Token expires after 1 hour → automatically refreshed
```

This is called OAuth 2.0 — an industry-standard security protocol used by Google, Facebook, and every major tech company.

---

## PART 4: AZURE DATABRICKS

### What is Databricks?

Databricks is a data platform built on top of **Apache Spark** — a powerful distributed computing engine that can process massive amounts of data across many computers simultaneously.

**Real-world analogy:** Apache Spark is like a large construction crew — you can split a big building project into small tasks and give each worker a different task. Databricks is the project management office that organises the crew, provides tools, and tracks progress.

**What Databricks gives us on top of Spark:**
- Notebooks (like Jupyter notebooks) for writing Python/SQL code
- Managed clusters (no need to set up servers yourself)
- Delta Live Tables for pipelines
- MLflow for machine learning
- Unity Catalog for data governance
- SQL Warehouse for BI tools

### 4.1 Databricks Workspace: `adb-healthstartup-prod`

**SKU (pricing tier) we chose: Premium**

| Feature | Standard | Premium (our choice) |
|---------|----------|---------------------|
| Delta Live Tables (DLT) | ❌ No | ✅ Yes |
| Who can see which table | ❌ No | ✅ Yes |
| Audit logs (who accessed what) | ❌ No | ✅ Yes |
| Key Vault secret scopes | ❌ No | ✅ Yes |
| Cost | Cheaper | ~35% more |

For healthcare — where we need access controls and audit logs — Premium is not optional.

---

### 4.2 The Cluster: `etl-job-cluster`

**What is a cluster?**
A cluster is a set of computers (virtual machines) that Spark uses to process data. You can have 1 computer (single node) or hundreds of computers working together.

**Real-world analogy:** Like hiring workers for a job. For a small job, you hire one person (single node). For a huge job, you hire hundreds (multi-node cluster).

**Settings we chose:**

| Setting | Value | Why |
|---------|-------|-----|
| Runtime | 14.3 LTS ML | LTS = Long Term Support. Like choosing Windows 10 over a beta version — stable and supported for years |
| Node type | Standard_D4ds_v5 | 4 CPU cores, 16GB RAM — enough for our data volume |
| Mode | Single Node | We have small data (2 rows in testing). No need to pay for multiple computers |
| Auto-terminate | 20 minutes | If you forget to turn it off, it auto-shuts after 20 min idle. Saves money! |

**Databricks Runtime versions explained:**
- **LTS (Long Term Support)** — Stable, production-ready, security patches for 2+ years. Always use this for real work.
- **ML** — Includes machine learning libraries (TensorFlow, PyTorch, MLflow) pre-installed
- **Photon** — Uses a faster C++ engine for SQL queries (2-3x speedup). Use for analytics workloads.
- **GPU** — Has NVIDIA graphics card drivers. Use for deep learning and AI model training.

---

### 4.3 Databricks CLI (Command Line Interface)

**What is it?**
Instead of clicking through the Databricks website, you can type commands in a terminal. Like the difference between using Windows Explorer to navigate files vs typing `cd Documents` in Command Prompt.

**Why use CLI?**
- Faster for experienced users
- Can be automated in scripts
- Used in CI/CD pipelines for deploying code

**Configuration file we created:** `~/.databrickscfg`
```ini
[DEFAULT]
host = https://adb-7405607057216468.8.azuredatabricks.net
token = your-personal-access-token
```
This tells the CLI which Databricks workspace to connect to and how to authenticate.

**Personal Access Token (PAT):**
Like a password for the API. Instead of username/password, you generate a token — a long string like `dapi123abc456def...` — and use that to authenticate.

---

### 4.4 Databricks Secret Scope: `kv-healthstartup`

**What is it?**
A named group of secrets that Databricks can access. We connected it to our Azure Key Vault, so when notebooks ask for a secret, Databricks fetches it from Key Vault automatically.

**How it works in a notebook:**
```python
# This line fetches the storage key from Key Vault
# The actual key value is never shown in the notebook output
storage_key = dbutils.secrets.get(scope="kv-healthstartup", key="adls-storage-key")
```

**Why Key Vault-backed scope instead of Databricks-native secrets?**

| Databricks Native Secrets | Azure Key Vault Backed (our choice) |
|--------------------------|-------------------------------------|
| Stored on Databricks servers | Stored in Azure Key Vault (more secure) |
| Basic audit trail | Full Azure Monitor audit log |
| Manual rotation | Supports automatic rotation |
| Only Databricks can use it | Also usable by other Azure services |

---

## PART 5: DELTA LAKE & MEDALLION ARCHITECTURE

### What is Delta Lake?

Delta Lake is a way of storing data files that adds powerful features like transactions, version history, and data quality enforcement.

**Before Delta Lake (plain Parquet files):**
```
Problem: Two pipelines writing at same time → Corrupted data
Problem: Pipeline fails halfway → Partial data written, table broken
Problem: Need yesterday's data → Impossible, only today's version exists
```

**With Delta Lake:**
```
Solution: ACID transactions — either fully written or not at all
Solution: Transaction log — can roll back to previous state
Solution: Time travel — query any historical version
```

**What does a Delta table look like on disk?**
```
patients/
├── _delta_log/                           ← The "transaction log" (like a bank statement)
│   ├── 00000000000000000000.json         ← "Table created on March 29"
│   ├── 00000000000000000001.json         ← "2 rows added"
│   └── 00000000000000000002.json         ← "1 row updated"
├── part-00000-abc123.parquet             ← Actual data file
└── part-00001-def456.parquet             ← Another data file
```

The Parquet files contain the actual data. The `_delta_log` files record every change ever made, like a bank transaction history.

**ACID explained simply:**

| Letter | Stands for | Simple explanation |
|--------|-----------|-------------------|
| A | Atomicity | "All or nothing" — a transaction either fully succeeds or fully fails. No half-written data. |
| C | Consistency | Data always follows the rules. If patient_id must be unique, Delta enforces that. |
| I | Isolation | Multiple people can read/write at the same time without corrupting each other's work. |
| D | Durability | Once saved, it stays saved. Even if the server crashes. |

**Time Travel — querying historical data:**
```python
# What did the patient table look like yesterday?
df = spark.read.format("delta") \
    .option("timestampAsOf", "2026-03-29") \
    .load("abfss://bronze@adlshealthstartupprod.dfs.core.windows.net/patients")

# What did it look like at version 0 (when first created)?
df = spark.read.format("delta") \
    .option("versionAsOf", 0) \
    .load("abfss://bronze@adlshealthstartupprod.dfs.core.windows.net/patients")
```

Real-world use case: "We processed data incorrectly last Tuesday. Can we reprocess from the original?" — Yes, with time travel!

---

### The Medallion Architecture: Bronze → Silver → Gold

**What is it?**
A way of organising data into three layers, each more refined and safer than the previous.

**Why "Medallion"?** Like Olympic medals — Bronze (raw, basic), Silver (refined, cleaned), Gold (the best, most valuable for decisions).

---

#### BRONZE LAYER — The Raw Data Store

**Purpose:** Store data exactly as it arrived from the source. No changes, no cleaning, no deletions.

**Think of it as:** The loading dock of a warehouse. Everything that comes in gets logged exactly as received.

**What's in our bronze patient table:**
```
patient_id    | given_name | family_name | date_of_birth | gender | medicare_number | postcode
P001          | Jane       | Smith       | 1985-03-15    | F      | 123456789       | 2000
P002          | John       | Doe         | 1962-07-22    | M      | 987654321       | 3000
```

**Why keep raw data?**
- If we make a mistake in Silver/Gold processing, we can reprocess from Bronze
- Audit trail — proves what data we received and when
- Legal requirement — some regulations require keeping original records

**Who can access Bronze?** Only data engineers. Never analysts.

---

#### SILVER LAYER — The Cleaned, Safe Data

**Purpose:** Remove all personally identifiable information (PHI). Clean and standardise the data.

**Think of it as:** The anonymisation team. They take the original records, remove the sensitive parts, and produce safe copies.

**What we do in Silver:**

1. **Hash the patient ID** (SHA-256):
   ```
   P001 → df1e40051eff4bcf9b4ebc93083bfcad7f5195746b3e657de6b72bf3cb8897c3
   ```
   Why hash instead of delete? We need to be able to link the same patient across different datasets (e.g., appointments + prescriptions) without knowing who they are. The hash lets us say "these two records are the same patient" without knowing the patient's actual ID.

   SHA-256 is a one-way function — you CANNOT go backwards from the hash to get "P001". It's like putting a letter in a shredder — you can't un-shred it.

2. **Delete sensitive fields completely:**
   - `given_name` → DELETED
   - `family_name` → DELETED
   - `medicare_number` → DELETED
   - `patient_id` → DELETED (replaced by hash above)

3. **Standardise remaining data:**
   - `gender` → convert to uppercase and remove spaces: `" f "` → `"F"`
   - `postcode` → remove leading/trailing spaces

4. **Add metadata:**
   - `silver_processed_at` → timestamp when this pipeline ran
   - `data_quality` → `"OK"` or `"INCOMPLETE"` based on missing fields

**What Silver looks like after transformation:**
```
patient_id_hash                                                   | date_of_birth | gender | postcode | data_quality
df1e40051eff4bcf9b4ebc93083bfcad7f5195746b3e657de6b72bf3cb8897c3 | 1985-03-15    | F      | 2000     | OK
eea502719605f8ec96582d94a0f1738190fe72d16c7b57de48fcfcebfbcb631a | 1962-07-22    | M      | 3000     | OK
```

**Who can access Silver?** Data engineers and data scientists.

---

#### GOLD LAYER — The Analytics-Ready Data

**Purpose:** Pre-aggregated tables for dashboards and reports. Zero individual records — only counts and summaries.

**Think of it as:** The statistics office. They only produce reports like "Number of patients by area" — never individual patient files.

**gold_patients_by_postcode:**
```
postcode | patient_count | female_count | male_count
2000     | 1             | 1            | 0
3000     | 1             | 0            | 1
```
This table has ZERO personally identifiable information. You cannot determine who any individual patient is from this data.

**gold_data_quality_summary:**
```
data_quality | source_system | record_count
OK           | clinic-erp    | 2
```
This tells data engineers: all records from the clinic ERP system passed quality checks.

**Who can access Gold?** Everyone — analysts, managers, Power BI dashboards.

---

## PART 6: DELTA LIVE TABLES (DLT)

### What is DLT?

Delta Live Tables is Databricks' way of building data pipelines. Instead of writing complex code to manage the order of operations, you simply declare what each table should look like, and DLT figures out the rest.

**Real-world analogy:** Like a cooking recipe vs ordering at a restaurant.

- **Traditional ETL (old way):** You write every step: "First boil water, then add pasta, then drain, then add sauce, then serve." You manage every detail.
- **DLT (our way):** You say "I want spaghetti bolognese." The kitchen figures out all the steps and the order.

**The `@dlt.table` decorator:**
```python
@dlt.table(name="silver_patients")
def silver_patients():
    bronze = dlt.read("bronze_patients")  # "I need bronze_patients as input"
    # ... transformations ...
    return result
```

DLT automatically:
- Runs `bronze_patients` before `silver_patients` (dependency management)
- Retries if there's a failure
- Tracks lineage (which tables depend on which)
- Monitors data quality metrics
- Updates the pipeline graph visualization

**DLT vs Traditional Spark ETL:**

| Aspect | Traditional Spark | Delta Live Tables |
|--------|------------------|-----------------|
| Dependency order | You manage manually | DLT figures out automatically |
| Retry on failure | You code it | Built-in |
| Data quality checks | You code it | `@dlt.expect` decorators |
| Pipeline visualisation | None | Automatic graph |
| Lineage tracking | None | Automatic |
| Code volume | ~300 lines | ~60 lines |

---

### DLT Compute: Serverless vs Classic

**The problem we hit:** When we tried Classic compute (regular VMs), Azure Australia East had no capacity (stockout). All D-family VMs were unavailable.

**Solution: Serverless compute**
- Databricks manages the infrastructure — we don't pick VMs
- No stockout issues (Databricks has reserved capacity)
- Starts faster (~30 seconds vs 5 minutes)
- Scales automatically

**The trade-off:** Serverless DLT blocks storage account keys for security reasons. We had to use OAuth (service principal) instead.

---

### Storage Authentication for Serverless DLT

**Why OAuth instead of storage key?**

Storage key = like giving someone the master key to your house. Anyone with the key has full access, forever.

OAuth = like a time-limited visitor pass. Valid for 1 hour, can be revoked, logs every entry.

**The 5 configuration lines we added to the DLT pipeline:**
```
fs.azure.account.auth.type... = OAuth
fs.azure.account.oauth.provider.type... = ClientCredsTokenProvider
fs.azure.account.oauth2.client.id... = {{secrets/kv-healthstartup/sp-client-id}}
fs.azure.account.oauth2.client.secret... = {{secrets/kv-healthstartup/sp-client-secret}}
fs.azure.account.oauth2.client.endpoint... = https://login.microsoftonline.com/<tenant-id>/oauth2/token
```

**Why `{{secrets/...}}` syntax?** This tells Databricks to fetch the value from Key Vault at runtime. The actual secret value never appears in the configuration.

---

### DLT Expectations (Data Quality Rules)

**What are they?**
Rules that check if data meets quality standards.

```python
# Drop any row where gender is not M or F
@dlt.expect_or_drop("valid_gender", "gender IN ('M', 'F')")

# Warn (but keep the row) if postcode is missing
@dlt.expect("has_postcode", "postcode IS NOT NULL")

# Stop the entire pipeline if patient_id is null (critical error)
@dlt.expect_or_fail("patient_id_required", "patient_id IS NOT NULL")
```

**Three types:**

| Type | What happens with bad records | Use when |
|------|------------------------------|----------|
| `@dlt.expect` | Keep the record, just log a warning | Non-critical quality issue |
| `@dlt.expect_or_drop` | Delete the bad record, continue | You want clean data but don't want to stop |
| `@dlt.expect_or_fail` | Stop the entire pipeline | Bad data means ALL data is suspect |

**Important lesson we learned:** Expectations run on the FINAL output of the function (after all transformations). If you drop `patient_id` inside the function and then write `@dlt.expect_or_drop("...", "patient_id IS NOT NULL")` — it will fail because `patient_id` no longer exists in the output. Solution: use `patient_id_hash IS NOT NULL` instead.

---

## PART 7: SQL WAREHOUSE & POWER BI

### What is a SQL Warehouse?

A SQL Warehouse is a computing cluster specifically designed for SQL queries from BI tools like Power BI.

**Real-world analogy:** Like a specialist helpdesk for SQL questions. Your notebook cluster handles Python code. The SQL Warehouse handles queries from Power BI and business analysts who only know SQL.

**SQL Warehouse vs Regular Cluster:**

| Feature | Regular Cluster | SQL Warehouse |
|---------|----------------|--------------|
| Languages | Python, SQL, R, Scala | SQL only |
| Users | Data engineers, scientists | Analysts, BI tools |
| Start time | 3-5 minutes | ~15 seconds (Serverless) |
| Best for | Building pipelines | Running dashboard queries |

**Settings we chose:**
- Size: `2X-Small` — the smallest and cheapest (2 DBUs). Fine for small data.
- Auto-stop: `10 minutes` — turns off if no queries for 10 minutes, saves money.
- Type: `Serverless` — starts fast, no VM management.

---

### Power BI Connection

**What is Power BI?**
Microsoft's business intelligence tool. Drag-and-drop interface for creating charts, graphs, and dashboards from data.

**How we connected it:**
1. In Power BI: Get Data → Azure Databricks
2. Entered the connection details:
   - **Server hostname:** `adb-7405607057216468.8.azuredatabricks.net` (our Databricks workspace URL)
   - **HTTP path:** `/sql/1.0/warehouses/32798e2fd869fa6c` (which SQL Warehouse to use)
3. Authenticated with a Personal Access Token
4. Selected the Gold tables (`gold_patients_by_postcode`, `gold_data_quality_summary`)

**What we built in Power BI:**
- **Bar chart:** Patient count by postcode
- **Pie chart:** Gender breakdown
- **Card visual:** Total records processed

**Important:** Power BI only connects to the Gold layer. Analysts using Power BI can never accidentally access Silver or Bronze data with patient names.

---

## PART 8: SECURITY & AUSTRALIAN PRIVACY ACT

### Australian Privacy Act 1988

**What is it?**
Australia's main privacy law. It says companies must protect personal information — how it's collected, stored, used, and disposed of.

**Key principles that affect our platform:**

| Principle | What it means | How we comply |
|-----------|--------------|---------------|
| APP 3: Collection | Only collect what you need | Silver layer removes fields not needed for analytics |
| APP 6: Use/Disclosure | Only use data for the purpose it was collected | Gold layer only allows analytics, not re-identification |
| APP 11: Security | Protect personal information from misuse | Key Vault, RBAC, encrypted storage |
| APP 12: Access | Individuals can request their data | Delta time travel allows us to find specific records if needed |

**My Health Records Act 2012:**
Specifically covers electronic health records in Australia. Key requirements:
- Data must stay in Australia (we use Australia East region — Sydney)
- Strict access controls on who can see medical information
- Criminal penalties (up to 2 years prison) for unauthorised access

### What We Implemented

**1. PHI Removal at Silver Layer**

PHI (Protected Health Information) removed:
- ✅ `given_name` → deleted
- ✅ `family_name` → deleted
- ✅ `medicare_number` → deleted
- ✅ `patient_id` → replaced with SHA-256 hash (irreversible)

PHI retained with justification:
- `date_of_birth` → needed for age-group health analytics
- `gender` → needed for gender health disparity research
- `postcode` → needed for geographic health analysis

**2. Data Residency in Australia**

All resources in `Australia East` (Sydney data centre). Data never leaves Australia.

**3. Table-Level Permissions**

```
Silver table: Only data engineers can SELECT
Gold tables:  Analysts + engineers can SELECT
Bronze table: Only data engineers can SELECT
```

Configured via Databricks table permissions (Data → table → Permissions → Grant).

**4. Secret Management**

All credentials stored in Azure Key Vault — never in code, notebooks, or configuration files.

**5. Store Results in Customer Account**

Setting enabled: "Store interactive notebook results in customer account"

What this means: When you run a notebook, the results (output data) are stored in YOUR Azure storage (ADLS Gen2), not on Databricks' servers. Important for healthcare — patient data should never sit on a vendor's infrastructure.

---

## PART 9: AZURE EVENT HUBS (STREAMING)

### What is Event Hubs?

Azure Event Hubs is a message queue service for real-time data. Think of it like a post office that receives millions of letters (events) per second and holds them until someone is ready to read them.

**Real-world analogy:** Like a conveyor belt at an airport luggage carousel. Bags (events) come in continuously. You grab them as they come past. If you're not there for a while, the bags queue up.

**What we created:**
- **Namespace:** `evhns-healthstartup-prod` — the post office building
- **Event Hub:** `patient-events` — one specific mailbox for patient-related events

**How it would work in production:**
```
Hospital IoT devices → send patient vitals every second
        ↓
Event Hubs (patient-events) — buffers the stream
        ↓
Databricks Structured Streaming — reads and processes in real-time
        ↓
Bronze Delta table — persists the streaming data
```

**Why we set it up but didn't connect it:**
Azure free trial VM stockout issues affected the Classic compute needed for testing streaming. The infrastructure is ready for when you upgrade from the free trial.

---

## PART 10: WHAT WE BUILT — COMPLETE SUMMARY

### The Data Journey

```
Step 1: Raw data arrives
──────────────────────
clinic-erp exports patient records:
patient_id=P001, given_name=Jane, family_name=Smith,
date_of_birth=1985-03-15, gender=F, medicare_number=123456789

Step 2: Bronze layer ingestion (Notebook 01)
────────────────────────────────────────────
Write exact copy to Delta table. No changes.
Location: abfss://bronze@adlshealthstartupprod.dfs.core.windows.net/patients

Step 3: DLT Pipeline runs
──────────────────────────
Bronze table → silver_patients function runs:
  - SHA-256 hash patient_id → patient_id_hash
  - Delete: given_name, family_name, medicare_number, patient_id
  - Uppercase gender: "f" → "F"
  - Add silver_processed_at timestamp
  - Add data_quality flag

Step 4: Silver table created
────────────────────────────
patient_id_hash=df1e400..., date_of_birth=1985-03-15,
gender=F, postcode=2000, data_quality=OK

Step 5: Gold aggregation
──────────────────────────
group by postcode → count patients, female, male
gold_patients_by_postcode: {postcode:2000, patient_count:1, female_count:1, male_count:0}

Step 6: Power BI dashboard
───────────────────────────
SQL Warehouse serves Gold data to Power BI
Bar chart shows patient distribution by postcode
```

### Resources Created

| Azure Resource | Name | Purpose |
|---------------|------|---------|
| Resource Group | rg-healthstartup-prod | Container for all project resources |
| Storage Account | adlshealthstartupprod | Stores all data files |
| Key Vault | kv-healthstartup-prod | Stores all credentials securely |
| App Registration | databricks-storage-sp | Service account for Databricks |
| Databricks Workspace | adb-healthstartup-prod | Data engineering platform |
| Databricks Cluster | etl-job-cluster | Compute for notebooks |
| Secret Scope | kv-healthstartup | Connects Databricks to Key Vault |
| DLT Pipeline | patient-etl-pipeline | Bronze → Silver → Gold automation |
| SQL Warehouse | sql-healthstartup | SQL endpoint for Power BI |
| Event Hubs | evhns-healthstartup-prod | Real-time streaming infrastructure |

### Tables Created

| Table | Layer | Contains | Who can access |
|-------|-------|----------|----------------|
| bronze_patients | Bronze | Raw data with all PHI | Data engineers only |
| silver_patients | Silver | PHI removed, hashed ID | Data engineers + scientists |
| gold_patients_by_postcode | Gold | Aggregate counts only | Everyone |
| gold_data_quality_summary | Gold | Quality metrics | Everyone |

---

## PART 11: INTERVIEW PREPARATION

### Round 1 — Basic Data Engineering Concepts

**Q: What is the difference between a Data Lake and a Data Warehouse?**

A (simple answer):
- **Data Lake:** A giant storage area for raw data in any format — spreadsheets, images, logs, database exports. Think of it like a real lake — everything pours in, in whatever form it comes. Azure Data Lake Storage Gen2 is our data lake.
- **Data Warehouse:** A structured, organised database optimised for analytics queries. Data is cleaned and organised before being stored. Think of it like a well-organised library. Snowflake and Azure Synapse are data warehouses.
- **Data Lakehouse (what we built):** Combines both — raw storage of a data lake + structured querying of a data warehouse, using Delta Lake as the "magic ingredient." Databricks is a Lakehouse platform.

---

**Q: What is Apache Spark and why do we use it?**

A: Apache Spark is a distributed computing engine — it can process massive amounts of data by splitting work across many computers simultaneously.

Imagine you need to read 1 million patient records. With a regular program (single computer), it reads them one by one. With Spark (many computers), it splits the records into chunks and reads them all at the same time — much faster.

In Databricks, Spark is the underlying engine. When we write `df = spark.read.format("delta").load(path)`, we're using Spark to read data in a distributed way.

---

**Q: What is the difference between `spark.read` and `spark.readStream`?**

A:
- `spark.read` — reads a fixed dataset that already exists (batch processing). Like reading a book that's already written.
- `spark.readStream` — reads data as it continuously arrives (stream processing). Like reading a newspaper as it's being printed — new articles keep coming.

We used `spark.read` (batch) for our DLT pipeline. For Event Hubs (real-time), we would use `spark.readStream`.

---

**Q: What is a DataFrame in Spark?**

A: A DataFrame is like a spreadsheet in memory — it has rows and columns, and you can perform operations on it (filter, sort, add columns, join with other tables). The difference from a regular spreadsheet is that a Spark DataFrame can hold billions of rows and can be processed across hundreds of computers simultaneously.

```python
# Read data into a DataFrame
df = spark.read.format("delta").load(path)

# Add a new column
df2 = df.withColumn("upper_gender", upper(col("gender")))

# Filter rows
df3 = df2.filter(col("postcode") == "2000")

# Show results
df3.show()
```

---

### Round 2 — Delta Lake

**Q: What are the key features of Delta Lake?**

A: Four main features:

1. **ACID Transactions** — No partial writes. If a pipeline fails halfway through writing 1 million rows, Delta rolls back to the previous complete state. Plain Parquet files would leave you with half the data written.

2. **Time Travel** — Query data as it was at any point in time.
   ```python
   # What did the table look like on March 29?
   spark.read.format("delta").option("timestampAsOf", "2026-03-29").load(path)
   ```

3. **Schema Enforcement** — Delta rejects data that doesn't match the table's schema. If you accidentally send a patient record with `date_of_birth` as a number instead of a date, Delta rejects it.

4. **Scalable Metadata** — Works efficiently even with millions of files, unlike plain Parquet.

---

**Q: Explain the Medallion Architecture.**

A: Medallion Architecture organises data into three layers:

- **Bronze** = Raw data, no changes. Source of truth. Never delete.
- **Silver** = Cleaned data. PHI removed in healthcare. Validated and standardised.
- **Gold** = Aggregated, analytics-ready. Pre-computed summaries for dashboards.

Why three layers instead of one?
- Different data consumers need different things
- Analysts shouldn't see raw patient names (compliance)
- If Silver processing logic is wrong, we can reprocess from Bronze
- Each layer has different access controls

---

**Q: What is Delta Live Tables and how does it differ from regular Spark?**

A: Delta Live Tables is a declarative pipeline framework. Instead of writing code that says "do step 1, then step 2, then step 3", you declare what each table should look like and let DLT figure out the execution order.

Regular Spark (you manage everything):
```python
# You write all the steps manually
bronze = spark.read.format("delta").load(bronze_path)
silver = bronze.withColumn("hash", sha2(col("id"), 256)).drop("id")
silver.write.format("delta").mode("overwrite").save(silver_path)
```

DLT (declarative):
```python
@dlt.table
def silver_patients():
    return dlt.read("bronze_patients").withColumn("hash", sha2(col("id"), 256)).drop("id")
# DLT handles: when to run, where to write, retries, monitoring
```

DLT gives you free: dependency management, data quality metrics, lineage graph, retry logic, and monitoring.

---

### Round 3 — Cloud & Azure

**Q: What is RBAC and why is it important?**

A: RBAC stands for Role-Based Access Control. Instead of giving individual people access to individual resources, you assign roles, and roles have predefined permissions.

Example without RBAC:
```
User A: can read storage account X
User A: can write to Key Vault Y
User A: can start cluster Z
... (100 individual permissions to manage)
```

Example with RBAC:
```
Role: "Data Engineer" → can read/write storage, access Key Vault, start clusters
User A → assigned "Data Engineer" role
(manage one role instead of 100 permissions)
```

In our project:
- `Key Vault Secrets Officer` role → can create/read/delete secrets
- `Key Vault Secrets User` role → can only read secrets (what AzureDatabricks needs)
- `Storage Blob Data Contributor` role → can read/write data files

---

**Q: What is a Service Principal and when would you use it instead of a user account?**

A: A Service Principal is an identity (account) for an application or automated service, not a human.

You use a Service Principal when:
- An automated pipeline needs to access Azure resources (it can't do MFA)
- You want actions logged under a service identity, not a person's identity
- The person who set it up might leave the company (the pipeline shouldn't stop working)
- You need fine-grained control over exactly what the service can access

In our project: Databricks pipeline → authenticates as `databricks-storage-sp` → accesses ADLS Gen2. The pipeline never uses anyone's personal credentials.

---

**Q: What is Azure Key Vault and what did you store in it?**

A: Azure Key Vault is a cloud-based secrets management service. It securely stores sensitive information (passwords, API keys, connection strings) and controls who can access them.

We stored:
- Storage account key (password to access our data lake)
- Service principal client ID and secret (credentials for OAuth authentication)
- Azure tenant ID (needed for authentication)
- Event Hubs connection string (for streaming)

Why not just put these in environment variables or code? Because code gets committed to Git, environment variables can be read by anyone on the system, and there's no audit trail. Key Vault logs every single access — who read which secret, when, from which IP address.

---

### Round 4 — Data Quality & Pipelines

**Q: How did you handle data quality in this project?**

A: We used three mechanisms:

1. **DLT Expectations** — declarative rules at the Silver layer:
   - Drop records with invalid gender values (`@dlt.expect_or_drop`)
   - Track records with missing date_of_birth (`data_quality = "INCOMPLETE"`)

2. **Gold layer summarisation** — the `gold_data_quality_summary` table tracks record counts by quality status per source system. If a new source sends all bad data, this table shows it immediately.

3. **PHI verification check** — a notebook that explicitly checks the Silver table has no PHI columns:
   ```python
   phi_columns = ["patient_id", "given_name", "family_name", "medicare_number"]
   leaked_phi = [c for c in phi_columns if c in silver_columns]
   if leaked_phi:
       raise Exception(f"PHI LEAK DETECTED: {leaked_phi}")
   ```

---

**Q: What is SHA-256 and why did you use it for patient IDs?**

A: SHA-256 is a cryptographic hash function. It takes any input and produces a 64-character string. The key properties:

1. **One-way:** `sha256("P001") = "df1e400..."` but you CANNOT reverse it to get "P001"
2. **Deterministic:** Same input always gives same output (useful for linking records)
3. **Unique:** Different inputs produce different outputs (almost never a collision)

Why we used it: We needed to remove the real patient ID (privacy requirement) but still be able to say "this record from the appointments table and this record from the prescriptions table belong to the same patient." SHA-256 lets us do this — both tables hash the same patient_id to the same hash value, so we can join them, without ever knowing the actual patient ID.

---

**Q: What errors did you encounter and how did you fix them?**

A: Several significant errors during setup — each taught an important lesson:

1. **`Invalid configuration value for fs.azure.account.key`**
   - Cause: Serverless DLT has a security policy blocking storage account keys
   - Fix: Switched to OAuth service principal authentication
   - Lesson: Know the limitations of Serverless compute; key-based auth works only on Classic compute

2. **`UNRESOLVED_COLUMN patient_id`**
   - Cause: DLT expectation referenced `patient_id` after it was dropped in the function
   - Fix: Changed expectation to reference `patient_id_hash` (derived column that still exists)
   - Lesson: DLT expectations run on the RETURNED DataFrame, after all transformations

3. **`CLUSTER_LAUNCH_RESOURCE_STOCKOUT`**
   - Cause: Azure free trial VM capacity unavailable in Australia East
   - Fix: Switched from Classic to Serverless DLT compute
   - Lesson: Serverless avoids VM capacity issues; important consideration for free trial accounts

4. **Secret scope creation failure via CLI**
   - Cause: CLI requires AAD token for Key Vault-backed scopes; personal accounts can't easily get this
   - Fix: Used the Databricks UI form at `#secrets/createScope`
   - Lesson: Not all CLI operations work with personal Microsoft accounts; some require UI

---

### Round 5 — Healthcare Domain

**Q: What is PHI and how did you protect it?**

A: PHI stands for Protected Health Information — any information about a person's health that can be used to identify them. Examples: patient name + diagnosis, Medicare number, medical record number.

How we protected it:

1. **Data minimisation** — Only collect what's needed for analytics. Don't store full names if you only need age groups.

2. **Pseudonymisation** — Replace real patient ID with SHA-256 hash. Records can still be linked across datasets without knowing the real ID.

3. **Data deletion** — Given name, family name, and Medicare number are permanently deleted at the Silver layer. No copies anywhere in the Gold layer.

4. **Access controls** — Even if someone gets unauthorized access to Silver, the PHI is already gone. Gold data has zero PHI.

5. **Australian data residency** — All data stays in Australia East (Sydney). Never sent to overseas servers.

---

**Q: What is data residency and why does it matter in healthcare?**

A: Data residency means ensuring data is physically stored and processed within a specific geographic boundary.

For Australian healthcare:
- My Health Records Act requires health records to be stored in Australia
- Patients have a right to know where their data is stored
- Data sent overseas may be subject to foreign government access (e.g., US CLOUD Act)

We implemented this by deploying ALL Azure resources to `Australia East` (Sydney data centre). No geo-redundancy to international regions.

In production, we would add `Australia Southeast` (Melbourne) as a disaster recovery region — still within Australia.

---

### Round 6 — System Design

**Q: How would you scale this system to handle 1TB of patient data per day?**

A: Several changes needed:

1. **Partitioning Bronze and Silver tables** by date:
   ```python
   df.write.format("delta") \
     .partitionBy("year", "month") \
     .save(bronze_path)
   ```
   This means queries for a specific month only read that month's files — much faster.

2. **Autoscaling clusters** instead of single node:
   - Use multi-node cluster with autoscaling (2-20 workers)
   - Spot VMs for workers (60-80% cheaper, interruptible)
   - Reserved instance for driver (stable)

3. **Change from batch to streaming** for real-time requirements:
   - Event Hubs for ingestion
   - Structured Streaming for processing
   - 5-minute micro-batches instead of daily batch

4. **Add monitoring and alerting:**
   - Azure Monitor for infrastructure metrics
   - Databricks alerts for pipeline failures
   - PagerDuty/Teams notifications for data quality failures

5. **CI/CD pipeline:**
   - GitHub Actions triggers deployment when code is pushed
   - Databricks CLI deploys updated notebooks and pipeline definitions
   - Automated testing before deployment

6. **Unity Catalog** for enterprise governance:
   - Centralised data catalog across all workspaces
   - Column-level security (hide specific columns from certain users)
   - Data lineage tracking across workspaces
   - Requires organisational Azure AD account (not personal)

---

**Q: What would you do differently if you were starting this project again?**

A: Several things:

1. **Start with Unity Catalog** — we ended up using Hive Metastore because of the personal account limitation. In a real company, Unity Catalog provides much better governance, data lineage, and access control.

2. **Infrastructure as Code (Terraform)** — instead of clicking through the Azure Portal, define all resources in Terraform code. This makes it reproducible, version-controlled, and auditable.

3. **Add Auto Loader** for Bronze ingestion — instead of writing a static batch, use Auto Loader to automatically pick up new files as they land:
   ```python
   @dlt.table
   def bronze_patients():
       return spark.readStream.format("cloudFiles") \
           .option("cloudFiles.format", "json") \
           .load("abfss://landing@adlshealthstartupprod.dfs.core.windows.net/patients")
   ```

4. **Add column-level encryption** for extra protection — even Silver data could have `date_of_birth` encrypted, only decrypted for authorised queries.

5. **Set up proper CI/CD** — GitHub Actions pipeline that runs tests, validates code, and deploys to Databricks automatically.

---

## GLOSSARY — Every Term Explained Simply

| Term | Simple Explanation |
|------|-------------------|
| **ADLS Gen2** | Azure's cloud storage, optimised for big data |
| **Apache Spark** | Distributed computing engine — processes data across many computers |
| **ACID** | Database guarantee: no partial writes, always consistent, isolated concurrent access, durable |
| **Azure** | Microsoft's cloud computing platform |
| **Bronze/Silver/Gold** | Medallion architecture layers: raw → clean → aggregated |
| **Cluster** | A set of computers working together to process data |
| **Container** | A folder in cloud storage (like a drawer in a filing cabinet) |
| **DAG** | Directed Acyclic Graph — the execution plan showing which steps depend on which |
| **DataFrame** | A table of data in Spark memory — has rows, columns, and schema |
| **DBU** | Databricks Unit — the billing unit for Databricks compute |
| **Delta Lake** | Storage format adding ACID transactions, time travel, and schema enforcement |
| **DLT** | Delta Live Tables — Databricks' declarative pipeline framework |
| **ETL** | Extract, Transform, Load — the process of moving and transforming data |
| **GDPR/Privacy Act** | Laws protecting personal data |
| **Hash (SHA-256)** | One-way function that converts data into a fixed-length string; cannot be reversed |
| **Key Vault** | Azure's secure digital safe for passwords and secrets |
| **LTS** | Long Term Support — a software version guaranteed to be stable and patched for years |
| **Managed Identity** | Azure-managed service account (no credential management needed) |
| **Medallion Architecture** | Bronze/Silver/Gold data organisation pattern |
| **OAuth** | Open Authorization — industry-standard token-based authentication |
| **Parquet** | Efficient columnar file format for big data |
| **PAT** | Personal Access Token — a password substitute for API authentication |
| **PHI** | Protected Health Information — health data that can identify a person |
| **PII** | Personally Identifiable Information — any data that identifies a person |
| **Pipeline** | Automated workflow that moves and transforms data |
| **RBAC** | Role-Based Access Control — permissions assigned via roles |
| **Resource Group** | Azure container grouping related resources together |
| **Secret Scope** | Databricks named group of secrets linked to Key Vault |
| **Service Principal** | An Azure identity for applications (not humans) |
| **Shuffle** | Spark operation where data moves between computers — expensive |
| **Spark** | Distributed computing framework for processing large datasets |
| **SQL Warehouse** | Databricks SQL-only compute for BI tools |
| **Streaming** | Processing data continuously as it arrives (vs. batch: processing a fixed set) |
| **Tenant** | An organisation's Azure Active Directory instance |
| **Time Travel** | Delta Lake feature to query historical versions of data |
| **Unity Catalog** | Databricks centralised data governance (requires org account) |
| **Z-ordering** | Delta Lake file layout optimisation for faster multi-column queries |
