# Secure Databricks Environment for an Australian Healthcare Startup
### Complete Beginner's Guide — Unity Catalog + Azure Free Trial

---

## Who This Guide Is For

You are a **fresher** building a **Greenfield healthcare company in Australia**.
You have no prior Azure or Databricks experience.
This guide explains **every step, every component, and every reason why**.

---

## Understanding the Big Picture Before You Start

### What is "Greenfield"?
A Greenfield project means you are building everything **from scratch** — no legacy systems, no old data. You get to design it the right way from day one.

### Why Does Healthcare Need Extra Security?
In Australia, healthcare data is protected by:
- **Privacy Act 1988** — protects personal information
- **My Health Records Act 2012** — protects electronic health records
- **Australian Privacy Principles (APPs)** — 13 principles that govern how health data is handled
- **HIPAA equivalence** — many Australian health companies also follow US HIPAA as best practice

If patient data is breached, the penalties can be millions of dollars AND criminal charges. This is why we build security into every layer.

### What Are We Building?
```
YOUR LAPTOP
    |
    v
AZURE (Microsoft Cloud) ← Where your data lives (servers in Australia)
    |
    v
DATABRICKS (Data Platform) ← Where you process and analyse data
    |
    v
UNITY CATALOG ← The security layer that controls WHO can see WHAT data
    |
    v
YOUR HEALTH DATA (Patient records, clinical notes, Medicare claims)
```

---

## PHASE 1: Azure Free Trial Setup

### Step 1.1 — Create Your Azure Free Trial Account

**What is Azure?**
Azure is Microsoft's cloud platform. Instead of buying physical servers, you rent computing power from Microsoft. For a startup, this means:
- No upfront hardware cost
- Pay only for what you use
- Data stored in Australia (important for compliance)

**Free Trial gives you:**
- $200 USD credit for 30 days
- 12 months of free services after that
- Always-free tier for some services

