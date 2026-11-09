# SAGAR-DRISHTI: Google Colab Compute Integration & Nationwide Prototype Implementation Plan

**System:** SAGAR-DRISHTI — Marine Oil Spill Detection & Vessel Attribution Platform  
**Target Coverage:** All 9 Indian Coastal States, 4 Coastal Union Territories & Configurable Offshore Zones  
**Compute Architecture:** Hybrid Prototype (Google Colab as GPU Worker + FastAPI/SQLite/Vercel Application Core)  
**Status:** IMPLEMENTATION PLANNING & ARCHITECTURE SPECIFICATION  
**Date:** November 8, 2026  

---

## 1. Executive Summary

This plan integrates **Google Colab** as the primary computational environment for SAGAR-DRISHTI during its prototype phase. It resolves the core infrastructure dilemma: executing heavy GPU deep learning (Sentinel-1 SAR segmentation) and scientific hydrodynamic backtracking (backward Lagrangian advection) without incurring recurring cloud GPU VM expenses ($50–$200/month).

By establishing a **decoupled, asynchronous job workflow**, Google Colab acts as an on-demand batch worker. The operational FastAPI backend, Leaflet dashboard, incident registry, and legal enforcement engine remain lightweight, persistent, and decoupled from active Colab notebook sessions.

---

## 2. Phase 1 — Repository & Infrastructure Assessment

### 2.1 Component Assessment Matrix

| Subsystem | Implemented Component | Actual Reality in Codebase | Colab Executability | Technical Remediation Needed |
| :--- | :--- | :--- | :--- | :--- |
| **SAR Segmentation Model** | `backend/app/ml/model_utils.py` | U-Net with ResNet-34 encoder (`segmentation-models-pytorch`). Verified standard PyTorch model. | **100% Compatible**. Runs natively on Colab T4/A100 GPU. | None. Model definition is functional. |
| **Model Weights** | `backend/data/models/` | Weight file `unet_resnet34_oilspill.pth` is **absent** (`README.md` lists as `TBD`). Runtime falls back to deterministic polygon mock. | **Target of Colab**. Colab will train and output this checkpoint. | Execute Colab training run; save weights to Google Drive. |
| **Training Pipeline** | `backend/app/ml/train.py` | PyTorch training loop combining BCE + Dice loss with Adam optimizer. | **Executable with Minor Path Fixes**. Hardcoded import `..config` requires module execution. | Provide standalone Colab execution script with dataset mounting. |
| **Dataset Loader** | `backend/app/ml/dataset.py` | OpenCV/PyTorch dataset loader expecting paired `images/` and `masks/`. | **100% Compatible**. | Deep-SAR Kaggle dataset must be downloaded in Colab. |
| **Inference Pipeline** | `backend/app/ml/infer.py` | Ingests GeoTIFF via `rasterio`, normalizes, resizes to 256x256, extracts polygon via `geojson_polygon_from_mask()`. | **100% Compatible**. Requires `rasterio`, `opencv-python`, `shapely`. | Colab executes inference and exports lightweight GeoJSON vectors. |
| **SAR Preprocessing** | `Sentinel-1 GRD` | **Missing**. No radiometric calibration ($\sigma^0$ dB conversion), Lee speckle filter, or terrain correction. | **Feasible in Colab**. Colab can run lightweight Python raster tools (`scipy`, `rasterio`). | Implement Python-native calibration and $3\times 3$ Lee speckle filtering. |
| **Hydrodynamic Drift** | `backend/app/physics/drift_model.py` | Pure-Python 200-particle Lagrangian advection retro-tracking 18 hours back using regional monsoon drift equations. | **100% Compatible**. Runs in Colab or backend. | Add spatial-temporal NetCDF interpolation for live CMEMS/ERA5 files. |
| **AIS Scoring & Dossier** | `scoring/scorer.py`, `nugen/` | 6-factor explainable scoring and Section 356J legal dossier generation. | **Not needed in Colab**. Runs natively in FastAPI backend. | Keep on backend; Colab only feeds detected slick polygon and timestamp. |
| **Database Persistence** | `backend/app/database.py` | SQLite database. On Vercel serverless, DB is ephemeral in `/tmp`. | **N/A**. Backend storage. | Implement persistent SQLite or Supabase PostgreSQL to receive Colab job results. |

### 2.2 Dependencies & Colab Environment Profile

