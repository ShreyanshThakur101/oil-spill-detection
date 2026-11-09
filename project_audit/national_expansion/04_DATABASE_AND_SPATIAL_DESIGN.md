# 04 — DATABASE & SPATIAL DATA MODEL DESIGN

**Status:** REVISED & EXPANDED  
**Revision Date:** November 8, 2026  
**Focus:** Architectural resolution of persistent database storage, serverless `/tmp` deprecation, and low-cost spatial indexing strategy.

---

## 1. Resolution of Database Persistence

### The Problem with Serverless `/tmp`
In the current deployed prototype on Vercel, the database is stored in `/tmp/oil_spill.db` (`api/index.py`). Because serverless lambdas are ephemeral and freeze or recycle containers across requests, data stored in `/tmp` is destroyed on cold starts or whenever traffic routes to a different execution instance. **This is unacceptable for durable national incident tracking.**

### Comprehensive Database Option Comparison

| Metric / Dimension | Option A: SQLite on Low-Cost VPS | Option B: Managed PostgreSQL Free Tier (Supabase / Neon) | Option C: Managed PostgreSQL + PostGIS |
| :--- | :--- | :--- | :--- |
| **Monthly Cost (INR)** | **₹0 (on existing VPS)** | **₹0 (Free Tier)** | **₹0 to ₹800 / mo** |
| **Persistence Guarantee** | 100% durable local SSD disk | 100% durable managed cloud storage | 100% durable managed cloud storage |
| **Storage Limits** | 20 GB to 40 GB (VPS disk) | 500 MB (Supabase) / 0.5 GB (Neon) | 500 MB (Free tier limit) |
| **Connection Limits** | Single-file local concurrency (WAL mode) | 60 direct / pooler on Supabase | 60 direct / pooler |
| **Inactivity / Sleeping** | Never sleeps (24/7 VPS daemon) | Sleeps after 7 days inactivity (Supabase free) | Sleeps after 7 days inactivity (free tier) |
| **Spatial Capabilities** | Pre-filtered bounding boxes + Shapely | Bounding box indexing + Shapely | Native PostGIS functions (`ST_Contains`, `ST_DWithin`) |
| **Backup & Recovery** | Automated daily SQLite snapshot to S3/B2 | Managed automated daily snapshots | Managed automated daily snapshots |
| **Deployment Complexity**| **Lowest** (Zero external dependencies) | Low (SQLAlchemy connection string change) | Medium (Requires PostGIS extension & GeoAlchemy2) |
| **Migration Risk** | Zero (Preserves existing code) | Low (Standard PostgreSQL migration) | Medium (Schema redefinition for spatial types) |

---

## 2. Recommended Database Architecture & Phased Path

### Recommendation: Option A for Initial Rollout -> Option B for Multi-Worker Scaling
1. **Initial Deployment (Milestones 1–4)**:
   - Run a single persistent SQLite database in Write-Ahead Logging (WAL) mode (`PRAGMA journal_mode=WAL;`) on the backend VPS.
   - Store spatial polygons in GeoJSON format.
   - Use fast indexed bounding-box range columns (`min_lon`, `min_lat`, `max_lon`, `max_lat`) for SQL filtering, followed by exact geometric checks in Python using Shapely.
   - **Cost: ₹0 extra**; 100% durable; zero network latency; no connection pooler exhaustion.
2. **Scale-Up Path (Milestones 5–7)**:
   - When background ingestion workers run concurrently on separate containers, switch the SQLAlchemy connection string from `sqlite:///...` to Supabase managed PostgreSQL (`postgresql://...`).
   - If spatial queries exceed 50,000 active records, enable the PostGIS extension.

---

## 3. National Data Model Schema

