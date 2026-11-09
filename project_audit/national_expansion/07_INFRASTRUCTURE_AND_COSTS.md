# 07 — INFRASTRUCTURE, SCALABILITY & COST ANALYSIS (INR)

**Status:** REVISED & EXPANDED  
**Revision Date:** November 8, 2026  
**Constraint:** LOW INFRASTRUCTURE BUDGET. Prioritize free and open-access tiers; avoid introducing expensive managed cloud services.

---

## 1. Evaluation of Practical Deployment Architectures

| Dimension / Metric | Option A: Vercel Frontend + Serverless API + GitHub Actions Cron | Option B: Vercel Frontend + Low-Cost VPS (Backend, Database & Workers) [RECOMMENDED] | Option C: Vercel Frontend & API + Managed DB + VPS Worker |
| :--- | :--- | :--- | :--- |
| **Monthly Cost (INR)** | **₹0 / mo** | **₹350 – ₹450 / mo** | **₹800 – ₹1,800 / mo** |
| **Free-Tier Restrictions** | Vercel 10s function timeout; GitHub Actions 2,000 free min/mo. | Unlimited runtime on VPS; Vercel free tier for static CDN. | Vercel API timeouts; managed DB connection limits. |
| **Runtime Limitations** | Cannot execute heavy image preprocessing or multi-minute advection simulations. | **No runtime limitations**. Workers run continuously or as cron daemons. | Worker has no limits, but API remains constrained by Vercel timeouts. |
| **Storage Constraints** | Vercel `/tmp` is ephemeral; GitHub Actions disk is destroyed post-run. | **20 GB to 40 GB NVMe SSD** included with VPS (plenty for thousands of patches & DB). | 500 MB managed DB limit + VPS disk. |
| **Processing Capabilities**| Low (Lightweight API only). | **High** (Multi-core CPU handles Python, GDAL, Shapely, PyTorch inference). | High on worker, low on API. |
| **System Reliability** | Fragile (Artifact handoffs between GitHub Actions and Vercel). | **High** (Self-contained daemon with systemd restart & daily backups). | High, but introduces multi-cloud network failure points. |
| **Maintenance Burden** | Low until workflows fail silently. | Low (Single standard Ubuntu VPS with automated updates). | Medium (Requires managing 3 distinct cloud providers). |

---

## 2. Recommended Architecture & Detailed Cost Breakdown

### The Recommended Architecture: Option B
- **Frontend**: Deployed on **Vercel Free Tier** (Global Edge CDN). Provides instant worldwide distribution, HTTPS SSL termination, and zero hosting cost.
- **Backend API & Scheduled Workers**: Hosted on a single **Low-Cost Linux VPS** (e.g. Hetzner Cloud CX22 at €3.79/mo ~₹350/mo, or DigitalOcean 1 GB Droplet at $4/mo ~₹350/mo).
  - Runs FastAPI on Uvicorn managed by `systemd`.
  - Runs the scheduled satellite poller and hydrodynamic workers via native Linux `cron`.
  - Hosts the persistent SQLite database on local NVMe SSD.
  - Reverse-proxied via Nginx with automated free Let's Encrypt SSL.
- **Storage**: Segmented satellite patches (~200 KB PNG) and GeoJSON geometries stored locally on VPS disk. For offsite backups, use **Cloudflare R2** (10 GB storage and unlimited egress free forever).

### Comprehensive Monthly Budget (INR)

| Component | Provider & Tier | Monthly Cost (INR) |
| :--- | :--- | :--- |
| **Frontend CDN** | Vercel Hobby Free Tier | **₹0** |
| **Backend & Worker Compute** | Hetzner Cloud CX22 (2 vCPU, 4 GB RAM, 40 GB NVMe) | **₹350 – ₹400** |
| **Domain Name (Optional)** | Standard `.in` or `.org` domain (~₹700/year) | **₹60 / mo** |
| **Database** | Persistent SQLite on NVMe SSD | **₹0** |
| **Offsite Backups** | Cloudflare R2 (10 GB Free Tier) | **₹0** |
| **Satellite Imagery** | Copernicus CDSE Open Access (Sentinel-1) | **₹0** |
| **Ocean Currents** | Copernicus Marine Service (CMEMS Global Physics) | **₹0** |
| **Surface Winds** | ECMWF ERA5 Climate Data Store | **₹0** |
| **AIS Vessel Tracking** | Global Fishing Watch Developer Free Tier | **₹0** |
| **Total Monthly Operating Cost** | **Fully Operational SAGAR-DRISHTI Platform** | **₹410 – ₹460 / month** |

---

## 3. Financial Comparison: SAGAR-DRISHTI vs. Traditional Surveillance

- **Indian Coast Guard Dornier 228 Sortie**: A single 3-hour maritime reconnaissance flight costs **₹35,00,000+** in aviation turbine fuel, flight crew, and airframe maintenance.
- **SAGAR-DRISHTI Surveillance**: Continuously monitors the entire 7,516 km coastline and offshore economic zones for an entire year for **under ₹5,500 total compute cost** (<0.15% of a single airborne sortie).