Google Colab instances provide:
- **Default GPU**: NVIDIA T4 (16 GB VRAM) on free tier; A100/V100 on Colab Pro.
- **Default RAM**: 12.7 GB system RAM.
- **Default Disk**: ~78 GB free temporary disk.

**Required Colab Environment Installation**:
```bash
!pip install -q torch torchvision segmentation-models-pytorch rasterio opencv-python shapely pyproj requests
```
All required dependencies install cleanly on standard Colab runtimes in under 45 seconds without system C++ compiler conflicts.

---

## 3. Phase 2 — Colab Compute Workload Architecture

```
┌────────────────────────────────────────────────────────────────────────┐
│                        GOOGLE COLAB WORKLOADS                          │
├─────────────────────────┬────────────────────────┬─────────────────────┤
│ 1. U-Net Training & Eval│ 2. SAR Preprocessing   │ 3. Batch Inference  │
│ - Deep-SAR Kaggle Data  │ - Radiometric Calib    │ - Full Swath Slicing│
│ - ResNet34 Backbone     │ - Lee Speckle Filter   │ - Sliding Window    │
│ - Output: .pth Weights  │ - Output: Clean GeoTIFF│ - Output: GeoJSON   │
└────────────┬────────────┴───────────┬────────────┴──────────┬──────────┘
             │                        │                       │
             ▼                        ▼                       ▼
    [Google Drive Cache]    [Lightweight Result]    [Lightweight Result]
  (Weights & Test Images)    (PNG Mask & Metrics)   (GeoJSON Slicks & IoU)
             │                        │                       │
             └────────────────────────┼───────────────────────┘
                                      │ HTTP POST / Manual Import
                                      ▼
             ┌────────────────────────────────────────────────┐
             │            SAGAR-DRISHTI BACKEND API           │
             │   - Validates Job Payload & Schema             │
             │   - Stores Incident in Persistent DB           │
             │   - Executes Drift Modeling & 6-Factor AIS     │
             │   - Renders Slick on React Leaflet Dashboard   │
             └────────────────────────────────────────────────┘
```

### Detailed Workload Specifications

| Workload | Input Data | Compute Profile | Expected Output | Output Size | Colab Disconnect Behavior | Return Mechanism to Backend |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **1. Model Training** | Kaggle Deep-SAR (images + binary masks, ~500 MB) | GPU (T4), ~15 min for 20 epochs, batch size 8 | `unet_resnet34_oilspill.pth` (weights) + validation report | ~85 MB | Checkpoints saved to mounted Google Drive at every epoch; training resumes from last epoch. | Checkpoint copied to `backend/data/models/` or uploaded to backend storage. |
| **2. SAR Preprocessing** | Raw Sentinel-1 GRD GeoTIFF tile (cropped 1000x1000) | CPU/RAM intensive (4 GB RAM, 2 min) | Calibrated, speckle-filtered GeoTIFF patch | ~4 MB | Non-destructive; re-run cell if interrupted. | Temporary file; piped directly into segmentation inference. |
| **3. Segmentation Inference** | Preprocessed SAR GeoTIFF or PNG patch | GPU (T4), < 2 seconds per patch | GeoJSON polygon of detected slick, area ($km^2$), elongation, IoU confidence | ~15 KB (GeoJSON) + ~200 KB (mask PNG) | Single-patch execution takes seconds; minimal disconnect risk. | Direct HTTP POST to `/api/colab/results` or export JSON payload. |
| **4. Historical Batch Ingestion** | 50+ historical Sentinel-1 scenes along Indian tanker routes | GPU (T4), ~25 min batch run | Batch results array: `[ { scene_id, slicks: [GeoJSON], timestamp } ]` | ~1.2 MB total JSON | Colab notebook tracks processed scene IDs in a progress file on Drive; resumes on restart. | Batch import script calls backend API for each detected candidate. |
| **5. Hydrodynamic Simulation** | Slick GeoJSON, CMEMS NetCDF currents, ERA5 winds | CPU (2 cores, 1.5 GB RAM, 30s) | Backward drift origin cone GeoJSON, 200 particle trajectories, dispersion cloud | ~80 KB (GeoJSON) | Fast execution; easily re-runnable. | Can run directly on backend or in Colab notebook. |

---

## 4. Phase 3 — Colab-to-Backend Job Workflow

To ensure reliability without tight coupling or continuous uptime dependencies, the prototype uses an **Asynchronous Hybrid Protocol** supporting both **Direct REST API Ingestion** and **File-Based Import**:

