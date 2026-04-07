# Azure Infrastructure Setup Guide
## Healthcare Databricks Platform

---

## Prerequisites
- Azure account (free trial: azure.microsoft.com/free)
- Databricks account (free trial: databricks.com)
- Power BI Desktop (free: microsoft.com/power-bi/desktop)
- Databricks CLI installed: `pip install databricks-cli`

---

## Step 1: Create Resource Group

1. Go to portal.azure.com
2. Search "Resource groups" → Create
3. Settings:
   - Subscription: Your subscription
   - Resource group name: `rg-healthstartup-prod`
   - Region: `Australia East`
4. Review + Create → Create

**Why Australia East:** Data residency requirement under Australian Privacy Act — patient data must stay in Australia.

---

## Step 2: Create Azure Data Lake Storage Gen2

1. Search "Storage accounts" → Create
2. Settings:
   - Resource group: `rg-healthstartup-prod`
   - Storage account name: `adlshealthstartupprod`
   - Region: `Australia East`
   - Performance: `Standard`
   - Redundancy: `LRS` (Locally Redundant — cheapest for dev)
3. Advanced tab → Enable "Hierarchical namespace" (this makes it ADLS Gen2)
4. Review + Create → Create

### Create Containers
Go to storage account → Containers → Create each:
- `bronze` (Private)
- `silver` (Private)
- `gold` (Private)
- `ml` (Private)

---

## Step 3: Create Azure Key Vault

1. Search "Key vaults" → Create
2. Settings:
   - Resource group: `rg-healthstartup-prod`
   - Key vault name: `kv-healthstartup-prod`
   - Region: `Australia East`
   - Pricing tier: `Standard`
3. Access configuration tab → Permission model: `Azure role-based access control`
4. Review + Create → Create

### Assign yourself Key Vault Secrets Officer role
1. Go to Key Vault → Access control (IAM) → Add role assignment
2. Role: `Key Vault Secrets Officer`
3. Assign to: your user account
4. Save

---

## Step 4: Create Azure Databricks Workspace

1. Search "Azure Databricks" → Create
2. Settings:
   - Resource group: `rg-healthstartup-prod`
   - Workspace name: `adb-healthstartup-prod`
   - Region: `Australia East`
   - Pricing tier: `Premium` (required for DLT, RBAC, audit logs)
3. Review + Create → Create

---

## Step 5: Create App Registration (Service Principal)

1. Search "Azure Active Directory" → App registrations → New registration
2. Name: `databricks-storage-sp`
3. Register

### Create Client Secret
1. Go to Certificates & secrets → New client secret
2. Description: `databricks-secret`
3. Expires: 24 months
4. **Copy the Value immediately** (shown only once)

### Assign Storage Role to Service Principal
1. Go to `adlshealthstartupprod` storage account
2. Access control (IAM) → Add role assignment
3. Role: `Storage Blob Data Contributor`
4. Assign to: `databricks-storage-sp`

---

## Step 6: Store Secrets in Key Vault

Go to `kv-healthstartup-prod` → Secrets → Generate/Import

Create each secret:

| Name | Value |
|------|-------|
| `adls-storage-key` | Storage account key (from Storage → Access keys) |
| `sp-client-id` | App Registration Application (client) ID |
| `sp-client-secret` | The secret value you copied in Step 5 |
| `tenant-id` | Azure AD → Overview → Tenant ID |

---

## Step 7: Create Databricks Workspace Resources

### Create Cluster
1. Databricks workspace → Compute → Create cluster
2. Settings:
   - Name: `etl-job-cluster`
   - Runtime: `14.3 LTS ML`
   - Node type: `Standard_D4ds_v5`
   - Mode: `Single node`
   - Auto-terminate: `20 minutes`
3. Create

### Configure Databricks CLI
```bash
databricks configure --token
# Host: https://adb-xxxx.azuredatabricks.net
# Token: (generate from User Settings → Developer → Access tokens)
```

### Create Secret Scope (UI method)
1. Navigate to: `https://<your-workspace>.azuredatabricks.net/#secrets/createScope`
2. Settings:
   - Scope name: `kv-healthstartup`
   - Manage principal: `All Users`
   - DNS name: `https://kv-healthstartup-prod.vault.azure.net/`
   - Resource ID: `/subscriptions/<sub-id>/resourceGroups/rg-healthstartup-prod/providers/Microsoft.KeyVault/vaults/kv-healthstartup-prod`
3. Create

### Assign AzureDatabricks SP Key Vault Access
1. Key Vault → Access control (IAM) → Add role assignment
2. Role: `Key Vault Secrets User`
3. Assign to: `AzureDatabricks` (enterprise application)

---

## Step 8: Create DLT Pipeline

1. Databricks → Delta Live Tables → Create Pipeline
2. Settings:
   - Name: `patient-etl-pipeline`
   - Source: `/Workspace/Users/<email>/patient-etl-pipeline/transformations/**`
   - Target schema: `default`
   - Compute: `Serverless`
3. Advanced → Configuration — add these key-value pairs:

| Key | Value |
|-----|-------|
| `fs.azure.account.auth.type.adlshealthstartupprod.dfs.core.windows.net` | `OAuth` |
| `fs.azure.account.oauth.provider.type.adlshealthstartupprod.dfs.core.windows.net` | `org.apache.hadoop.fs.azurebfs.oauth2.ClientCredsTokenProvider` |
| `fs.azure.account.oauth2.client.id.adlshealthstartupprod.dfs.core.windows.net` | `{{secrets/kv-healthstartup/sp-client-id}}` |
| `fs.azure.account.oauth2.client.secret.adlshealthstartupprod.dfs.core.windows.net` | `{{secrets/kv-healthstartup/sp-client-secret}}` |
| `fs.azure.account.oauth2.client.endpoint.adlshealthstartupprod.dfs.core.windows.net` | `https://login.microsoftonline.com/<tenant-id>/oauth2/token` |

4. Save → Start

---

## Step 9: Create SQL Warehouse

1. Databricks → SQL Warehouses → Create
2. Settings:
   - Name: `sql-healthstartup`
   - Size: `2X-Small`
   - Type: `Serverless`
   - Auto-stop: `10 minutes`
3. Create

---

## Step 10: Connect Power BI

1. Open Power BI Desktop
2. Get Data → Azure Databricks → Connect
3. Settings:
   - Server hostname: (from SQL Warehouse → Connection details)
   - HTTP path: (from SQL Warehouse → Connection details)
   - Authentication: Personal Access Token
4. Select tables: `gold_patients_by_postcode`, `gold_data_quality_summary`
5. Load → Create visualisations

---

## Troubleshooting Common Issues

| Error | Cause | Fix |
|-------|-------|-----|
| `CLUSTER_LAUNCH_RESOURCE_STOCKOUT` | Azure VM capacity unavailable | Try different VM size or use Serverless |
| `Invalid configuration value for fs.azure.account.key` | Serverless DLT blocks account keys | Use OAuth service principal instead |
| `UNRESOLVED_COLUMN patient_id` in DLT | Expectations reference dropped columns | Reference derived columns (e.g., patient_id_hash) |
| `userAADToken required` for secret scope CLI | CLI needs AAD token for Key Vault scope | Use UI form at `#secrets/createScope` |
| `Secret does not exist` | Secret not yet created in Key Vault | Create secret in Key Vault first |
| `AADSTS7000215 Invalid client secret` | Copied Secret ID instead of Secret Value | Copy VALUE column, not ID column |
