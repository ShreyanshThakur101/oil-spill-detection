# 08 — RISKS, CAVEATS & DECISIONS REQUIRING APPROVAL

**Status:** REVISED & EXPANDED  
**Revision Date:** November 8, 2026  
**Objective:** Transparent catalog of verified technical/scientific limitations, legal constraints, and seven explicit decisions requiring project owner approval.

---

## 1. Verified Limitations & Mitigation Strategies

| Risk / Limitation | Root Cause | Impact | Mitigation Strategy |
| :--- | :--- | :--- | :--- |
| **Sentinel-1 Revisit Gaps** | Orbital mechanics dictate a 6–12 day revisit period over specific Indian coastal coordinates. | An oil spill occurring right after a satellite pass may not be observed from radar for several days. | Explicitly label platform as **Scheduled Surveillance**, not 24/7 live video. Plan optical fallback (Sentinel-2) where cloud cover permits. |
| **Vercel Serverless Ephemeral Storage** | Vercel serverless runs in stateless micro-containers with ephemeral `/tmp` storage. | Database records written to `/tmp` are destroyed on cold start or instance recycling. | Host backend and persistent database on a low-cost Linux VPS (Option B). |
| **Global Fishing Watch Rate Limits** | GFW free developer API enforces rate limits on spatial queries. | High-frequency polling across the entire EEZ could exhaust quotas. | Query GFW strictly on-demand when a verified slick polygon is detected, restricting queries to the backward drift origin cone. |
| **Scientific Attribution vs. Legal Proof** | The 6-factor attribution formula is a heuristic scoring model, not an automated conviction tool. | Presenting an attribution score as definitive proof in court could lead to admiralty legal challenges. | Clearly label all outputs as **Investigative Attribution Leads**. Mandate physical boarding, oil record book audits, and GC-MS fuel sampling before issuing formal charges. |
| **Nugen Endpoint Inactivity** | The remote endpoint `https://docs.nugen.in/inference` is a documentation portal (returns 404). | Remote LLM calls fail. | Retain and maintain the high-fidelity local domain-aligned generation function in `backend/app/nugen/client.py`. |

---

## 2. Seven Specific Decisions Presented for Approval

### Decision 1: Background Ingestion & Compute Architecture
- **Problem**: Scheduled satellite discovery, SAR image downloading, and hydrodynamic simulations cannot execute inside Vercel's short serverless HTTP request window.
- **Option A**: Hybrid (Vercel API + GitHub Actions Cron). Free, but GitHub Actions has a 2,000 min/mo limit and cannot store persistent states easily.
- **Option B (RECOMMENDED)**: Low-Cost VPS (Hetzner or DigitalOcean at ~₹350–₹450/mo) hosting the FastAPI backend, persistent database, and scheduled cron workers, with the React frontend served on Vercel CDN (free).
- **Option C**: Pure serverless (remain on Vercel with pre-computed demonstration outputs).

### Decision 2: Persistent Database Strategy
- **Problem**: Ephemeral `/tmp` storage on Vercel destroys nationwide incident records.
- **Option A (RECOMMENDED)**: Persistent SQLite database in WAL mode on the VPS NVMe SSD. Zero extra cost, zero external cloud dependency, sub-millisecond latency.
- **Option B**: Managed PostgreSQL free tier on Supabase (500 MB limit, sleeping after 7 days inactivity).
- **Option C**: Managed PostgreSQL + PostGIS (higher complexity, unnecessary for early rollout).

### Decision 3: National Geographic Boundary & Offshore Zone Strategy
- **Problem**: Decoupling the system from hardcoded Kochi/Mumbai cases without inventing arbitrary boundaries.
- **Recommendation**: Anchor coastal baselines to Survey of India (SOI) administrative state limits, and support 3 explicit tiers:
  1. Coastal Territorial Sea (12 nm).
  2. Configurable Offshore Monitoring Zones (24, 50, 100 nm buffers).
  3. Strategic Wider Maritime Domain (Full EEZ) supported as a future expansion.

### Decision 4: SAR Model Weights & Inference Strategy
- **Problem**: U-Net model code exists, but binary weights file `unet_resnet34_oilspill.pth` is missing from `backend/data/models/`.
- **Option A (RECOMMENDED)**: Train the ResNet-34 U-Net on free Google Colab/Kaggle GPU using the existing `train.py` script and the Kaggle Deep-SAR dataset, then commit verified weights with documented IoU metrics.
- **Option B**: Source an existing open-source SAR oil spill segmentation checkpoint.

### Decision 5: AIS Telemetry Source & Access Strategy
- **Problem**: Live vessel attribution requires access to terrestrial/satellite AIS data across Indian waters.
- **Recommendation**: Activate the Global Fishing Watch (GFW) API using a free developer API key, restricting queries strictly to the backward drift origin cone to preserve rate-limit quotas, with local SQLite caching.

### Decision 6: Satellite Imagery & Derived Product Storage Strategy
- **Problem**: Full Sentinel-1 scenes are 1.2 GB each. Storing full scenes nationwide would rapidly exhaust low-cost storage.
- **Recommendation**: Do not store full raw GeoTIFF scenes. Stream or crop localized bounding-box patches (~200 KB PNG) and store only derived GeoJSON polygons and legal brief JSONs locally (<1.5 GB/year total).

### Decision 7: Deployment Architecture & Monthly Budget
- **Problem**: Establishing a realistic production environment within a strict low-cost budget.
- **Recommendation**: Deploy frontend on Vercel CDN (₹0) and backend/database/workers on a Hetzner Cloud CX22 VPS (~₹350–₹400/mo), achieving complete nationwide surveillance for **under ₹450 per month**.

---

## 3. Account & Credential Checklist (Required for Milestone 3 & 5)

When ready to connect live external data, the following free developer registrations will be needed:
1. **Copernicus Data Space Ecosystem (CDSE)**: Free account for Sentinel-1 scene discovery.
2. **Copernicus Marine Service (CMEMS)**: Free account for ocean surface current vectors.
3. **Global Fishing Watch (GFW)**: Free developer Bearer API Key for AIS vessel positions and blackout gaps.