```mermaid
sequenceDiagram
    autonumber
    actor Operator as Operator / Researcher
    participant Colab as Google Colab Notebook
    participant Drive as Google Drive / Storage
    participant Backend as FastAPI Backend
    participant DB as Persistent SQLite / PostGIS
    participant Dashboard as React Dashboard

    Operator->>Backend: 1. Create Job (or Colab generates Job ID)
    Backend-->>Operator: Return job_id: "JOB-20261108-MH01"
    Operator->>Colab: 2. Run Notebook with job_id & target scene
    Colab->>Colab: 3. Download SAR data, Calibrate, Run U-Net Inference
    Colab->>Drive: 4. Checkpoint weights & save debug masks
    Colab->>Backend: 5. POST /api/colab/results (Bearer Secret + Payload)
    Note over Colab,Backend: If offline: Colab exports job_result.json; Operator uploads via UI
    Backend->>Backend: 6. Validate GeoJSON schema & IoU confidence
    Backend->>DB: 7. Insert into observations & incidents tables
    Backend->>Backend: 8. Trigger 6-Factor AIS correlation & Section 356J draft
    Dashboard->>Backend: 9. Fetch /api/incidents
    Backend-->>Dashboard: 10. Display newly detected slick on Leaflet Map
```

### 4.1 Job States & Transitions

```
[PENDING] ──► [RUNNING_COLAB] ──► [COMPLETED] ──► [IMPORTED_TO_DB]
                      │
                      ▼
                   [FAILED] (with error log)
```

1. `PENDING`: Job registered in backend with target Sentinel-1 Product ID and coastal zone.
2. `RUNNING_COLAB`: Colab worker acknowledged job execution.
3. `COMPLETED`: Inference finished in Colab; GeoJSON polygon and confidence metrics generated.
4. `IMPORTED_TO_DB`: Backend validated payload, created incident record, and executed drift/AIS pipelines.
5. `FAILED`: Job failed in Colab (e.g. out of memory, invalid raster coordinates); error logged.

### 4.2 Colab Ingestion API Contract

- **Endpoint**: `POST /api/colab/results`
- **Authentication**: `Authorization: Bearer <COLAB_SECRET_TOKEN>` (configured in `.env`).
- **Request Payload Schema**:
```json
{
  "job_id": "JOB-20261108-MH01",
  "observation": {
    "product_id": "S1A_IW_GRDH_1SDV_20261108T021512_MH",
    "zone_id": "IN-MH",
    "satellite": "Sentinel-1A",
    "acquisition_time": "2026-11-08T02:15:12Z",
    "polarization": "VV+VH",
    "footprint_geojson": { "type": "Polygon", "coordinates": [...] }
  },
  "detection": {
    "slick_detected": true,
    "confidence_iou": 0.894,
    "model_checkpoint": "unet_resnet34_oilspill_v1.pth",
    "polygon_geojson": {
      "type": "Polygon",
      "coordinates": [[[72.62, 18.78], [72.68, 18.82], [72.74, 18.89], [72.70, 18.91], [72.63, 18.85], [72.62, 18.78]]]
    },
    "shape_features": {
      "area_km2": 18.4,
      "perimeter_km": 24.1,
      "elongation": 2.8,
      "fragment_count": 1,
      "age_class": "fresh"
    }
  },
  "provenance": {
    "source": "LIVE_OBSERVATION",
    "worker": "Google_Colab_T4_Instance_2026",
    "preprocessing": "Radiometric_Sigma0_LeeFilter_3x3",
    "processed_timestamp": "2026-11-08T11:00:00Z"
  }
}
```

---

## 5. Phase 4 — Nationwide Coastal Geography & Configurable Offshore Zones

The geographic foundation covers **all 9 Indian Coastal States and 4 Coastal Union Territories** from the beginning, categorized into 13 authoritative surveillance sectors:

```
┌────────────────────────────────────────────────────────────────────────┐
│             ALL 13 INDIAN COASTAL STATES & UNION TERRITORIES           │
├───────────────────────┬────────────────────────┬───────────────────────┤
│ WESTERN COAST (5)     │ EASTERN COAST (4)      │ ISLANDS & UTs (4)     │
│ - Gujarat (IN-GJ)     │ - Tamil Nadu (IN-TN)   │ - Andaman & Nicobar   │
│ - Maharashtra (IN-MH) │ - Andhra Pradesh(IN-AP)│   Islands (IN-AN)     │
│ - Goa (IN-GA)         │ - Odisha (IN-OD)       │ - Lakshadweep (IN-LD) │
│ - Karnataka (IN-KA)   │ - West Bengal (IN-WB)  │ - Puducherry (IN-PY)  │
│ - Kerala (IN-KL)      │                        │ - DNH & Daman & Diu   │
│                       │                        │   (IN-DD)             │
└───────────────────────┴────────────────────────┴───────────────────────┘
```

