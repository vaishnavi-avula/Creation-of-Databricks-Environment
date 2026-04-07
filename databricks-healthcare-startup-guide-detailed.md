# Complete Beginner's Guide: Setting Up Databricks for a Healthcare Startup in Australia
### Step-by-Step | No Prior Experience Required | Azure Free Trial

---

## Before You Start: Read This First

This guide assumes you have **never used Azure or Databricks before**. Every step is explained from scratch, including what each tool is, why we need it, and exactly where to click.

By the end of this guide, you will have:
- A working cloud data platform on Microsoft Azure
- A Databricks workspace where your team can process patient data
- A secure, compliant environment ready for Australian healthcare data

**Time required:** ~3-4 hours to complete everything for the first time

**What you need before starting:**
- A computer with internet access
- An email address (to create your Azure account)
- A credit card (required by Microsoft to verify identity — you will NOT be charged during the free trial)

---

## Table of Contents

1. [Understanding the Big Picture](#1-understanding-the-big-picture)
2. [What is Azure?](#2-what-is-azure)
3. [What is Databricks?](#3-what-is-databricks)
4. [Why Your Healthcare Startup Needs Both](#4-why-your-healthcare-startup-needs-both)
5. [Your Complete Architecture](#5-your-complete-architecture)
6. [Phase 1: Create Your Azure Account](#6-phase-1-create-your-azure-account)
7. [Phase 2: Set Up Your Resource Group](#7-phase-2-set-up-your-resource-group)
8. [Phase 3: Create Your Data Lake Storage](#8-phase-3-create-your-data-lake-storage)
9. [Phase 4: Create Your Key Vault (Password Manager)](#9-phase-4-create-your-key-vault)
10. [Phase 5: Create Your Databricks Workspace](#10-phase-5-create-your-databricks-workspace)
11. [Phase 6: Connect Key Vault to Databricks](#11-phase-6-connect-key-vault-to-databricks)
12. [Phase 7: Set Up Unity Catalog (Data Governance)](#12-phase-7-set-up-unity-catalog)
13. [Phase 8: Design and Create Your Clusters](#13-phase-8-design-and-create-your-clusters)
14. [Phase 9: Set Up Your Data Lakehouse Structure](#14-phase-9-set-up-your-data-lakehouse-structure)
15. [Phase 10: Build Your First ETL Pipeline](#15-phase-10-build-your-first-etl-pipeline)
16. [Phase 11: Set Up Real-time Streaming](#16-phase-11-set-up-real-time-streaming)
17. [Phase 12: Security and Compliance](#17-phase-12-security-and-compliance)
18. [Phase 13: Cost Management](#18-phase-13-cost-management)
19. [Your Free Trial Roadmap](#19-your-free-trial-roadmap)
20. [Glossary of Terms](#20-glossary-of-terms)

---

## 1. Understanding the Big Picture

### What Problem Are We Solving?

Imagine your healthcare startup collects data from multiple places:
- Patients fill in forms on your app
- Doctors send patient records from their clinic software
- Smartwatches send heart rate and blood oxygen data every second
- Your billing system exports CSV files every night

Without a proper system, this data ends up:
- In different formats (some JSON, some CSV, some database tables)
- In different places (some on servers, some in emails, some in Excel files)
- Accessible to everyone — including people who shouldn't see private patient data

This is a **compliance disaster** waiting to happen under Australia's Privacy Act.

### What We Are Building

We are building a **Data Lakehouse** — a central, secure, organised place where all your data lives and can be processed. Think of it like building a hospital for your data:

```
REAL HOSPITAL ANALOGY:

Emergency Department  =  Raw Data Ingestion (data arrives messy)
Triage               =  Bronze Layer (store everything as-is)
Treatment            =  Silver Layer (clean, validate, organise)
Patient Records Room  =  Gold Layer (ready to use, properly filed)
Research Department  =  ML Layer (scientists analyse patterns)
Security Desk        =  Unity Catalog (controls who can enter each room)
```

---

## 2. What is Azure?

**Azure is Microsoft's cloud platform.** Instead of buying physical servers and storing them in your office, you rent computing power and storage from Microsoft's data centres.

### Why use Azure instead of your own servers?

| Owning Servers | Using Azure |
|---|---|
| Buy hardware upfront (~$50,000+) | Pay only for what you use |
| Physical security you manage | Microsoft manages physical security |
| Data stored in your office | Data stored in Microsoft's Sydney data centre |
| You fix hardware when it breaks | Microsoft fixes it |
| Hard to scale up/down | Scale up in minutes |

### Azure for Australian Healthcare

Microsoft has data centres in **Sydney (Australia East)** and **Melbourne (Australia Southeast)**. When we choose Australia East, your patient data **physically stays in Australia** — this is a legal requirement under the Australian Privacy Act.

### Key Azure services we will use:

| Service | Simple Explanation | Real-World Analogy |
|---|---|---|
| **Azure Portal** | The website where you manage everything | Control panel / dashboard |
| **Resource Group** | A folder that groups related services together | A project folder on your desktop |
| **ADLS Gen2** | File storage for huge amounts of data | A very large, organised hard drive in the cloud |
| **Key Vault** | Secure storage for passwords and secrets | A digital safe/password manager |
| **Azure Active Directory** | User account management | Your company's HR system for IT access |
| **Event Hubs** | Receives streaming data in real-time | A post office that handles millions of letters/second |

---

## 3. What is Databricks?

**Databricks is a data processing platform** that runs on top of Azure. It gives your team a place to write code, process data, run machine learning models, and query data with SQL — all in one place.

### The Notebook Concept

The main way you work in Databricks is through **Notebooks** — think of them like Google Docs but for code. Multiple people can work in the same notebook, run Python or SQL code cell by cell, and see results immediately.

```
DATABRICKS NOTEBOOK EXAMPLE:

┌─────────────────────────────────────────────────────┐
│ Cell 1 (Python):                                    │
│   df = spark.read.format("delta")                   │
│      .load("/mnt/silver/patients")                  │
│   display(df)                                       │
│                          [Run ▶]                    │
├─────────────────────────────────────────────────────┤
│ Output:                                             │
│ patient_id | name    | age | postcode               │
│ P001       | [MASK]  | 34  | 2000                   │
│ P002       | [MASK]  | 67  | 3000                   │
└─────────────────────────────────────────────────────┘
```

### What is a Cluster?

A **cluster** is a group of computers (virtual machines in Azure) that Databricks uses to run your code. When you run a notebook, Databricks sends the work to the cluster to process it.

```
YOUR LAPTOP                    DATABRICKS CLUSTER
     │                              │
     │  "Process 500GB of           │
     │   patient records"  ─────►  [VM1] [VM2] [VM3] [VM4]
     │                              │
     │  Results sent back  ◄─────  Processed in parallel
     │                              │
     └──────────────────────────────┘
```

**Why multiple computers?** Because 500GB of data processed on one computer would take hours. Split it across 4 computers and it takes a quarter of the time.

### What is Apache Spark?

Databricks is built on top of **Apache Spark** — an open-source engine designed to process massive amounts of data quickly across many computers. You don't need to understand Spark deeply — Databricks makes it easy to use through Python and SQL.

### Key Databricks concepts:

| Concept | Simple Explanation |
|---|---|
| **Workspace** | Your team's Databricks environment — like an office building |
| **Cluster** | The computers that run your code |
| **Notebook** | A document where you write and run code |
| **Delta Lake** | A special way to store data that prevents corruption |
| **Delta Live Tables (DLT)** | An automated pipeline that moves data from raw to clean |
| **SQL Warehouse** | A fast database for running SQL queries and dashboards |
| **Unity Catalog** | Controls who can access which data |
| **MLflow** | Tracks and manages machine learning experiments |

---

## 4. Why Your Healthcare Startup Needs Both

### Your Team's Needs

| Team Member | What They Need | Azure Provides | Databricks Provides |
|---|---|---|---|
| Data Engineer | Store raw patient data, build pipelines | ADLS Gen2 (storage) | Delta Live Tables, notebooks |
| Data Engineer | Schedule automated jobs | — | Databricks Workflows |
| Data Scientist | Explore data, train ML models | — | ML Runtime, MLflow, notebooks |
| Data Platform Lead | Security, access control, governance | Azure AD, Key Vault | Unity Catalog |
| BI Analyst | SQL queries, Power BI dashboards | — | SQL Warehouse |

### Compliance Requirements (Australian Privacy Act)

| Requirement | How We Meet It |
|---|---|
| Data must stay in Australia | Azure Australia East (Sydney) |
| Audit trail of who accessed what | Databricks audit logging → Azure Monitor |
| Encryption of patient data | Azure-managed encryption at rest + TLS in transit |
| Access control on patient data | Unity Catalog column-level masking |
| Data retention for 7 years | ADLS Gen2 lifecycle policies |
| Ability to prove data lineage | Delta Lake time travel + DLT lineage |

---

## 5. Your Complete Architecture

Here is what we are building. Read through this before starting so you understand where each piece fits.

```
┌──────────────────────────────────────────────────────────────────────┐
│                    DATA SOURCES (Where data comes from)              │
│                                                                      │
│  [Clinic EHR/EMR]  [FHIR API]  [Wearable Devices]  [CSV Uploads]    │
└──────┬───────────────┬──────────────┬───────────────┬───────────────┘
       │               │              │               │
       │ (batch files) │ (API calls)  │ (real-time)   │ (manual)
       ▼               ▼              ▼               ▼
┌──────────────────────────────────────────────────────────────────────┐
│                    AZURE INGESTION LAYER                             │
│                                                                      │
│   [Azure Data Factory]              [Azure Event Hubs]              │
│   Picks up batch files              Receives real-time streams       │
└──────────────────────────┬───────────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────────────┐
│              AZURE DATA LAKE STORAGE GEN2 (Your Data Lake)           │
│                                                                      │
│  [bronze/]       [silver/]        [gold/]          [ml/]            │
│  Raw data        Clean data       Business data    ML features       │
│  as received     validated        aggregated        for models       │
└──────────────────────────┬───────────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────────────┐
│                    AZURE DATABRICKS WORKSPACE                        │
│                                                                      │
│  ┌────────────────┐  ┌──────────────┐  ┌────────────────────────┐  │
│  │  ETL Cluster   │  │ SQL Warehouse│  │   ML Cluster           │  │
│  │  (Pipelines)   │  │ (Analytics)  │  │   (Data Science)       │  │
│  └────────────────┘  └──────────────┘  └────────────────────────┘  │
│  ┌────────────────┐                                                  │
│  │Streaming Cluster│                                                 │
│  │(Real-time data)│                                                  │
│  └────────────────┘                                                  │
│                                                                      │
│  [Delta Live Tables]  [Unity Catalog]  [MLflow]  [Workflows]        │
└──────────────────────────┬───────────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────────────┐
│                    CONSUMPTION LAYER (Who uses the data)             │
│                                                                      │
│   [Power BI Dashboards]  [REST APIs]  [ML Model Endpoints]          │
└──────────────────────────────────────────────────────────────────────┘

SECURITY LAYER (runs across everything):
   [Azure Key Vault]  [Azure Active Directory]  [Audit Logs]
```

### The Medallion Architecture Explained

All data flows through 3 quality layers — called **Bronze, Silver, Gold**:

**Bronze (Raw)** — Store everything exactly as it arrived. Never change this.
```
Example: A CSV file from a clinic arrives with inconsistent date formats,
missing fields, and duplicates. Store it as-is in Bronze.
Why: If there's ever a legal dispute, you can prove exactly what data you received.
```

**Silver (Clean)** — Fix the issues. Validate, deduplicate, standardise.
```
Example: Fix date formats, remove duplicates, mask Medicare numbers,
flag records with missing required fields.
Why: Your data scientists and analysts work from here — it needs to be reliable.
```

**Gold (Business-ready)** — Aggregate and join for specific business use cases.
```
Example: Join patient records with their encounters and observations.
Create a "patient_summary" table with one row per patient.
Why: Power BI dashboards and reports work from here — fast, pre-joined queries.
```

---

## 6. Phase 1: Create Your Azure Account

### Step 1.1 — Sign Up for Azure Free Trial

1. Open your web browser and go to **portal.azure.com**
2. Click **"Start free"** or **"Try Azure for free"**
3. Sign in with a Microsoft account, or create one (use your work email)
4. You will be asked to:
   - Verify your identity with a phone number
   - Enter credit card details (Microsoft charges $1 to verify — refunded immediately)
   - Agree to the terms

**What you get for free:**
- $200 USD credit (approximately $310 AUD) valid for **30 days**
- 12 months of popular services free
- Always-free tier on 55+ services

> **Important:** Set a budget alert so you don't accidentally overspend. We'll cover this in Phase 13.

### Step 1.2 — Set Your Default Region

After signing in to the Azure Portal:

1. Click the **gear icon** (Settings) in the top right corner
2. Under **"Language + region"** → Set **Region** to **"Australia"**
3. Click **"Apply"**

This makes sure you always see prices in AUD and defaults are set to Australian regions.

### Step 1.3 — Note Your Subscription ID

1. In the Azure Portal, click **"Subscriptions"** in the left menu
   - If you don't see it, search "Subscriptions" in the top search bar
2. Click on your subscription name
3. On the Overview page, find **"Subscription ID"**
4. Copy and save this somewhere — you'll need it multiple times

```
Your Subscription ID: 2e4d86c9-3434-492e-8aa0-1510148509c9
                      (you already have this from earlier)
```

---

## 7. Phase 2: Set Up Your Resource Group

### What is a Resource Group?

Think of a Resource Group as a **project folder**. All the Azure services you create for your healthcare platform (storage, Databricks, Key Vault, etc.) go inside this folder. This makes it easy to:
- Find everything related to your project
- Control who has access to the whole project
- Delete everything at once when testing (delete the folder, everything inside is deleted)

### Step 2.1 — Create the Resource Group

**Via Azure Portal (recommended for beginners):**

1. In the Azure Portal, type **"Resource groups"** in the top search bar
2. Click **"Resource groups"** from the dropdown
3. Click the blue **"+ Create"** button
4. Fill in the form:

```
Subscription:    [Your subscription — should auto-fill]
Resource group:  rg-healthstartup-prod
Region:          Australia East
```

5. Click **"Review + create"**
6. Click **"Create"**

You will see a notification "Resource group created successfully" within a few seconds.

**Naming explained:**
- `rg` = resource group (prefix tells you what type it is)
- `healthstartup` = your company/project name
- `prod` = production environment

> **Naming Convention Rule:** We always use this pattern: `{type}-{project}-{environment}`
> This becomes important when you have multiple environments (dev, test, prod).

### Step 2.2 — Set a Budget Alert

Before creating anything expensive, set up a budget alert:

1. In the Azure Portal, search **"Cost Management + Billing"**
2. Click **"Budgets"** in the left menu
3. Click **"+ Add"**
4. Set:
   - Name: `budget-healthstartup-freetrial`
   - Amount: `$150 USD` (leaves buffer before your $200 credit runs out)
   - Alert at: 80% and 100%
   - Email: your email address
5. Click **"Create"**

Now Azure will email you when you've spent $120 and $150 — giving you warning before running out of credit.

---

## 8. Phase 3: Create Your Data Lake Storage

### What is ADLS Gen2?

**Azure Data Lake Storage Generation 2 (ADLS Gen2)** is where all your data lives. It's like a very large, organised hard drive in the cloud. For a healthcare startup processing 100GB–1TB/day, you need a storage system built for big data — regular Azure Blob Storage would work but ADLS Gen2 is:
- Optimised for big data workloads (much faster for Databricks to read)
- Supports folder-level permissions (important for PHI access control)
- Much cheaper per GB for large volumes

### Step 3.1 — Create the Storage Account

1. In the Azure Portal, search **"Storage accounts"** in the top bar
2. Click **"+ Create"**
3. Fill in the **Basics** tab:

```
Subscription:        [Your subscription]
Resource group:      rg-healthstartup-prod
Storage account name: adlshealthstartupprod
                      (no hyphens allowed in storage names)
Region:              Australia East
Performance:         Standard
Redundancy:          Locally-redundant storage (LRS)
                     [cheapest option — fine for free trial]
```

4. Click **"Next: Advanced"**

5. On the **Advanced** tab, find **"Data Lake Storage Gen2"** section:

```
Hierarchical namespace:  [✓] Enable
                         (THIS IS CRITICAL — makes it ADLS Gen2)
```

6. Also on Advanced tab, under **Security**:
```
Minimum TLS version:     TLS 1.2
                         (required for healthcare compliance)
```

7. Click **"Review + create"** → **"Create"**

Wait about 30 seconds for deployment to complete.

### Step 3.2 — Create Your Containers (Folders)

Containers in ADLS Gen2 are like top-level folders. We need 4:

1. Go to your newly created storage account
2. In the left menu, click **"Containers"** under Data storage
3. Click **"+ Container"** and create each one:

| Container Name | Access Level | Purpose |
|---|---|---|
| `bronze` | Private | Raw data as received |
| `silver` | Private | Cleaned and validated data |
| `gold` | Private | Business-ready aggregated data |
| `ml` | Private | Machine learning features |

For each container:
- Click **"+ Container"**
- Name: `bronze` (then repeat for others)
- Public access level: **Private** (no anonymous access — required for PHI)
- Click **"Create"**

### Step 3.3 — Note Your Storage Account Details

From the storage account Overview page, copy:
```
Storage account name:  adlshealthstartupprod
Primary endpoint (DFS): https://adlshealthstartupprod.dfs.core.windows.net/
```

Save these — you'll need them when connecting Databricks to storage.

---

## 9. Phase 4: Create Your Key Vault

### What is Azure Key Vault?

Key Vault is a **digital safe** for storing secrets — things like:
- Passwords and connection strings
- API keys
- Encryption keys

**Why not just store these in code or a config file?**

Imagine your notebook contains:
```python
# BAD - Never do this
storage_password = "MySecretPassword123"
```

If this notebook gets shared, committed to GitHub, or seen by the wrong person — your data is compromised. Key Vault means your code looks like:

```python
# GOOD - Password is fetched from the safe at runtime
storage_password = dbutils.secrets.get(scope="kv-healthstartup", key="storage-password")
```

No one reading your code can see the actual password.

### Step 4.1 — Create the Key Vault

1. Search **"Key vaults"** in the Azure Portal
2. Click **"+ Create"**
3. Fill in **Basics** tab:

```
Subscription:     [Your subscription]
Resource group:   rg-healthstartup-prod
Key vault name:   kv-healthstartup-prod
Region:           Australia East
Pricing tier:     Standard
```

4. Click **"Next: Access configuration"**

5. On the **Access configuration** tab — THIS IS CRITICAL:

```
Permission model:
  ( ) Vault access policy
  (●) Azure role-based access control (RBAC)   ← Select this one
```

**Why RBAC?** It integrates with Azure Active Directory, which means:
- You can use the same permission system as the rest of Azure
- Every access is logged (required for Privacy Act compliance)
- You can grant access to groups, not just individuals

6. Under **"Resource access"**:
```
[✓] Azure Virtual Machines for deployment
[✓] Azure Databricks          ← Enable this
```

7. Click **"Next: Networking"**:
```
Public access: Allow public access from all networks
(We'll restrict this later in production)
```

8. Click **"Review + create"** → **"Create"**

### Step 4.2 — Note Your Key Vault Details

From the Key Vault Overview page, copy:
```
Vault URI:  https://kv-healthstartup-prod.vault.azure.net/
Resource ID: (click "JSON View" in top right to find the full resource ID)
```

The Resource ID looks like:
```
/subscriptions/2e4d86c9-3434-492e-8aa0-1510148509c9/resourceGroups/rg-healthstartup-prod/providers/Microsoft.KeyVault/vaults/kv-healthstartup-prod
```

---

## 10. Phase 5: Create Your Databricks Workspace

### What is a Databricks Workspace?

A workspace is your team's **Databricks environment** — like an office building that contains:
- All your notebooks (where people write code)
- All your clusters (the computers that run code)
- All your jobs and pipelines
- All your data access settings

One workspace = one environment. You eventually want a separate workspace for development and production (we'll set that up later).

### Step 5.1 — Create the Workspace

1. Search **"Azure Databricks"** in the Azure Portal
2. Click **"+ Create"**
3. Fill in **Basics** tab:

```
Subscription:      [Your subscription]
Resource group:    rg-healthstartup-prod
Workspace name:    adb-healthstartup-prod
Region:            Australia East
Pricing tier:      Premium   ← CRITICAL: must be Premium, not Standard
```

**Why Premium?**

| Feature | Standard | Premium |
|---|---|---|
| Unity Catalog (data governance) | No | Yes |
| Table/column access control | No | Yes |
| Row-level security | No | Yes |
| Audit logging | Basic | Full |
| Cost | Cheaper | ~25% more |

For healthcare data with PHI, Premium is non-negotiable. The extra cost buys you the ability to control exactly who can see which columns of patient data.

4. Click **"Review + create"** → **"Create"**

Deployment takes **3-5 minutes** — longer than other resources.

### Step 5.2 — Open Your Databricks Workspace

1. Once deployed, click **"Go to resource"**
2. Click the blue **"Launch Workspace"** button
3. A new browser tab opens — this is your Databricks workspace

You'll see the Databricks home screen with a left-hand navigation bar. This is where your team will spend most of their time.

### Step 5.3 — Create a Personal Access Token

A Personal Access Token (PAT) is like a password that lets tools (like the Databricks CLI) connect to your workspace programmatically.

1. In Databricks, click your **username/profile icon** in the top right corner
2. Click **"User Settings"**
3. Click **"Developer"** in the left menu
4. Next to **"Access tokens"**, click **"Manage"**
5. Click **"Generate new token"**
6. Fill in:
   ```
   Comment:  cli-admin-token
   Lifetime:  90  (days)
   ```
7. Click **"Generate"**
8. **IMMEDIATELY copy the token** — it is shown only once
   ```
   Example: dapi1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p
   ```
9. Store this token in a safe place (we'll put it in Key Vault shortly)

### Step 5.4 — Install the Databricks CLI on Your Computer

The Databricks CLI (Command Line Interface) lets you run Databricks commands from your computer's terminal.

**Open a terminal** (on Windows: search "Command Prompt" or "PowerShell"):

```bash
# Install the Databricks CLI using Python's package manager
pip install databricks-cli

# Verify it installed correctly
databricks --version
# Should show: Version X.X.X
```

If `pip` is not found, you need to install Python first:
- Go to python.org → Download Python 3.11+ → Install it
- Then try `pip install databricks-cli` again

### Step 5.5 — Configure the CLI

```bash
# Run the configuration wizard
databricks configure --token
```

It will ask two questions:

```
Databricks Host (should begin with https://):
→ Type: https://adb-XXXXXXXXXXXXXXXX.X.azuredatabricks.net
  (find this URL in the Azure Portal on your Databricks workspace Overview page)

Token:
→ Paste the token you copied in Step 5.3
```

**Test that it works:**
```bash
databricks workspace ls /
# Should list folders in your workspace
# Output example:
#   /Shared
#   /Users
```

If you see folder names, the CLI is connected successfully.

---

## 11. Phase 6: Connect Key Vault to Databricks

This phase tells Databricks where to find secrets. It connects your Databricks workspace to your Key Vault so that notebooks can securely fetch passwords without ever seeing them in code.

### Step 6.1 — Find the Databricks Managed Identity

When Azure created your Databricks workspace, it automatically created a hidden **managed identity** — think of it as Databricks' own service account. We need to find this identity so we can give it permission to read from Key Vault.

**Via Azure Portal:**

1. In the search bar at the top, type the name of the **managed resource group** that Azure created:
   ```
   databricks-rg-adb-healthstartup-prod
   ```
   (It's similar to your resource group name but with `databricks-rg-` prefix)

2. If you can't find it by name, go to:
   - Azure Portal → **Resource groups** → Look for a group with `databricks-rg` in the name

3. Inside this resource group, look for a resource of type **"Managed Identity"**
   - It usually has a name like `dbmanagedidentity` or similar

4. Click on the Managed Identity resource

5. On the Overview page, find and copy the **"Object (principal) ID"**:
   ```
   Object (principal) ID:  xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
   ```
   Save this — you need it in the next step.

### Step 6.2 — Grant Databricks Permission to Read Key Vault

We need to give Databricks' managed identity two permissions on Key Vault:

**Permission 1: Key Vault Reader** — Allows Databricks to see that the Key Vault exists and read its properties

**Permission 2: Key Vault Secrets User** — Allows Databricks to read the actual secret values

**Assign Permission 1:**

1. Go to your Key Vault (`kv-healthstartup-prod`)
2. In the left menu, click **"Access control (IAM)"**
3. Click **"+ Add"** → **"Add role assignment"**
4. On the **Role** tab:
   - Search for `Key Vault Reader`
   - Click on it to select it
   - Click **"Next"**
5. On the **Members** tab:
   - "Assign access to": Select **"Managed identity"**
   - Click **"+ Select members"**
   - In the panel that opens on the right:
     - Subscription: your subscription
     - Managed identity: **"User-assigned managed identity"**
     - Search for your identity name
     - Click on it to select
     - Click **"Select"**
6. Click **"Review + assign"** → **"Review + assign"**

**Assign Permission 2:**

Repeat the same steps but this time:
- In Step 4, search for `Key Vault Secrets User` instead
- Everything else is the same

### Step 6.3 — Verify the Role Assignments

1. On your Key Vault, click **"Access control (IAM)"**
2. Click the **"Role assignments"** tab
3. You should see two rows for your Databricks managed identity:

```
Role                      Type              Principal
────────────────────────  ────────────────  ──────────────────────────
Key Vault Reader          Managed identity  [your identity name]
Key Vault Secrets User    Managed identity  [your identity name]
```

> **Wait 2-3 minutes** after this step. Azure needs time to apply these permissions across its systems. If you proceed immediately, you may get "Access Denied" errors.

### Step 6.4 — Create the Databricks Secret Scope

Now we create the "link" in Databricks that points to your Key Vault:

```bash
# Run this in your terminal (the Databricks CLI you set up in Phase 5)
databricks secrets create-scope \
  --scope kv-healthstartup \
  --scope-backend-type AZURE_KEYVAULT \
  --resource-id /subscriptions/2e4d86c9-3434-492e-8aa0-1510148509c9/resourceGroups/rg-healthstartup-prod/providers/Microsoft.KeyVault/vaults/kv-healthstartup-prod \
  --dns-name https://kv-healthstartup-prod.vault.azure.net/
```

**Command breakdown:**
- `--scope kv-healthstartup` → The nickname Databricks will use for this Key Vault
- `--scope-backend-type AZURE_KEYVAULT` → Tells Databricks the secrets are in Azure Key Vault
- `--resource-id ...` → The full Azure address of your Key Vault (note: uses your actual subscription ID)
- `--dns-name ...` → The web address of your Key Vault

**Verify it worked:**
```bash
databricks secrets list-scopes
```

Expected output:
```
Name              Backend Type
────────────────  ──────────────
kv-healthstartup  AZURE_KEYVAULT
```

### Step 6.5 — Add Your First Secret and Test It

**Add the storage account key to Key Vault:**

First, get your storage account key:
1. Go to your storage account (`adlshealthstartupprod`) in the Azure Portal
2. In the left menu, click **"Access keys"** under Security + networking
3. Click **"Show"** next to key1
4. Copy the **Key** value (a long string of letters and numbers)

Now add it to Key Vault:
1. Go to your Key Vault in the Azure Portal
2. Click **"Secrets"** in the left menu
3. Click **"+ Generate/Import"**
4. Fill in:
   ```
   Upload options:  Manual
   Name:            adls-storage-key
   Secret value:    [paste the storage key you just copied]
   ```
5. Click **"Create"**

**Test it in Databricks:**

1. Open your Databricks workspace
2. Click **"+ New"** → **"Notebook"**
3. Name it `test-key-vault`, language: Python
4. In the first cell, type:

```python
# List available secret scopes
display(dbutils.secrets.listScopes())
```

Click the **Run** button (▶) or press **Shift + Enter**

Expected output:
```
name              backend_type
kv-healthstartup  AZURE_KEYVAULT
```

5. In a new cell:

```python
# Retrieve the secret — value will show as [REDACTED] for security
key = dbutils.secrets.get(scope="kv-healthstartup", key="adls-storage-key")
print(f"Secret retrieved successfully. Length: {len(key)} characters")
```

Expected output:
```
Secret retrieved successfully. Length: 88 characters
```

If you see the length printed (not zero), **Key Vault is connected and working correctly.**

---

## 12. Phase 7: Set Up Unity Catalog

### What is Unity Catalog?

Unity Catalog is Databricks' **data governance system**. Governance means controlling:
- Who can see which tables
- Who can see which columns within a table
- What operations they can perform (read only? read and write?)

For a healthcare startup, this is critical because:
- A BI analyst should be able to query patient statistics but NOT see individual Medicare numbers
- A data scientist should access de-identified data but NOT raw PHI
- Audit logs must show every time someone accessed patient data

### Step 7.1 — Access the Databricks Account Console

The Account Console is different from the Workspace. It's the top-level management interface.

1. In your Databricks workspace, click your **profile icon** (top right)
2. Click **"Manage Account"** — this opens the Account Console in a new tab

### Step 7.2 — Create a Unity Catalog Metastore

A metastore is the central registry for all your data assets (tables, schemas, catalogs).

1. In the Account Console, click **"Data"** in the left menu
2. Click **"+ Create metastore"**
3. Fill in:
   ```
   Name:     healthstartup-metastore
   Region:   australiaeast
   ADLS Gen2 path: abfss://gold@adlshealthstartupprod.dfs.core.windows.net/unity-catalog/
   ```
4. Click **"Create"**

### Step 7.3 — Assign the Metastore to Your Workspace

1. After creating the metastore, click **"Assign to workspace"**
2. Select your workspace (`adb-healthstartup-prod`)
3. Click **"Assign"**

### Step 7.4 — Create Your Catalog Structure

Back in your Databricks workspace (not Account Console):

1. Click **"Catalog"** in the left navigation bar
2. Click **"+ Add"** → **"Add a catalog"**
3. Create the main catalog:
   ```
   Catalog name:  healthstartup
   ```
4. Inside the catalog, create schemas (databases):

```sql
-- Run this in a Databricks notebook

-- Bronze database (raw data)
CREATE SCHEMA IF NOT EXISTS healthstartup.bronze_db
COMMENT 'Raw, unmodified data as received from source systems';

-- Silver database (clean data)
CREATE SCHEMA IF NOT EXISTS healthstartup.silver_db
COMMENT 'Validated, deduplicated, and standardised patient data';

-- Gold database (business-ready data)
CREATE SCHEMA IF NOT EXISTS healthstartup.gold_db
COMMENT 'Aggregated business-ready data for reporting and dashboards';

-- ML database (feature store)
CREATE SCHEMA IF NOT EXISTS healthstartup.ml_db
COMMENT 'Feature engineering outputs for machine learning models';
```

### Step 7.5 — Set Up Access Control

Create groups in Azure Active Directory and assign Unity Catalog permissions:

**Create Azure AD Groups (in Azure Portal):**

1. In Azure Portal, search **"Azure Active Directory"**
2. Click **"Groups"** → **"+ New group"**
3. Create these 4 groups:

| Group Name | Members | Description |
|---|---|---|
| `grp-databricks-admins` | Data Platform Lead | Full admin access |
| `grp-databricks-engineers` | 2 Data Engineers | Create clusters, manage pipelines |
| `grp-databricks-scientists` | Data Scientist | Interactive clusters, ML features |
| `grp-databricks-analysts` | BI Analysts | SQL Warehouse read-only access |

**Assign Unity Catalog permissions (in Databricks notebook):**

```sql
-- Give engineers access to bronze and silver (where they do their work)
GRANT USE CATALOG ON CATALOG healthstartup TO `grp-databricks-engineers`;
GRANT USE SCHEMA ON SCHEMA healthstartup.bronze_db TO `grp-databricks-engineers`;
GRANT USE SCHEMA ON SCHEMA healthstartup.silver_db TO `grp-databricks-engineers`;
GRANT SELECT, MODIFY ON SCHEMA healthstartup.bronze_db TO `grp-databricks-engineers`;
GRANT SELECT, MODIFY ON SCHEMA healthstartup.silver_db TO `grp-databricks-engineers`;

-- Give data scientists read access to silver and full access to ML
GRANT USE CATALOG ON CATALOG healthstartup TO `grp-databricks-scientists`;
GRANT USE SCHEMA, SELECT ON SCHEMA healthstartup.silver_db TO `grp-databricks-scientists`;
GRANT USE SCHEMA, SELECT, MODIFY ON SCHEMA healthstartup.ml_db TO `grp-databricks-scientists`;

-- Give analysts read-only access to gold (no PHI here)
GRANT USE CATALOG ON CATALOG healthstartup TO `grp-databricks-analysts`;
GRANT USE SCHEMA, SELECT ON SCHEMA healthstartup.gold_db TO `grp-databricks-analysts`;
```

---

## 13. Phase 8: Design and Create Your Clusters

### Understanding the Cluster Types

We create **4 separate clusters** for different purposes. This is better than one big shared cluster because:
- Each cluster is sized correctly for its workload (no paying for more than you need)
- A bug in one team's work doesn't slow down another team
- You can apply different security policies to each cluster

```
PURPOSE-BUILT CLUSTER DESIGN:

Data Engineers         ──►  ETL Job Cluster      (automated pipelines)
BI Analysts            ──►  SQL Warehouse         (SQL queries, Power BI)
Data Scientist         ──►  ML Interactive        (notebooks, model training)
Streaming Data         ──►  Streaming Cluster     (24/7 real-time processing)
```

### Cluster 1: ETL Job Cluster

**What it does:** Runs your data pipelines — moving data from Bronze to Silver to Gold.

**Key characteristic:** This cluster **does not stay running**. It starts when a job begins and terminates when the job finishes. You only pay for the time it's actually processing data.

**Create it in Databricks:**

1. In Databricks, click **"Compute"** in the left menu
2. Click **"+ Create compute"**
3. Fill in:

```
Cluster name:      etl-job-cluster
Policy:            Unrestricted (we'll add policies later)
Cluster mode:      Multi node

Databricks runtime version:
   Select: 14.x LTS (Scala 2.12, Spark 3.5.0)
   Why LTS? LTS = Long Term Support. Microsoft guarantees security patches
   for 2+ years. Use LTS for production clusters.

Worker type:       Standard_DS3_v2
   Specs: 4 cores, 14 GB RAM per worker
   Why this size? Good balance for medium-volume ETL. Not too small
   (bottleneck), not too large (wasteful).

Min workers:       2
Max workers:       6
   Why autoscaling? During quiet hours (midnight), 2 workers is enough.
   During peak ingestion (9am data load), it scales to 6 automatically.

Enable autoscaling: [✓] Yes

Auto termination:  [✓] Terminate after 10 minutes of inactivity
   Why: If someone accidentally starts this cluster manually and forgets
   to stop it, it auto-stops after 10 minutes. Saves cost.
```

4. Click **"Create compute"**

> **Spot Instances (Save 60-80% on dev/test):**
> Under "Advanced options" → "Spot instances" → Enable for development.
> Spot instances are unused Azure capacity sold cheaply. Azure can reclaim them
> with 30-second notice. Fine for retryable jobs, NOT for production pipelines.

**Monthly cost estimate:** ~$400-600 AUD (running 4-6 hours/day on production workloads)

---

### Cluster 2: SQL Warehouse

**What it does:** Handles SQL queries from analysts and Power BI dashboards.

**Key characteristic:** Scales to zero when nobody is using it. A SQL Warehouse is different from a regular cluster — it's optimised for many simultaneous SQL queries.

1. In Databricks, click **"SQL Warehouses"** in the left menu
   (Note: this is under the SQL section, not Compute)
2. Click **"+ Create SQL Warehouse"**
3. Fill in:

```
Name:      sql-warehouse-analytics
Size:      Small
   Why Small? Your team has ~5 analysts. Small handles up to 10 concurrent
   queries. You can upgrade to Medium if queries are slow.

Auto stop:      10 minutes
   Why 10 minutes? Power BI may trigger a query at 9am, finish, then
   no queries until 10am. 10-minute auto-stop ensures the warehouse
   shuts down and you stop paying after 10 minutes of silence.

Type:           Serverless
   Serverless SQL Warehouses scale to zero automatically — no minimum
   running cost when idle.
```

4. Click **"Create"**

**Monthly cost estimate:** ~$200-400 AUD (usage-based — you only pay when queries run)

---

### Cluster 3: ML Interactive Cluster

**What it does:** Your data scientist uses this for exploring data, training machine learning models, and testing hypotheses in notebooks.

**Key characteristic:** This cluster stays running while the scientist is working (unlike job clusters). It has the ML Runtime pre-installed with all the data science libraries.

1. In Databricks **"Compute"** → **"+ Create compute"**
2. Fill in:

```
Cluster name:      ml-interactive-ds

Databricks runtime version:
   Select: 14.x LTS ML (includes Machine Learning libraries)
   This runtime has pre-installed: scikit-learn, TensorFlow, PyTorch,
   XGBoost, MLflow, pandas, numpy, matplotlib — everything a data
   scientist needs without manual installation.

Worker type:       Standard_DS4_v2
   Specs: 8 cores, 28 GB RAM per worker
   Why bigger than ETL? ML models need more memory. Loading a
   patient feature matrix of 1M rows into memory requires RAM.

Min workers:       1
Max workers:       3

Auto termination:  60 minutes
   Why 60 minutes (not 10)? Data scientists often run a cell, then spend
   20 minutes thinking/writing before running the next cell. A 10-minute
   timeout would keep shutting down mid-experiment. 60 minutes balances
   cost with usability.

Enable autoscaling: [✓] Yes
```

3. Click **"Create compute"**

**Monthly cost estimate:** ~$300-500 AUD (assuming 6-8 hours of active daily use)

---

### Cluster 4: Streaming Cluster

**What it does:** Runs 24/7 to process data arriving in real-time from wearable devices and health sensors via Azure Event Hubs.

**Key characteristic:** This cluster **never terminates** — streaming is continuous. It is also on **On-demand instances** (not Spot) because Azure reclaiming Spot instances would break your stream.

1. In Databricks **"Compute"** → **"+ Create compute"**
2. Fill in:

```
Cluster name:      streaming-wearables

Databricks runtime version:
   Select: 14.x LTS (standard, not ML)

Cluster mode:      Fixed size (NOT autoscaling)
   Why fixed? Streaming needs predictable, stable resources. Autoscaling
   can cause temporary unavailability while scaling up/down, which would
   cause data loss in a stream.

Worker type:       Standard_DS3_v2

Workers:           2
   Why fixed at 2? At your data volume (medium), 2 workers can handle
   the stream comfortably. For wearable data at 100-500 devices,
   2 workers is plenty.

Auto termination:  Off
   Why off? The stream must never stop — stopping it means losing
   real-time data. You manually stop it only for maintenance.

Spot instances:    No
   Why not? Azure reclaims Spot instances with 30-second notice.
   Your stream would fail. Always use On-demand for streaming.
```

3. Click **"Create compute"**

**Monthly cost estimate:** ~$500-800 AUD (24/7 operation)

---

### Cost Summary

| Cluster | Monthly Estimate (AUD) | When it runs |
|---|---|---|
| ETL Job Cluster | $400-600 | 4-6 hours/day |
| SQL Warehouse | $200-400 | Only when queried |
| ML Interactive | $300-500 | 6-8 hours/day |
| Streaming Cluster | $500-800 | 24/7 |
| ADLS Gen2 Storage (1TB) | $50-80 | Always |
| **Total** | **$1,450-2,380** | |

> **Free Trial tip:** During the trial, only run the ETL cluster and SQL Warehouse for testing. Do not start the streaming cluster 24/7 — test it briefly. Your $310 AUD credit will last ~2 weeks if you're careful.

---

## 14. Phase 9: Set Up Your Data Lakehouse Structure

### Connecting Databricks to ADLS Gen2

Before you can read or write data, Databricks needs permission to access your storage account.

**Step 9.1 — Mount ADLS Gen2 in Databricks**

Open a new notebook in Databricks and run:

```python
# First, store your storage account name as a variable
storage_account = "adlshealthstartupprod"

# Configure Databricks to authenticate to ADLS using the Key Vault secret
configs = {
    "fs.azure.account.auth.type": "OAuth",
    "fs.azure.account.oauth.provider.type":
        "org.apache.hadoop.fs.azurebfs.oauth2.ClientCredsTokenProvider",
    "fs.azure.account.oauth2.client.id":
        dbutils.secrets.get("kv-healthstartup", "sp-client-id"),
    "fs.azure.account.oauth2.client.secret":
        dbutils.secrets.get("kv-healthstartup", "sp-client-secret"),
    "fs.azure.account.oauth2.client.endpoint":
        f"https://login.microsoftonline.com/{dbutils.secrets.get('kv-healthstartup', 'tenant-id')}/oauth2/token"
}

# Mount each container as a drive in Databricks
for container in ["bronze", "silver", "gold", "ml"]:
    dbutils.fs.mount(
        source=f"abfss://{container}@{storage_account}.dfs.core.windows.net/",
        mount_point=f"/mnt/{container}",
        extra_configs=configs
    )
    print(f"Mounted /mnt/{container} successfully")
```

After running this, your storage containers are available as:
```
/mnt/bronze/    → points to your bronze container
/mnt/silver/    → points to your silver container
/mnt/gold/      → points to your gold container
/mnt/ml/        → points to your ml container
```

**Step 9.2 — Create Your First Delta Table**

Let's create a sample patient table to test everything is working. Delta tables are stored as files in ADLS but accessed as structured tables in Databricks.

```python
from pyspark.sql.types import StructType, StructField, StringType, DateType, TimestampType
from pyspark.sql import Row
from datetime import date, datetime

# --- Step 1: Define the schema (structure of the table) ---
# In healthcare, we ALWAYS define schemas explicitly.
# Why? If a source system sends bad data (e.g., a number where a date should be),
# Spark will reject it rather than silently storing garbage.

patient_schema = StructType([
    StructField("patient_id",      StringType(),    nullable=False),  # Cannot be empty
    StructField("given_name",      StringType(),    nullable=True),
    StructField("family_name",     StringType(),    nullable=True),
    StructField("date_of_birth",   DateType(),      nullable=True),
    StructField("gender",          StringType(),    nullable=True),
    StructField("medicare_number", StringType(),    nullable=True),   # Australian Medicare
    StructField("postcode",        StringType(),    nullable=True),
    StructField("ingested_at",     TimestampType(), nullable=False),  # When we received it
    StructField("source_system",   StringType(),    nullable=False)   # Where it came from
])

# --- Step 2: Create sample data (in production this comes from FHIR/HL7) ---
sample_patients = [
    Row(patient_id="P001", given_name="Jane", family_name="Smith",
        date_of_birth=date(1985, 3, 15), gender="F",
        medicare_number="2123456701", postcode="2000",
        ingested_at=datetime.now(), source_system="clinic-erp"),
    Row(patient_id="P002", given_name="John", family_name="Doe",
        date_of_birth=date(1962, 7, 22), gender="M",
        medicare_number="3987654302", postcode="3000",
        ingested_at=datetime.now(), source_system="clinic-erp"),
]

df = spark.createDataFrame(sample_patients, schema=patient_schema)

# --- Step 3: Write to Bronze layer as a Delta table ---
df.write \
    .format("delta") \
    .mode("append") \
    .option("mergeSchema", "false") \
    .save("/mnt/bronze/patients/")

print("Bronze patient table created successfully!")

# --- Step 4: Register it in Unity Catalog ---
spark.sql("""
    CREATE TABLE IF NOT EXISTS healthstartup.bronze_db.patients
    USING DELTA
    LOCATION '/mnt/bronze/patients/'
""")

print("Table registered in Unity Catalog!")
```

**Step 9.3 — Verify the Table**

```sql
-- In a new notebook cell using SQL
SELECT * FROM healthstartup.bronze_db.patients
```

You should see your 2 sample patient rows.

---

## 15. Phase 10: Build Your First ETL Pipeline

### What is ETL?

ETL stands for **Extract, Transform, Load**:
- **Extract:** Pull data from a source (a CSV file, an API, a database)
- **Transform:** Clean it, validate it, change its format, join it with other data
- **Load:** Write the result to a destination (your Silver or Gold Delta table)

### Using Delta Live Tables (DLT)

Delta Live Tables is Databricks' framework for building reliable data pipelines. Instead of writing complex Spark code with error handling, you write simple Python functions and DLT handles the rest.

**Create a DLT Pipeline:**

1. In Databricks, click **"Delta Live Tables"** in the left menu
2. Click **"Create pipeline"**
3. Fill in:
   ```
   Pipeline name:        bronze-to-silver-patients
   Product edition:      Core
   Pipeline mode:        Triggered (runs on schedule, not continuously)
   Source code:          [we'll add notebooks below]
   Destination:          Unity Catalog → healthstartup → silver_db
   Cluster:              Use existing cluster → etl-job-cluster
   ```

**Create the pipeline notebook:**

1. Create a new notebook: `pipelines/bronze_to_silver`
2. Add this code:

```python
import dlt
from pyspark.sql.functions import col, current_timestamp, sha2, upper, trim, when, isnan

# ═══════════════════════════════════════════════════════════════
# BRONZE TABLE: Raw data as received
# This table just reads from the incoming files — no changes made
# ═══════════════════════════════════════════════════════════════

@dlt.table(
    name="bronze_patients",
    comment="Raw patient records as received from source systems. Never modify this data.",
    table_properties={
        "quality": "bronze",
        "layer": "raw"
    }
)
def bronze_patients():
    """
    Auto Loader reads new files from ADLS as they arrive.
    cloudFiles.format = "json" because FHIR sends JSON.
    cloudFiles.schemaLocation = where to store the detected schema.
    """
    return (
        spark.readStream
            .format("cloudFiles")
            .option("cloudFiles.format", "json")
            .option("cloudFiles.schemaLocation", "/mnt/bronze/_checkpoints/patients_schema")
            .load("/mnt/bronze/fhir-incoming/patients/")
    )


# ═══════════════════════════════════════════════════════════════
# SILVER TABLE: Cleaned and validated data
# Fixes issues from Bronze, applies data quality rules
# ═══════════════════════════════════════════════════════════════

# Data quality rules: these expectations DROP rows that fail the check
# This protects Silver from bad data
@dlt.expect_or_drop("patient_id_not_null", "patient_id IS NOT NULL")
@dlt.expect_or_drop("valid_date_of_birth",  "date_of_birth <= current_date()")
@dlt.expect_or_drop("valid_gender",         "gender IN ('M', 'F', 'O', 'U')")
@dlt.table(
    name="silver_patients",
    comment="Validated and pseudonymised patient records. Medicare numbers removed.",
    table_properties={
        "quality": "silver",
        "layer": "cleansed",
        "contains_phi": "true"    # Tag that this table has sensitive data
    }
)
def silver_patients():
    return (
        dlt.read_stream("bronze_patients")

            # --- Pseudonymise: replace real patient_id with a hash ---
            # Why? The real patient_id might be a Medicare number or MRN.
            # The hash is one-way — you can track the patient across tables
            # but you can't reverse it back to their real ID.
            .withColumn(
                "patient_id_hash",
                sha2(col("patient_id"), 256)    # SHA-256 hash — industry standard
            )

            # --- Remove direct identifiers ---
            # Medicare number is direct PHI — analysts don't need it
            .drop("medicare_number")
            .drop("given_name")      # Name is PHI — not needed for analytics
            .drop("family_name")

            # --- Standardise fields ---
            .withColumn("gender", upper(trim(col("gender"))))   # "f" → "F", " M " → "M"
            .withColumn("postcode", trim(col("postcode")))      # Remove accidental spaces

            # --- Add processing metadata ---
            .withColumn("silver_processed_at", current_timestamp())

            # --- Drop the raw patient_id — only keep the hash ---
            .drop("patient_id")
    )
```

3. Add this notebook to your DLT pipeline
4. Click **"Start"** to run it

**What happens when the pipeline runs:**
```
Files arrive in /mnt/bronze/fhir-incoming/patients/
    │
    ▼
Auto Loader detects new files → creates bronze_patients
    │
    ▼
DLT runs quality checks:
    - Row with NULL patient_id? → DROPPED (goes to quarantine)
    - Row with future birth date? → DROPPED
    - Row with valid data? → PASSES
    │
    ▼
Pseudonymisation: patient_id → sha256 hash
Medicare number, names → REMOVED
    │
    ▼
silver_patients table updated
```

---

## 16. Phase 11: Set Up Real-time Streaming

### What is Streaming Data?

Streaming data arrives continuously — second by second, rather than in batches. In healthcare, this is typically:
- Heart rate from a smartwatch: every 1-5 seconds
- Blood oxygen (SpO2) from a pulse oximeter: every second
- Blood pressure from a connected cuff: every few minutes
- Hospital patient monitor: multiple readings per second

### Step 11.1 — Create Azure Event Hubs

Azure Event Hubs is a service that can receive millions of messages per second from devices and hold them briefly so Databricks can process them.

**Think of it like:** A high-speed conveyor belt that receives packages (device readings) and delivers them to a warehouse (Databricks) for processing.

1. In Azure Portal, search **"Event Hubs"**
2. Click **"+ Create"**
3. Fill in:
   ```
   Subscription:     [Your subscription]
   Resource group:   rg-healthstartup-prod
   Namespace name:   evhns-healthstartup-prod
   Location:         Australia East
   Pricing tier:     Standard
   Throughput units: 1 (handles ~1MB/sec — enough for initial startup)
   ```
4. Click **"Review + create"** → **"Create"**

5. After creation, open the namespace → **"+ Event Hub"**:
   ```
   Name:               evh-wearables
   Partition count:    4
   Message retention:  1 day
   ```

### Step 11.2 — Get the Event Hub Connection String

1. In your Event Hub namespace, click **"Shared access policies"**
2. Click **"RootManageSharedAccessKey"**
3. Copy the **"Connection string–primary key"**
4. Add it to Key Vault:
   - Go to Key Vault → Secrets → **"+ Generate/Import"**
   - Name: `eventhub-connection-string`
   - Value: [paste the connection string]
   - Click **"Create"**

### Step 11.3 — Write the Streaming Code in Databricks

Create a new notebook: `streaming/wearables-ingestion`

```python
from pyspark.sql.functions import from_json, col, current_timestamp
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType, TimestampType

# ─────────────────────────────────────────────
# STEP 1: Define what data we expect from devices
# ─────────────────────────────────────────────
device_schema = StructType([
    StructField("device_id",       StringType(),   nullable=False),
    StructField("patient_id_hash", StringType(),   nullable=False),  # Already hashed at device
    StructField("heart_rate",      IntegerType(),  nullable=True),   # BPM
    StructField("spo2",            DoubleType(),   nullable=True),   # Blood oxygen %
    StructField("timestamp",       TimestampType(),nullable=False),  # When reading was taken
    StructField("device_type",     StringType(),   nullable=True),   # e.g. "smartwatch", "pulse_ox"
])

# ─────────────────────────────────────────────
# STEP 2: Connect to Event Hubs and start reading
# ─────────────────────────────────────────────
connection_string = dbutils.secrets.get(
    scope="kv-healthstartup",
    key="eventhub-connection-string"
)

# Encrypt the connection string (required by the Event Hubs connector)
encrypted_conn = sc._jvm.org.apache.spark.eventhubs.EventHubsUtils.encrypt(connection_string)

# Start reading the stream
df_raw_stream = (
    spark.readStream
        .format("eventhubs")
        .option("eventhubs.connectionString", encrypted_conn)
        .load()
)

# The data arrives as raw bytes — convert to string first
df_string = df_raw_stream.select(
    col("body").cast("string").alias("raw_payload"),
    col("enqueuedTime").alias("received_at")
)

# ─────────────────────────────────────────────
# STEP 3: Parse the JSON payload
# ─────────────────────────────────────────────
df_parsed = df_string.select(
    from_json(col("raw_payload"), device_schema).alias("data"),
    col("received_at")
).select("data.*", "received_at")

# ─────────────────────────────────────────────
# STEP 4: Add quality flags (don't drop — flag for review)
# Heart rate outside 30-250 BPM is likely a sensor error
# SpO2 outside 70-100% is either critical or a sensor error
# ─────────────────────────────────────────────
from pyspark.sql.functions import when

df_with_flags = df_parsed.withColumn(
    "heart_rate_flag",
    when((col("heart_rate") < 30) | (col("heart_rate") > 250), "SUSPECT")
    .otherwise("OK")
).withColumn(
    "spo2_flag",
    when((col("spo2") < 70) | (col("spo2") > 100), "SUSPECT")
    .otherwise("OK")
).withColumn("ingested_at", current_timestamp())

# ─────────────────────────────────────────────
# STEP 5: Write to Bronze Delta table continuously
# ─────────────────────────────────────────────
query = (
    df_with_flags
        .writeStream
        .format("delta")
        .option("checkpointLocation", "/mnt/bronze/_checkpoints/wearables/")
        .outputMode("append")
        .start("/mnt/bronze/wearables/")
)

print("Streaming pipeline started. Listening for wearable data...")
print(f"Stream status: {query.status}")
```

**Register as a Delta table:**
```sql
CREATE TABLE IF NOT EXISTS healthstartup.bronze_db.wearable_readings
USING DELTA
LOCATION '/mnt/bronze/wearables/'
COMMENT 'Real-time readings from patient wearable devices. Refreshes continuously.'
```

---

## 17. Phase 12: Security and Compliance

### Australian Privacy Act Requirements Checklist

| Requirement | What to Do | Status |
|---|---|---|
| Encryption at rest | ✓ ADLS Gen2 encrypts by default | Done |
| Encryption in transit | ✓ TLS 1.2 set on storage account | Done |
| Access control on PHI | Set up in next steps | Pending |
| Audit logging | Set up in next steps | Pending |
| Data retention (7 years) | Set up in next steps | Pending |
| Incident response plan | Document and test | Pending |

### Step 12.1 — Column-Level Security (PHI Masking)

Even in the Silver layer, some columns still have sensitive data. Unity Catalog lets you mask a column so different users see different things:

```sql
-- When a regular analyst runs:  SELECT * FROM silver_db.patients
-- They see:  postcode=2000, patient_id_hash=abc123..., date_of_birth=XXXX-XX-XX
-- When an admin runs the same query, they see the real date_of_birth

-- Create a masking policy for date of birth
CREATE FUNCTION healthstartup.silver_db.mask_dob(dob DATE)
    RETURN CASE
        WHEN IS_ACCOUNT_GROUP_MEMBER('grp-databricks-admins')
          OR IS_ACCOUNT_GROUP_MEMBER('grp-databricks-engineers')
        THEN CAST(dob AS STRING)          -- Admins/engineers see real DOB
        ELSE 'XXXX-XX-XX'                 -- Analysts see masked DOB
    END;

-- Apply the mask to the date_of_birth column
ALTER TABLE healthstartup.silver_db.patients
    ALTER COLUMN date_of_birth
    SET MASK healthstartup.silver_db.mask_dob;
```

### Step 12.2 — Enable Audit Logging

Audit logging records every action taken in Databricks: who logged in, who ran which query, who accessed which table.

**Create a Log Analytics Workspace:**

1. In Azure Portal, search **"Log Analytics workspaces"**
2. Click **"+ Create"**
3. Fill in:
   ```
   Subscription:     [Your subscription]
   Resource group:   rg-healthstartup-prod
   Name:             law-healthstartup-audit
   Region:           Australia East
   ```
4. Click **"Review + create"** → **"Create"**
5. Once created, go to **"Usage and estimated costs"** → **"Data Retention"**
6. Set retention to **2557 days (7 years)** — required by Australian health records law

**Connect Databricks to Log Analytics:**

1. In Azure Portal, go to your Databricks workspace
2. Click **"Diagnostic settings"** in the left menu
3. Click **"+ Add diagnostic setting"**
4. Fill in:
   ```
   Name: send-to-log-analytics

   Logs to capture (check all):
   [✓] accounts
   [✓] clusters
   [✓] dbfs
   [✓] instancePools
   [✓] jobs
   [✓] notebook
   [✓] secrets
   [✓] sqlPermissions
   [✓] workspace

   Destination:
   [✓] Send to Log Analytics workspace
   Subscription: [your subscription]
   Log Analytics workspace: law-healthstartup-audit
   ```
5. Click **"Save"**

From now on, every action in Databricks is logged and retained for 7 years.

### Step 12.3 — Set Up Data Retention Policy on ADLS Gen2

1. Go to your storage account in Azure Portal
2. Click **"Lifecycle management"** in the left menu
3. Click **"+ Add a rule"**
4. Fill in:
   ```
   Rule name:        retain-7-years
   Rule scope:       Apply rule to all blobs in your storage account
   Blob type:        Block blobs
   ```
5. Under **"Base blobs"** tab:
   ```
   If: base blobs were last modified → More than 2557 days ago
   Then: Delete the blob
   ```
6. Click **"Add"**

This automatically deletes data older than 7 years, keeping you compliant without manual cleanup.

---

## 18. Phase 13: Cost Management

### Setting Up Azure Cost Alerts

1. In Azure Portal, search **"Cost Management"**
2. Click **"Budgets"** → **"+ Add"**
3. Create two budgets:

**Budget 1 — Free Trial Warning:**
```
Name:           freetrial-warning
Reset period:   Monthly
Amount:         $140 USD
Alert at 80%:   $112 USD → email you
Alert at 100%:  $140 USD → email you
```

**Budget 2 — Production Monthly Budget:**
```
Name:           monthly-production
Reset period:   Monthly
Amount:         $1,800 AUD
Alert at 80%:   Email team
Alert at 100%:  Email team
```

### Daily Cost-Saving Habits

**For Data Engineers:**
```python
# At end of each day — list running clusters and stop any that are idle
display(dbutils.fs.ls("/"))  # Just to check workspace is accessible

# In Databricks UI: Compute → Check each cluster
# If "Status = Running" and you're done → Click "Terminate"
```

**For Data Scientist:**
- Set a calendar reminder at end of each day: "Stop Databricks cluster"
- The 60-minute auto-terminate is a backup, not a primary strategy

**For the Platform Lead — Weekly Cost Review:**
1. Azure Portal → Cost Management → **Cost analysis**
2. Group by: **"Service name"**
3. Look for anything unexpectedly high
4. Common culprits: clusters left running, SQL Warehouse not auto-stopping

### Cluster Auto-Termination Reminder

A cluster left running overnight can cost:
```
Standard_DS4_v2 × 2 workers = ~$0.50/DBU × 4 DBUs/hr = $2 USD/hour
8 hours overnight = $16 USD = ~$25 AUD... every night
```

Always terminate interactive clusters at end of day.

---

## 19. Your Free Trial Roadmap

Follow this plan to make the most of your $310 AUD credit:

### Week 1 — Foundation
- [ ] Create Azure account and note subscription ID
- [ ] Create resource group `rg-healthstartup-prod`
- [ ] Create ADLS Gen2 storage account with 4 containers
- [ ] Create Key Vault with RBAC enabled
- [ ] Create Databricks workspace (Premium)
- [ ] Install Databricks CLI and configure it
- [ ] Connect Key Vault to Databricks (secret scope)
- [ ] Set up Unity Catalog and create catalog/schemas
- [ ] Mount ADLS containers in Databricks

**Goal:** Be able to read/write data from Databricks to ADLS

### Week 2 — Data Pipelines
- [ ] Create ETL Job Cluster
- [ ] Create SQL Warehouse
- [ ] Create first Delta tables (Bronze and Silver patient)
- [ ] Build Bronze → Silver DLT pipeline
- [ ] Schedule the pipeline to run on a trigger
- [ ] Connect Power BI to SQL Warehouse
- [ ] Create a basic patient count dashboard in Power BI

**Goal:** Have a working end-to-end pipeline from raw CSV to Power BI dashboard

### Week 3 — Streaming and Security
- [ ] Create Azure Event Hubs
- [ ] Create Streaming Cluster (run briefly, not 24/7 on free trial)
- [ ] Test streaming wearable data into Bronze
- [ ] Apply column masking on PHI fields
- [ ] Enable audit logging to Log Analytics
- [ ] Create Azure AD groups and assign Unity Catalog permissions
- [ ] Test that an analyst account cannot see masked PHI columns

**Goal:** Validate security and compliance controls work

### Month 2 — Production Readiness (Paid)
- [ ] Upgrade to pay-as-you-go billing
- [ ] Create a separate Development workspace
- [ ] Set up GitHub/Azure DevOps for notebook version control
- [ ] Schedule all ETL jobs in Databricks Workflows
- [ ] Start the Streaming Cluster permanently
- [ ] Engage a privacy lawyer to review your data flows
- [ ] Document data lineage for Privacy Act compliance

---

## 20. Glossary of Terms

| Term | Plain English Explanation |
|---|---|
| **Azure** | Microsoft's cloud platform — rented computers and storage on the internet |
| **Databricks** | A data processing platform that runs on Azure |
| **ADLS Gen2** | A huge, organised cloud hard drive optimised for big data |
| **Key Vault** | A digital safe for storing passwords and secrets |
| **Resource Group** | A folder in Azure that groups related services together |
| **Cluster** | A group of virtual machines that run your Databricks code |
| **Notebook** | A document in Databricks where you write and run code |
| **Delta Lake** | A way of storing data that prevents corruption and supports version history |
| **ETL** | Extract, Transform, Load — the process of moving and cleaning data |
| **Delta Live Tables (DLT)** | Databricks' tool for building automated, reliable ETL pipelines |
| **SQL Warehouse** | A fast database optimised for SQL queries and BI dashboards |
| **Unity Catalog** | Databricks' tool for controlling who can access which data |
| **MLflow** | A tool for tracking machine learning experiments |
| **Medallion Architecture** | Bronze/Silver/Gold — three layers of increasing data quality |
| **PHI** | Protected Health Information — data that identifies a real patient |
| **Pseudonymisation** | Replacing a real identifier (like a name) with an untraceable code (like a hash) |
| **FHIR** | A standard format for sharing healthcare data between systems |
| **HL7** | Another standard for healthcare data exchange (older than FHIR) |
| **Spark** | The open-source engine Databricks uses to process big data fast |
| **Streaming** | Processing data as it arrives in real-time (vs. batch processing) |
| **Event Hubs** | Azure service that receives real-time data streams from devices |
| **RBAC** | Role-Based Access Control — permissions based on job roles |
| **TLS** | Transport Layer Security — encrypts data while it travels over the internet |
| **Managed Identity** | An automatic "service account" Azure creates for a service to use |
| **Secret Scope** | A named link in Databricks that points to a Key Vault |
| **Auto Loader** | Databricks feature that automatically detects and loads new files |
| **DBU** | Databricks Unit — the unit used to measure and price compute usage |
| **Spot Instance** | Cheap Azure VM that can be reclaimed by Microsoft with 30-second notice |
| **On-demand Instance** | Standard Azure VM — more expensive but guaranteed availability |
| **Audit Log** | A record of every action taken (who did what, when) |
| **Australian Privacy Act** | Australian law governing how personal data (including health data) must be handled |

---

## Quick Reference Card

Save this for daily use:

```
YOUR KEY DETAILS:
─────────────────────────────────────────────────────
Subscription ID:    2e4d86c9-3434-492e-8aa0-1510148509c9
Resource Group:     rg-healthstartup-prod
Storage Account:    adlshealthstartupprod
Key Vault:          kv-healthstartup-prod
Databricks:         adb-healthstartup-prod
Region:             australiaeast (Sydney)
─────────────────────────────────────────────────────

KEY URLS:
─────────────────────────────────────────────────────
Azure Portal:       https://portal.azure.com
Key Vault URL:      https://kv-healthstartup-prod.vault.azure.net/
Storage DFS:        https://adlshealthstartupprod.dfs.core.windows.net/
─────────────────────────────────────────────────────

DATABRICKS MOUNTS:
─────────────────────────────────────────────────────
/mnt/bronze/  →  Raw data (never modify)
/mnt/silver/  →  Cleaned data
/mnt/gold/    →  Business-ready data
/mnt/ml/      →  ML features
─────────────────────────────────────────────────────

UNITY CATALOG PATH:
─────────────────────────────────────────────────────
healthstartup.bronze_db.[table]
healthstartup.silver_db.[table]
healthstartup.gold_db.[table]
healthstartup.ml_db.[table]
─────────────────────────────────────────────────────

COST REMINDERS:
─────────────────────────────────────────────────────
- Stop interactive clusters at end of day
- SQL Warehouse auto-stops after 10 min idle
- Do NOT run streaming cluster 24/7 on free trial
- Check Cost Management weekly
─────────────────────────────────────────────────────
```

---

*Document version: 2.0 (Beginner-Friendly) | Created: 2026-03-28*
*Region: Australia East | Compliance: Australian Privacy Act 1988 + My Health Records Act 2012*
*Subscription: 2e4d86c9-3434-492e-8aa0-1510148509c9*