```
┌─────────────────────────────────┐
│       surveillance_zones        │
├─────────────────────────────────┤
│ id: VARCHAR(16) [PK]            │ ◄─── e.g. "IN-MH", "IN-KL"
│ name: VARCHAR(64)               │
│ coast: VARCHAR(16)              │ ◄─── "WEST", "EAST", "ISLANDS"
│ baseline_geojson: JSON          │
│ territorial_sea_nm: INTEGER     │ ◄─── Default 12 nm
│ offshore_buffer_nm: INTEGER     │ ◄─── Configurable: 24, 50, 100 nm
│ active_monitoring: BOOLEAN      │
└────────────────┬────────────────┘
                 │ 1:N
┌────────────────▼────────────────┐
│          observations           │
├─────────────────────────────────┤
│ id: VARCHAR(64) [PK]            │ ◄─── Sentinel-1 Product ID
│ zone_id: VARCHAR(16) [FK]       │
│ satellite: VARCHAR(32)          │
│ acquisition_time: DATETIME      │
│ footprint_geojson: JSON         │
│ min_lon / max_lon / ...: FLOAT  │ ◄─── Bounding box index columns
│ status: VARCHAR(32)             │ ◄─── DISCOVERED / DOWNLOADED / PROCESSED / NO_SLICK
│ provenance: VARCHAR(32)         │ ◄─── LIVE_OBSERVATION / HISTORICAL_VERIFIED / SYNTHETIC_DEMO
└────────────────┬────────────────┘
                 │ 1:N
┌────────────────▼────────────────┐
│           incidents             │
├─────────────────────────────────┤
│ id: INTEGER [PK, Auto]          │ ◄─── Central Incident Registry
│ observation_id: VARCHAR(64)[FK] │
│ zone_id: VARCHAR(16) [FK]       │
│ title: VARCHAR(128)             │
│ detected_at: DATETIME           │
│ severity: VARCHAR(16)           │ ◄─── TIER_1 (<700t), TIER_2 (700-10,000t), TIER_3 (>10,000t)
│ status: VARCHAR(32)             │ ◄─── CANDIDATE / INVESTIGATING / VERIFIED / CLOSED
│ provenance: VARCHAR(32)         │ ◄─── LIVE_OBSERVATION / SYNTHETIC_DEMO / HISTORICAL_VERIFIED
│ slick_geojson: JSON             │
│ slick_area_km2: FLOAT           │
│ origin_polygon_geojson: JSON    │
│ estimated_spill_time: DATETIME  │
│ uncertainty_radius_km: FLOAT    │
│ primary_suspect_mmsi: VARCHAR   │
│ primary_suspect_score: FLOAT    │
│ legal_dossier_json: JSON        │ ◄─── Frozen Section 356J Investigative Brief
└────────────────┬────────────────┘
                 │ 1:N
┌────────────────▼────────────────┐
│         vessel_scores           │
├─────────────────────────────────┤
│ id: INTEGER [PK, Auto]          │
│ incident_id: INTEGER [FK]       │
│ mmsi: VARCHAR(16)               │
│ vessel_name: VARCHAR(64)        │
│ vessel_type: VARCHAR(32)        │
│ flag: VARCHAR(8)                │
│ proximity_score: FLOAT          │
│ parity_score: FLOAT             │
│ temporality_score: FLOAT        │
│ ais_gap_score: FLOAT            │
│ speed_anomaly_score: FLOAT      │
│ vessel_type_prior: FLOAT        │
│ composite_score: FLOAT          │
│ explanation: TEXT               │
│ track_geojson: JSON             │
└─────────────────────────────────┘
```

---

## 4. Provenance Enforcement in Schema & API

1. **Foreign Key Integrity**: Every `incident` links to an `observation`. If an observation is tagged `SYNTHETIC_DEMO`, the incident inherits `provenance = "SYNTHETIC_DEMO"`.
2. **Dashboard Query Filter**: Live surveillance metrics and national incident statistics automatically enforce `WHERE provenance != 'SYNTHETIC_DEMO'`.
3. **Demo Isolation**: A dedicated `/api/demo-cases` endpoint serves synthetic demonstration scenarios without mixing them into operational surveillance tables.