### 5.1 Authoritative Baseline & Offshore Buffer Specifications

| Sector ID | State / UT | Coastline (km) | Littoral Anchor Points | Configurable Offshore Monitoring Zones |
| :--- | :--- | :--- | :--- | :--- |
| `IN-GJ` | **Gujarat** | 1,214.7 | Gulf of Kutch, Saurashtra, Gulf of Khambhat | 12 nm Territorial Sea; 50 nm High-Risk Tanker Buffer around Kandla/Mundra/Sikka/SPM. |
| `IN-MH` | **Maharashtra** | 652.6 | Dahanu, Mumbai Harbour, Murud, Redi | 12 nm Territorial Sea; Custom 80 nm Polygon enclosing **Mumbai High Offshore Oil Field**. |
| `IN-GA` | **Goa** | 101.0 | Terekhol River to Talpona River | 12 nm Territorial Sea; 24 nm Contiguous Zone around Mormugao Port approaches. |
| `IN-KA` | **Karnataka** | 280.0 | Karwar, Tadadi, Bhatkal, New Mangalore | 12 nm Territorial Sea; 30 nm Coastal Shipping Lane Buffer. |
| `IN-KL` | **Kerala** | 569.7 | Kasaragod, Kochi, Alappuzha, Pozhiyoor | 12 nm Territorial Sea; 50 nm Offshore Buffer covering Lakshadweep Sea commercial fairway. |
| `IN-TN` | **Tamil Nadu** | 906.9 | Pulicat, Chennai, Palk Bay, VOC Tuticorin | 12 nm Territorial Sea; Palk Strait Special Conservation Buffer; 40 nm Gulf of Mannar Buffer. |
| `IN-AP` | **Andhra Pradesh** | 973.7 | Krishnapatnam, Machilipatnam, Visakhapatnam | 12 nm Territorial Sea; Custom 60 nm Polygon enclosing **Krishna-Godavari (KG) Offshore Basin**. |
| `IN-OD` | **Odisha** | 476.4 | Gopalpur, Puri, Paradip, Dhamra | 12 nm Territorial Sea; 50 nm Paradip Tanker Route & Olive Ridley Marine Sanctuary Buffer. |
| `IN-WB` | **West Bengal** | 157.5 | Digha, Sagar Island, Haldia, Sundarbans | 12 nm Territorial Sea; 30 nm Hooghly River Estuary Fairway. |
| `IN-AN` | **Andaman & Nicobar** | 1,962.0 | North Andaman to Indira Point (Great Nicobar) | 12 nm Territorial Sea; **Six Degree Channel Special Buffer** (Malacca Strait international tanker lane). |
| `IN-LD` | **Lakshadweep** | 132.0 | Minicoy, Kavaratti, Agatti, Bitra | 12 nm Territorial Sea; **Nine Degree Channel Special Buffer** (high-density Persian Gulf transit corridor). |
| `IN-PY` | **Puducherry** | 45.0 | Puducherry, Karaikal, Mahe, Yanam | 12 nm Littoral Monitoring Zone. |
| `IN-DD` | **DNH & Daman & Diu** | 42.0 | Daman, Diu, Simbor | 12 nm Gulf of Khambhat Monitoring Zone. |

### 5.2 Decoupling Monitoring Zones from Legal Maritime Boundaries
- **Operational Monitoring Zones**: Bounded polygons defined by latitude/longitude vertices or buffered distance offsets from the coastline ($d_{\text{buffer}} \in \{12, 24, 50, 100\}\text{ nm}$). These define where the satellite scheduler searches for scenes and where radar inference is evaluated.
- **Legal Maritime Boundaries**: Territorial waters (12 nm) and the Exclusive Economic Zone (200 nm) governed by the Territorial Waters, Continental Shelf, Exclusive Economic Zone and other Maritime Zones Act 1976. The system never labels a 50 nm operational monitoring buffer as a sovereign legal boundary.