**How to do it:**
1. Go to portal.azure.com
2. Click "Start free"
3. Sign in with a Microsoft account (or create one)
4. Enter your credit card (for identity verification — you won't be charged during free trial)
5. Select your country as **Australia**

**Why Australia matters:**
When you select Australia, Microsoft stores your data in their **Australian data centres** (Sydney and Melbourne). This satisfies Australian data sovereignty requirements — patient data must not leave Australia without consent.

---

### Step 1.2 — Create a Resource Group

**What is a Resource Group?**
Think of it like a **folder on your computer**. All the Azure services you create go inside this folder. When your startup grows and you need to delete or move things, you operate on the whole folder instead of individual items.

**Why it matters for security:**
You can apply security policies to the entire resource group. Every service inside inherits those policies.

**How to do it:**
1. In Azure Portal, search for "Resource Groups" in the top search bar
2. Click "+ Create"
3. Fill in:
   - **Subscription**: Azure subscription 1 (your free trial)
   - **Resource group name**: `rg-healthstartup-prod`
   - **Region**: `Australia East` (Sydney data centre)
4. Click "Review + Create" then "Create"

**Naming explained:**
- `rg` = resource group (standard prefix)
- `healthstartup` = your company name
- `prod` = production environment

---

### Step 1.3 — Create Azure Data Lake Storage (ADLS Gen2)

**What is ADLS Gen2?**
This is where your actual data files are stored. Think of it as a **hard drive in the cloud** that is:
- Infinitely scalable (grows as your data grows)
- Hierarchical (organised in folders like a normal file system)
- Secure (encrypted at rest and in transit)

**Why Gen2 specifically?**
Gen2 adds a hierarchical namespace (real folders) on top of blob storage. Databricks requires this to work efficiently with Delta Lake format.

**How to do it:**
1. Search "Storage accounts" in Azure Portal
2. Click "+ Create"
3. Fill in:
   - **Resource group**: `rg-healthstartup-prod`
   - **Storage account name**: `adlshealthstartup` (must be globally unique, lowercase, no hyphens)
   - **Region**: `Australia East`
   - **Performance**: Standard
   - **Redundancy**: `Locally-redundant storage (LRS)` — cheapest, fine for free trial

4. Go to **Advanced** tab:
   - Enable **Hierarchical namespace** = YES (this is what makes it Gen2)
   - Enable **Secure transfer required** = YES (forces HTTPS only)
   - **Minimum TLS version**: TLS 1.2

5. Go to **Networking** tab:
   - **Network access**: "Enable public access from selected virtual networks and IP addresses"
   - We will restrict this further later

6. Click "Review + Create" then "Create"

**Why TLS 1.2?**
TLS is the encryption protocol for data moving over the internet. Older versions (1.0, 1.1) have known security vulnerabilities. Healthcare standards require TLS 1.2 minimum.

**Create your container structure:**
After the storage account is created:
1. Go to your storage account → "Containers" → "+ Container"
2. Create these containers (think of them as top-level folders):

| Container Name | Purpose |
|---------------|---------|
| `bronze` | Raw data exactly as received from source systems |
| `silver` | Cleaned, validated, standardised data |
| `gold` | Aggregated, business-ready data for reporting |
| `unity-catalog` | Unity Catalog managed storage |

**Why Bronze/Silver/Gold (Medallion Architecture)?**
This is an industry-standard pattern for healthcare data:
- **Bronze**: Keep the original raw data forever. If something goes wrong, you can always reprocess from here.
- **Silver**: Cleaned data. Patient names standardised, dates in correct format, nulls handled.
- **Gold**: Ready for doctors/analysts/dashboards. Fast queries, pre-aggregated.

This separation is also required for **audit trails** — regulators may ask "show me the original data you received on this date."

---

### Step 1.4 — Create Azure Key Vault

**What is Key Vault?**
A Key Vault is like a **highly secure safe** that stores:
- Passwords
- API keys
- Connection strings
- Encryption keys

**Why not just put passwords in your code?**
If someone gains access to your code repository (like GitHub), they get all your passwords. Key Vault separates secrets from code. Your code asks "give me the database password" and Key Vault checks if that code is authorised before handing it over.

**How to do it:**
1. Search "Key vaults" in Azure Portal
2. Click "+ Create"
3. Fill in:
   - **Resource group**: `rg-healthstartup-prod`
   - **Key vault name**: `kv-healthstartup-prod`
   - **Region**: `Australia East`
   - **Pricing tier**: Standard
4. Go to **Access configuration** tab:
   - **Permission model**: `Azure role-based access control (RBAC)`
   - This is more secure than the older "Vault access policy" model
5. Click "Review + Create" then "Create"

---

### Step 1.5 — Create Azure Active Directory App Registration

**What is App Registration?**
When Databricks needs to access your storage, it needs to **prove its identity**. An App Registration is like creating an **identity card** for Databricks. Azure will only allow Databricks to access data if it can present this identity card.

**How to do it:**
1. Search "App registrations" in Azure Portal
2. Click "+ New registration"
3. Fill in:
   - **Name**: `databricks-healthstartup-sp`
   - **Supported account types**: "Accounts in this organizational directory only"
4. Click "Register"
5. After creation, note down:
   - **Application (client) ID** — copy this, you'll need it later
   - **Directory (tenant) ID** — copy this too

6. Create a client secret:
   - Go to "Certificates & secrets" → "+ New client secret"
   - Description: `databricks-access`
   - Expires: 12 months
   - Click "Add"
   - **IMMEDIATELY copy the secret value** — Azure only shows it once!

7. Store the secret in Key Vault:
   - Go to your Key Vault → "Secrets" → "+ Generate/Import"
   - Name: `databricks-sp-secret`
   - Value: paste the secret you just copied

**Why a Service Principal instead of your personal account?**
If you leave the company or your account is compromised, you don't want Databricks to stop working or expose all your personal data. A service principal is a non-human identity specifically for this purpose.

---

### Step 1.6 — Assign Permissions (RBAC)

**What is RBAC?**
Role-Based Access Control means you assign **roles** (not individual permissions) to identities. Roles are bundles of permissions. Examples:
- `Storage Blob Data Contributor` = can read and write files
- `Storage Blob Data Reader` = can only read files
- `Key Vault Secrets User` = can read secrets but not create them

**Principle of Least Privilege:**
Give every identity only the **minimum permissions it needs** to do its job. This is a core security principle — if Databricks is compromised, it can only damage what it has access to.

**Assign permissions to the Service Principal:**
1. Go to your storage account → "Access Control (IAM)" → "+ Add" → "Add role assignment"
2. Role: `Storage Blob Data Contributor`
3. Members: search for `databricks-healthstartup-sp`
4. Click "Review + assign"

5. Go to your Key Vault → "Access Control (IAM)" → "+ Add" → "Add role assignment"
6. Role: `Key Vault Secrets User`
7. Members: `databricks-healthstartup-sp`
8. Click "Review + assign"

---

## PHASE 2: Create the Databricks Workspace

### Step 2.1 — What is Databricks?

Databricks is a **data analytics platform** built on top of Apache Spark. Think of it as:
- A very powerful Excel that can handle millions of rows
- A collaborative notebook environment where you write Python/SQL code
- A pipeline engine that automates data processing
- A governance layer (Unity Catalog) that controls data access

For healthcare, Databricks is popular because:
- It can process FHIR (healthcare data standard) and HL7 messages
- It has built-in data lineage (track where every piece of data came from)
- It supports column-level encryption for sensitive fields like Medicare numbers

---

### Step 2.2 — Create the Databricks Workspace

**How to do it:**
1. Search "Azure Databricks" in Azure Portal
2. Click "+ Create"
3. Fill in:
   - **Resource group**: `rg-healthstartup-prod`
   - **Workspace name**: `databricks-healthstartup-prod`
   - **Region**: `Australia East`
   - **Pricing tier**: `Premium` ← CRITICAL for Unity Catalog and security features

**Why Premium tier?**
Unity Catalog, Role-Based Access Control, and audit logs are **only available in Premium tier**. For a healthcare company, these are non-negotiable. Standard tier does not support them.

4. Go to **Networking** tab:
   - **Deploy Azure Databricks workspace in your own Virtual Network**: Yes
   - This creates a VNet (private network) — your Databricks cluster won't be exposed to the public internet

5. Click "Review + Create" then "Create"

**Wait about 5 minutes for deployment.**

---

### Step 2.3 — Launch Databricks and First-Time Setup

1. Go to your Databricks resource in Azure Portal
2. Click "Launch Workspace" — this opens the Databricks UI
3. You'll land on the Databricks home page

**The Databricks Interface:**
```
LEFT SIDEBAR:
├── Catalog     ← Unity Catalog browser (see your data)
├── Workflows   ← Schedule automated jobs
├── Compute     ← Create/manage clusters (processing power)
├── Notebooks   ← Write Python/SQL code
├── SQL Editor  ← Run SQL queries
└── Settings    ← Admin settings
```

---

## PHASE 3: Unity Catalog Setup

### Step 3.1 — What is Unity Catalog?

Unity Catalog is Databricks' **data governance layer**. It is the most important security component.

**Without Unity Catalog:**
- Anyone in your Databricks workspace can see all data
- No audit trail of who accessed what
- No column-level security (can't hide Medicare numbers from junior staff)
- No data lineage

**With Unity Catalog:**
```
Unity Catalog Controls:
├── WHO can access data (user/group permissions)
├── WHAT they can see (table/column/row level)
├── WHEN they accessed it (audit logs)
├── WHERE the data came from (lineage)
└── WHY it's sensitive (data classification tags)
```

**The Hierarchy:**
```
METASTORE (one per Azure region)
    |
    ├── CATALOG (like a database server)
    |       |
    |       ├── SCHEMA (like a database / folder)
    |       |       |
    |       |       ├── TABLE (patient_demographics)
    |       |       ├── TABLE (clinical_notes)
    |       |       └── VIEW (de-identified_patients)
    |       |
    |       └── SCHEMA (another schema)
    |
    └── CATALOG (another catalog for different department)
```

**For your healthcare startup:**
```
METASTORE: healthstartup-metastore (Australia East)
    |
    ├── CATALOG: bronze_catalog     ← raw ingested data
    ├── CATALOG: silver_catalog     ← cleaned data
    ├── CATALOG: gold_catalog       ← business-ready data
    └── CATALOG: sandbox_catalog    ← for testing/development
```

---

### Step 3.2 — Create the Unity Catalog Metastore

**What is a Metastore?**
A Metastore is the **central registry** that stores all metadata (information about your data — table names, column names, who owns what, permissions). It is the brain of Unity Catalog.

**One critical rule:** One metastore per Azure region per Databricks account. All your workspaces in Australia East share one metastore.

**How to do it:**
1. Go to accounts.azuredatabricks.net (the account-level portal, different from workspace)
2. Sign in with the same Azure account
3. Go to **Data** → **Create metastore**
4. Fill in:
   - **Name**: `healthstartup-metastore-australiaeast`
   - **Region**: `australiaeast`
   - **ADLS Gen2 path**: `abfss://unity-catalog@adlshealthstartup.dfs.core.windows.net/`
5. Click "Create"

**Assign the metastore to your workspace:**
1. Still in accounts.azuredatabricks.net
2. Go to **Data** → select your metastore → **Assign to workspace**
3. Select `databricks-healthstartup-prod`
4. Click "Assign"

---

### Step 3.3 — Configure Storage Credential

**What is a Storage Credential?**
Remember the Service Principal (identity card) we created in Step 1.5? A Storage Credential is how we register that identity card **inside Databricks** so Unity Catalog can use it to access your ADLS storage.

**How to do it:**
In the Databricks workspace:
1. Go to **Catalog** → **+** → **Add a storage credential**
2. Fill in:
   - **Credential name**: `adls-healthstartup-credential`
   - **Authentication type**: Service Principal
   - **Directory (tenant) ID**: paste from Step 1.5
   - **Application (client) ID**: paste from Step 1.5
   - **Client secret**: paste the secret value from Step 1.5
3. Click "Create"

---

### Step 3.4 — Create External Locations

**What is an External Location?**
An External Location is a **registered path** in your storage that Unity Catalog knows about and can govern. You can't just use any arbitrary path — you must register it.

**How to do it:**
1. Go to **Catalog** → **+** → **Add an external location**
2. Create four external locations:

**External Location 1 — Bronze:**
- Name: `bronze-external-location`
- URL: `abfss://bronze@adlshealthstartup.dfs.core.windows.net/`
- Storage credential: `adls-healthstartup-credential`

**External Location 2 — Silver:**
- Name: `silver-external-location`
- URL: `abfss://silver@adlshealthstartup.dfs.core.windows.net/`
- Storage credential: `adls-healthstartup-credential`

**External Location 3 — Gold:**
- Name: `gold-external-location`
- URL: `abfss://gold@adlshealthstartup.dfs.core.windows.net/`
- Storage credential: `adls-healthstartup-credential`

**External Location 4 — Unity Catalog managed:**
- Name: `unitycatalog-managed-location`
- URL: `abfss://unity-catalog@adlshealthstartup.dfs.core.windows.net/`
- Storage credential: `adls-healthstartup-credential`

3. For each, click **Test connection** to verify it works, then **Create**

---

### Step 3.5 — Create Catalogs

**How to do it:**
In Databricks, open a notebook or use the SQL Editor and run:

```sql
-- Create Bronze catalog (raw data)
CREATE CATALOG IF NOT EXISTS bronze_catalog
  MANAGED LOCATION 'abfss://bronze@adlshealthstartup.dfs.core.windows.net/'
  COMMENT 'Raw ingested healthcare data - do not modify';

-- Create Silver catalog (cleaned data)
CREATE CATALOG IF NOT EXISTS silver_catalog
  MANAGED LOCATION 'abfss://silver@adlshealthstartup.dfs.core.windows.net/'
  COMMENT 'Cleaned and validated healthcare data';

-- Create Gold catalog (business-ready)
CREATE CATALOG IF NOT EXISTS gold_catalog
  MANAGED LOCATION 'abfss://gold@adlshealthstartup.dfs.core.windows.net/'
  COMMENT 'Aggregated data ready for reporting and dashboards';

-- Create Sandbox catalog (for development/testing)
CREATE CATALOG IF NOT EXISTS sandbox_catalog
  COMMENT 'Development and testing - no real patient data allowed here';
```

---

### Step 3.6 — Create Schemas Inside Each Catalog

```sql
-- Bronze schemas (organised by source system)
CREATE SCHEMA IF NOT EXISTS bronze_catalog.clinic_erp
  COMMENT 'Raw data from clinic ERP system';

CREATE SCHEMA IF NOT EXISTS bronze_catalog.pathology_lab
  COMMENT 'Raw data from pathology lab systems';

CREATE SCHEMA IF NOT EXISTS bronze_catalog.medicare_claims
  COMMENT 'Raw Medicare claims data';

-- Silver schemas (organised by data domain)
CREATE SCHEMA IF NOT EXISTS silver_catalog.patients
  COMMENT 'Cleaned patient demographic data';

CREATE SCHEMA IF NOT EXISTS silver_catalog.clinical
  COMMENT 'Cleaned clinical events and encounters';

CREATE SCHEMA IF NOT EXISTS silver_catalog.billing
  COMMENT 'Cleaned billing and claims data';

-- Gold schemas
CREATE SCHEMA IF NOT EXISTS gold_catalog.reporting
  COMMENT 'Pre-aggregated data for dashboards';

CREATE SCHEMA IF NOT EXISTS gold_catalog.analytics
  COMMENT 'Data for analytical queries';
```

---

## PHASE 4: Security Configuration

### Step 4.1 — Create User Groups

**What are Groups?**
Instead of assigning permissions to individual users (which becomes unmanageable as your team grows), you assign permissions to **groups**. Then you add users to groups.

Example: If 5 doctors all need access to patient tables, you add them to the `clinical-staff` group and give that group permission — not each doctor individually.

**Healthcare-specific groups to create:**

Go to **Settings** → **Identity and Access** → **Groups** → **Add group**:

| Group Name | Who Belongs Here | Access Level |
|-----------|-----------------|-------------|
| `data-engineers` | Your data team | Can create/modify tables |
| `clinical-staff` | Doctors, nurses | Can READ silver/gold patient data |
| `data-analysts` | Business analysts | Can READ gold data only |
| `data-admins` | IT administrators | Full admin access |
| `auditors` | Compliance/audit team | Read-only access to all data + audit logs |
| `developers` | Dev/test engineers | Access to sandbox only |

---

### Step 4.2 — Grant Permissions Using Unity Catalog

**The permission model works like this:**
To access a table, a user needs permissions at EVERY level:
- Permission to USE the **catalog**
- Permission to USE the **schema**
- Permission to SELECT on the **table**

```sql
-- ============================================================
-- CLINICAL STAFF permissions
-- They can read cleaned patient data (silver) but NOT raw (bronze)
-- ============================================================

GRANT USE CATALOG ON CATALOG silver_catalog TO `clinical-staff`;
GRANT USE CATALOG ON CATALOG gold_catalog TO `clinical-staff`;

GRANT USE SCHEMA ON SCHEMA silver_catalog.patients TO `clinical-staff`;
GRANT USE SCHEMA ON SCHEMA silver_catalog.clinical TO `clinical-staff`;
GRANT USE SCHEMA ON SCHEMA gold_catalog.reporting TO `clinical-staff`;

-- They can SELECT (read) but not INSERT/UPDATE/DELETE
GRANT SELECT ON SCHEMA silver_catalog.patients TO `clinical-staff`;
GRANT SELECT ON SCHEMA silver_catalog.clinical TO `clinical-staff`;
GRANT SELECT ON SCHEMA gold_catalog.reporting TO `clinical-staff`;

-- ============================================================
-- DATA ENGINEERS permissions
-- They process data through all layers
-- ============================================================

GRANT USE CATALOG ON CATALOG bronze_catalog TO `data-engineers`;
GRANT USE CATALOG ON CATALOG silver_catalog TO `data-engineers`;
GRANT USE CATALOG ON CATALOG gold_catalog TO `data-engineers`;

GRANT CREATE SCHEMA ON CATALOG bronze_catalog TO `data-engineers`;
GRANT CREATE SCHEMA ON CATALOG silver_catalog TO `data-engineers`;
GRANT CREATE SCHEMA ON CATALOG gold_catalog TO `data-engineers`;

GRANT ALL PRIVILEGES ON CATALOG bronze_catalog TO `data-engineers`;
GRANT ALL PRIVILEGES ON CATALOG silver_catalog TO `data-engineers`;
GRANT ALL PRIVILEGES ON CATALOG gold_catalog TO `data-engineers`;

-- ============================================================
-- DATA ANALYSTS permissions
-- Gold layer only, read-only
-- ============================================================

GRANT USE CATALOG ON CATALOG gold_catalog TO `data-analysts`;
GRANT USE SCHEMA ON SCHEMA gold_catalog.reporting TO `data-analysts`;
GRANT USE SCHEMA ON SCHEMA gold_catalog.analytics TO `data-analysts`;
GRANT SELECT ON SCHEMA gold_catalog.reporting TO `data-analysts`;
GRANT SELECT ON SCHEMA gold_catalog.analytics TO `data-analysts`;

-- ============================================================
-- DEVELOPERS permissions
-- Sandbox only
-- ============================================================

GRANT ALL PRIVILEGES ON CATALOG sandbox_catalog TO `developers`;

-- ============================================================
-- AUDITORS permissions
-- Read everything, modify nothing
-- ============================================================

GRANT USE CATALOG ON CATALOG bronze_catalog TO `auditors`;
GRANT USE CATALOG ON CATALOG silver_catalog TO `auditors`;
GRANT USE CATALOG ON CATALOG gold_catalog TO `auditors`;
GRANT SELECT ON CATALOG bronze_catalog TO `auditors`;
GRANT SELECT ON CATALOG silver_catalog TO `auditors`;
GRANT SELECT ON CATALOG gold_catalog TO `auditors`;
```

---

### Step 4.3 — Column-Level Security (Masking Sensitive Data)

**What is Column-Level Security?**
In healthcare, not everyone should see full patient details. A billing analyst needs to know a patient had an appointment, but doesn't need to see their Medicare number or date of birth.

**Column masking** replaces sensitive values with masked versions based on who is asking:
- A doctor sees: `2123456701` (full Medicare number)
- An analyst sees: `****456701` (masked)
- An auditor sees: `[REDACTED]` (fully hidden)

```sql
-- First, create the patient demographics table
CREATE TABLE IF NOT EXISTS silver_catalog.patients.demographics (
  patient_id      STRING NOT NULL,
  given_name      STRING,
  family_name     STRING,
  date_of_birth   DATE,
  gender          STRING,
  medicare_number STRING,
  postcode        STRING,
  phone_number    STRING,
  email_address   STRING,
  ingested_at     TIMESTAMP NOT NULL,
  source_system   STRING NOT NULL
);

-- Create a masking function for Medicare numbers
CREATE OR REPLACE FUNCTION silver_catalog.patients.mask_medicare(medicare STRING)
RETURNS STRING
LANGUAGE SQL
RETURN
  CASE
    WHEN is_member('clinical-staff') THEN medicare          -- doctors see full number
    WHEN is_member('data-analysts')  THEN concat('****', right(medicare, 6))  -- analysts see last 6
    WHEN is_member('auditors')       THEN '[REDACTED]'      -- auditors see nothing
    ELSE '[ACCESS DENIED]'
  END;

-- Apply the masking function to the column
ALTER TABLE silver_catalog.patients.demographics
  ALTER COLUMN medicare_number
  SET MASK silver_catalog.patients.mask_medicare;

-- Mask phone numbers too
CREATE OR REPLACE FUNCTION silver_catalog.patients.mask_phone(phone STRING)
RETURNS STRING
LANGUAGE SQL
RETURN
  CASE
    WHEN is_member('clinical-staff') THEN phone
    ELSE concat('****', right(phone, 4))
  END;

ALTER TABLE silver_catalog.patients.demographics
  ALTER COLUMN phone_number
  SET MASK silver_catalog.patients.mask_phone;
```

---

### Step 4.4 — Row-Level Security (Patients See Only Their Own Data)

**What is Row-Level Security?**
A patient portal should only show a patient their own records, not every patient's data. Row-level security filters which **rows** a user can see based on their identity.

```sql
-- Create a row filter function
-- This is used when patients log in via a portal
CREATE OR REPLACE FUNCTION silver_catalog.patients.filter_own_records(patient_id STRING)
RETURNS BOOLEAN
LANGUAGE SQL
RETURN
  -- Clinical staff see ALL patients
  is_member('clinical-staff')
  OR
  -- Admins see everything
  is_member('data-admins')
  OR
  -- A patient only sees their own row
  -- (current_user() returns the logged-in user's email)
  -- In production, map patient_id to user email via a lookup table
  patient_id = current_user();

-- Apply the row filter to the table
ALTER TABLE silver_catalog.patients.demographics
  SET ROW FILTER silver_catalog.patients.filter_own_records ON (patient_id);
```

---

### Step 4.5 — Create De-identified Views

**Why de-identified views?**
For analytics and research, you often don't need real patient identifiers. De-identified data (data with all identifying information removed) has fewer legal restrictions and can be shared more freely.

```sql
-- A de-identified view that researchers can use
CREATE OR REPLACE VIEW gold_catalog.analytics.deidentified_patients AS
SELECT
  -- Use a hash of the real ID — consistent but not reversible
  sha2(patient_id, 256)                    AS hashed_patient_id,
  -- Age range instead of exact date of birth
  CASE
    WHEN datediff(current_date(), date_of_birth) / 365 < 18  THEN 'Under 18'
    WHEN datediff(current_date(), date_of_birth) / 365 < 30  THEN '18-29'
    WHEN datediff(current_date(), date_of_birth) / 365 < 45  THEN '30-44'
    WHEN datediff(current_date(), date_of_birth) / 365 < 60  THEN '45-59'
    WHEN datediff(current_date(), date_of_birth) / 365 < 75  THEN '60-74'
    ELSE '75+'
  END                                      AS age_group,
  gender,
  -- Only first 3 digits of postcode (region, not exact location)
  left(postcode, 3)                        AS postcode_region,
  source_system,
  date_trunc('month', ingested_at)         AS ingestion_month
  -- Medicare number, name, phone, email deliberately excluded
FROM silver_catalog.patients.demographics;

-- Grant access to researchers
GRANT SELECT ON VIEW gold_catalog.analytics.deidentified_patients TO `data-analysts`;
```

---

## PHASE 5: Compute Security (Clusters)

### Step 5.1 — What is a Cluster?

A cluster is the **computing power** that runs your notebooks and jobs. It is a group of virtual machines (servers) that Spark uses to process data in parallel.

**Types of clusters:**
- **All-Purpose Cluster**: For interactive work in notebooks (you run code manually)
- **Job Cluster**: Created automatically for scheduled jobs, terminated when done (cheaper)

For a free trial, you want to be careful about cluster costs — they run up quickly!

---

### Step 5.2 — Create a Secure Cluster

Go to **Compute** → **Create compute**:

```
Cluster name:     healthstartup-shared-cluster
Policy:           Unrestricted (for now; create policies later)
Cluster mode:     Single node (cheapest for development)
Databricks runtime: 15.4 LTS (Long Term Support) — always use LTS for stability
Node type:        Standard_DS3_v2 (cheapest that supports Unity Catalog)
```

**Critical security settings (click "Advanced options"):**

**Spark config tab — add these:**
```
spark.databricks.unityCatalog.enabled true
spark.databricks.repl.allowedLanguages python,sql
spark.databricks.acl.dfAclsEnabled true
```

**Auto-termination:** Set to **30 minutes** of inactivity
- Why: A running cluster costs money. If you forget to turn it off, it drains your free trial credit fast.

---

### Step 5.3 — Cluster Access Control

By default, any workspace user can attach to any cluster. In healthcare, you want to control this.

1. Go to your cluster → **Permissions**
2. Set:
   - `data-admins` group: **Can Manage**
   - `data-engineers` group: **Can Restart**
   - `clinical-staff` group: **Can Attach To**
   - `developers` group: **Can Attach To**
   - All other users: **No permissions**

---

## PHASE 6: Audit Logging

### Step 6.1 — What are Audit Logs?

Audit logs record **every action** taken in your Databricks workspace:
- Who logged in
- Who ran which query
- Who accessed which table
- Who changed permissions
- Who downloaded data

For Australian healthcare compliance, you must be able to answer: **"Who accessed patient X's records on date Y?"**

---

### Step 6.2 — Enable Diagnostic Logging

1. Go to Azure Portal → your Databricks workspace
2. Go to **Diagnostic settings** → **+ Add diagnostic setting**
3. Fill in:
   - **Diagnostic setting name**: `databricks-audit-logs`
   - **Logs**: Check `accounts`, `clusters`, `dbfs`, `instancePools`, `jobs`, `notebook`, `secrets`, `sqlPermissions`, `workspace`
   - **Destination**: Send to **Log Analytics workspace** (create one if needed)
4. Click "Save"

**What each log category means:**
| Category | What it records |
|---------|----------------|
| `accounts` | User login/logout |
| `clusters` | Cluster start/stop/create/delete |
| `notebook` | Notebook commands run |
| `sqlPermissions` | Permission grants/revokes |
| `secrets` | Secret access (not the value, just that it was accessed) |
| `workspace` | File/notebook create/delete |

---

## PHASE 7: Network Security

### Step 7.1 — What is a Virtual Network (VNet)?

A VNet is a **private network** in the cloud. By default, cloud services are accessible from the public internet. A VNet puts your services inside a private network — like your office's internal network.

**Why this matters for healthcare:**
Patient data should never be accessible from the public internet, even accidentally.

We already enabled VNet injection when creating the Databricks workspace (Step 2.2). Here's what that means:

```
PUBLIC INTERNET
      |
   FIREWALL
      |
   VNet (your private network in Azure)
      |
      ├── Databricks Subnet (where clusters run)
      └── Storage Subnet (where ADLS lives)
```

---

### Step 7.2 — Configure Private Endpoints for Storage

**What is a Private Endpoint?**
Normally, your ADLS storage has a public URL that anyone can try to access. A Private Endpoint gives your storage a **private IP address inside your VNet** — the storage becomes accessible only from within your network.

1. Go to your storage account → **Networking** → **Private endpoint connections** → **+ Private endpoint**
2. Fill in:
   - **Name**: `pe-adls-healthstartup`
   - **Region**: `Australia East`
   - **Target sub-resource**: `dfs` (Data Lake Storage)
3. In **Virtual Network** tab: select the VNet Databricks created
4. Click "Review + Create" then "Create"

After this, disable public access to storage:
- Go to storage account → **Networking** → **Public network access**: **Disabled**

---

## PHASE 8: Sample Healthcare Tables

### Step 8.1 — Patient Demographics Table

Open a Databricks notebook and run:

```python
from pyspark.sql.types import *
from pyspark.sql import Row
from datetime import date, datetime

# Always define schemas explicitly in healthcare
# This ensures bad data is rejected, not silently stored
patient_schema = StructType([
    StructField("patient_id",      StringType(),    nullable=False),
    StructField("given_name",      StringType(),    nullable=True),
    StructField("family_name",     StringType(),    nullable=True),
    StructField("date_of_birth",   DateType(),      nullable=True),
    StructField("gender",          StringType(),    nullable=True),
    StructField("medicare_number", StringType(),    nullable=True),
    StructField("postcode",        StringType(),    nullable=True),
    StructField("phone_number",    StringType(),    nullable=True),
    StructField("email_address",   StringType(),    nullable=True),
    StructField("ingested_at",     TimestampType(), nullable=False),
    StructField("source_system",   StringType(),    nullable=False)
])

sample_patients = [
    Row(patient_id="P001", given_name="Jane", family_name="Smith",
        date_of_birth=date(1985, 3, 15), gender="F",
        medicare_number="2123456701", postcode="2000",
        phone_number="0412345678", email_address="jane.smith@email.com",
        ingested_at=datetime.now(), source_system="clinic-erp"),
    Row(patient_id="P002", given_name="John", family_name="Doe",
        date_of_birth=date(1962, 7, 22), gender="M",
        medicare_number="3987654302", postcode="3000",
        phone_number="0498765432", email_address="john.doe@email.com",
        ingested_at=datetime.now(), source_system="clinic-erp"),
]

df = spark.createDataFrame(sample_patients, schema=patient_schema)

# Write to Unity Catalog as a Delta table
df.write \
  .format("delta") \
  .mode("overwrite") \
  .saveAsTable("silver_catalog.patients.demographics")

print("Patient table created successfully.")
```

**Why Delta format?**
Delta Lake adds ACID transactions to data files. ACID means:
- **Atomic**: A write either fully completes or fully fails — no partial data
- **Consistent**: Data is always valid
- **Isolated**: Concurrent writes don't corrupt each other
- **Durable**: Once written, data persists even if the system crashes

For healthcare, this is critical — a partial patient record write could corrupt medical history.

---

### Step 8.2 — Verify Security is Working

```sql
-- Check who owns the table
DESCRIBE TABLE EXTENDED silver_catalog.patients.demographics;

-- Check current permissions
SHOW GRANTS ON TABLE silver_catalog.patients.demographics;

-- Verify row count
SELECT COUNT(*) as total_patients FROM silver_catalog.patients.demographics;

-- Test masked column (Medicare number should appear based on your group)
SELECT patient_id, given_name, medicare_number
FROM silver_catalog.patients.demographics;
```

---

## PHASE 9: Australian Compliance Checklist

### Requirements Under Australian Privacy Act & My Health Records Act

| Requirement | How We've Met It | Status |
|-------------|-----------------|--------|
| Data stored in Australia | ADLS in Australia East (Sydney) | Done |
| Encryption at rest | ADLS default encryption (AES-256) | Done |
| Encryption in transit | TLS 1.2 enforced on storage | Done |
| Access control | Unity Catalog RBAC + ABAC | Done |
| Audit logging | Databricks diagnostic logs | Done |
| Data minimisation | Column masking, de-identified views | Done |
| Right to access | Row-level filtering for patient portal | Done |
| Breach notification | Set up Azure Security Center alerts | To do |
| Data retention policy | Delta Lake time travel (30 day default) | Partial |

---

## PHASE 10: Cost Management (Free Trial Tips)

### How to Not Exhaust Your $200 Credit

| Risk | Action |
|------|--------|
| Cluster left running | Set auto-termination to 30 minutes |
| Large cluster size | Use Single Node for development |
| Storage costs | Use LRS redundancy (cheapest) |
| Forgotten resources | Set budget alert at $150 in Azure Cost Management |

**Set a budget alert:**
1. Azure Portal → search "Cost Management"
2. **Budgets** → **+ Add**
3. Amount: $150, Period: Monthly
4. Alert at 80% and 100%
5. Send email to yourself

---

## Summary: Your Security Architecture

```
┌─────────────────────────────────────────────────────┐
│                  AZURE AUSTRALIA EAST                │
│                                                     │
│  ┌─────────────────────────────────────────────┐   │
│  │           Virtual Network (VNet)             │   │
│  │                                             │   │
│  │   ┌──────────────┐    ┌──────────────────┐  │   │
│  │   │  Databricks  │    │   ADLS Gen2      │  │   │
│  │   │  Workspace   │◄──►│  (Private        │  │   │
│  │   │  (Premium)   │    │   Endpoint)      │  │   │
│  │   └──────┬───────┘    └──────────────────┘  │   │
│  │          │                                   │   │
│  │   ┌──────▼───────┐    ┌──────────────────┐  │   │
│  │   │Unity Catalog │    │   Key Vault      │  │   │
│  │   │  Metastore   │    │  (Secrets)       │  │   │
│  │   └──────────────┘    └──────────────────┘  │   │
│  └─────────────────────────────────────────────┘   │
│                                                     │
│  ┌─────────────────────────────────────────────┐   │
│  │           Security Layers                    │   │
│  │  Network → VNet + Private Endpoints          │   │
│  │  Identity → RBAC + Service Principal         │   │
│  │  Data → Column Masking + Row Filtering       │   │
│  │  Audit → Diagnostic Logs → Log Analytics     │   │
│  └─────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
```

---

## What to Do Next

1. **Complete the setup** following this guide top to bottom
2. **Add real users** to the groups you created
3. **Build your ingestion pipeline** — connect to your clinic's ERP system
4. **Set up Data Quality checks** — ensure bad data is caught at bronze layer
5. **Schedule automated jobs** — nightly data refresh using Databricks Workflows
6. **Engage a compliance consultant** — before going live with real patient data, get a privacy impact assessment done by an Australian privacy professional

---

*Guide created for Vaishnavi Avula — Greenfield Healthcare Startup, Australia — April 2026*
