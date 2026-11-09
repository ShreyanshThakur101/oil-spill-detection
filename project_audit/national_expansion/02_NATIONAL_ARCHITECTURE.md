# 02 — PROPOSED NATIONWIDE ARCHITECTURE & GEOGRAPHIC DESIGN

**Status:** REVISED & EXPANDED  
**Revision Date:** November 8, 2026  
**System:** SAGAR-DRISHTI Nationwide Maritime Surveillance Platform  
**Target Coverage:** Entire Indian Coastline (7,516 km), Island Territories, and Configurable Offshore Monitoring Zones  

---

## 1. Architectural Philosophy

1. **Evolution, Not Rebuild**: Preserve and evolve the working FastAPI backend, React dashboard, Leaflet map components, 6-factor scoring formulas, and legal dossier generation.
2. **Three-Tier Geographic Hierarchy**: Explicitly differentiate:
   - **Tier 1: Coastal Monitoring Zones**: Immediate littoral waters (0 to 12 nautical miles territorial sea) adjacent to coastal states.
   - **Tier 2: Configurable Offshore Monitoring Zones**: Priority economic corridors, offshore energy installations (e.g. Mumbai High), tanker transit fairways, and environmentally sensitive areas buffered out to operator-defined distances (e.g. 24, 50, or 100 nm).
   - **Tier 3: Wider Maritime Domain / Full EEZ**: The entire 2.02M km² Exclusive Economic Zone supported as a strategic architecture expansion without mandating full-EEZ compute in initial deployment.
3. **Low-Cost Infrastructure**: Maximize free Copernicus open-access tiers, public global datasets, and efficient persistent storage before introducing expensive managed cloud services.

---

## 2. System Layer Hierarchy

```
┌────────────────────────────────────────────────────────────────────────┐
│               LAYER 1: NATIONAL MARITIME DASHBOARD (SPA)               │
│  - National Overview Map (Leaflet) + 11 Coastal Regional Sectors       │
│  - Configurable Offshore Monitoring Zone Overlay (Custom NM Buffers)   │
│  - Provenance-Segregated Incident Triage Queue & Observation Catalog   │
│  - 6-Factor Suspect Scoreboard & Investigative Draft Dossier Modal     │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ HTTP REST / JSON
┌───────────────────────────────────▼────────────────────────────────────┐
│               LAYER 2: CORE REST API & DOMAIN ENGINE                   │
│  - FastAPI Endpoints: /api/regions, /api/observations, /api/incidents  │
│  - Provenance Enforcement Middleware (live vs synthetic separation)    │
│  - 6-Factor AIS Attribution Scorer (backend/app/scoring/)             │
│  - Multi-Agent Decision Engine & Legal Dossier (backend/app/nugen/)    │
└──────────────────┬─────────────────┬───────────────────┬───────────────┘
                   │                 │                   │
┌──────────────────▼──────────┐ ┌────▼─────────────┐ ┌───▼───────────────┐
│ LAYER 3: SCHEDULED WORKERS  │ │ LAYER 4: DATABASE│ │ LAYER 5: STORAGE  │
│ - Sentinel-1 Catalog Poller │ │ - Incidents      │ │ - Segmented Patch │
│ - SAR Preprocessing Worker  │ │ - Observations   │ │   PNGs & GeoJSON  │
│ - Lagrangian Drift Engine   │ │ - AIS Trajectories│ │ - Legal Dossiers  │
│ - AIS Telemetry Fetcher     │ │ - Durable SQL    │ │ - Local Disk or   │
│ (Cron on VPS / Dedicated)   │ │   (VPS / Managed)│ │   Cloudflare R2   │
└─────────────────────────────┘ └──────────────────┘ └───────────────────┘
```

---

## 3. Geographic Architecture: Authoritative Coastal & Offshore Zones

To prevent inventing arbitrary coordinates, geographic boundaries are anchored to **Survey of India (SOI)** coastal state administrative divisions and **Flanders Marine Institute / UNCLOS** maritime boundary baselines.

### 3.1 The 11 Coastal Surveillance Sectors

| Sector ID | State / Territory | Coast | Littoral Baseline Reference | Major Maritime Fairways & Infrastructure |
| :--- | :--- | :--- | :--- | :--- |
| `IN-GJ` | **Gujarat** | West | Gulf of Kutch to Gulf of Khambhat | Kandla, Mundra, Sikka tanker terminals, Vadinar SPM |
| `IN-MH` | **Maharashtra** | West | Dahanu to Redi | Mumbai Port, JNPT, Mumbai High offshore oil fields |
| `IN-GA` | **Goa** | West | Terekhol River to Talpona River | Mormugao Port, Zuari estuary, iron ore fairways |
| `IN-KA` | **Karnataka** | West | Karwar to Mangalore | New Mangalore Port, Karwar naval base corridor |
| `IN-KL` | **Kerala** | West | Kasaragod to Pozhiyoor | Port of Cochin, SPM Aluva, Lakshadweep Sea corridor |
| `IN-TN` | **Tamil Nadu** | East | Pulicat Lake to Cape Comorin | Chennai, Kamarajar (Ennore), VOC Port (Tuticorin), Palk Strait |
| `IN-AP` | **Andhra Pradesh** | East | Krishnapatnam to Kalingapatnam | Visakhapatnam Port, Gangavaram, KG Basin offshore gas fields |
| `IN-OD` | **Odisha** | East | Gopalpur to Subarnarekha River | Paradip Port, Dhamra Port, Chandipur defense range |
| `IN-WB` | **West Bengal** | East | Digha to Sundarbans (Haldia/Hooghly) | Haldia Dock Complex, Kolkata Port approach fairway |
| `IN-AN` | **Andaman & Nicobar** | Islands | Great Nicobar to North Andaman | Malacca Strait western approach, Six Degree Channel, Port Blair |
| `IN-LD` | **Lakshadweep** | Islands | Minicoy to Chetlat | Nine Degree Channel international tanker shipping route |

### 3.2 Configurable Offshore Monitoring Zones
Rather than fixing arbitrary static bounding boxes, the system supports dynamic offshore buffers:
1. **Territorial Sea Zone (Default)**: 12 nautical miles (~22.2 km) from baseline.
2. **Contiguous & Customs Zone**: 24 nautical miles (~44.4 km) from baseline.
3. **High-Risk Tanker & Offshore Corridor**: Custom buffered polygons encompassing:
   - Mumbai High Offshore Field (bounded polygon ~80 km offshore).
   - International Tanker Route traversing the Nine Degree Channel (Lakshadweep) and Six Degree Channel (Great Nicobar).
4. **Wider Maritime Domain (Future Expansion)**: 200 nautical miles (~370.4 km) full EEZ outer limits, activated selectively when satellite observations cover deeper oceanic sectors.

---

## 4. End-to-End Nationwide Data Flow

```mermaid
flowchart TD
    subgraph ScheduledIngestion [Scheduled Satellite Ingestion]
        CDSE[Copernicus CDSE API] -->|Poll New S1 Passes (Every 6h)| Poller[Scene Discovery Cron]
        Poller -->|New Observation Footprint| ObservationDB[(Observations Table)]
        ObservationDB --> Downloader[Bounding Box Patch Downloader]
    end

    subgraph AnalyticalPipeline [Automated Surveillance Pipeline]
        Downloader --> Preprocess[SAR Radiometric Calib & Speckle Filter]
        Preprocess --> Segment[U-Net CNN Dark Patch Segmentation]
        Segment -->|No Slick| UpdateObsNoSlick[Mark Observation: NO_SLICK]
        Segment -->|Dark Patch Detected| CreateIncident[Create Incident: UNVERIFIED / CANDIDATE]
        CreateIncident --> OceanDrift[Lagrangian Retro-Advection Engine]
        OceanDrift -->|Origin Cone & Window| GFW[GFW AIS Query]
        GFW --> Scorer[6-Factor Attribution Scorer]
        Scorer --> DossierGen[Legal Dossier Engine (Investigative Draft)]
        DossierGen --> CompleteIncident[(Incident Finalized in Database)]
    end

    subgraph Presentation [National Maritime Dashboard]
        CompleteIncident --> API[FastAPI Backend]
        API --> Frontend[React National Dashboard]
        Frontend --> Operator([ICG MRCC Commander / Operator])
        Operator -->|Human Review & Verify| VerifiedStatus[Status: VERIFIED / PROVENANCE: LIVE]
        Operator -->|Export Order| CourtDossier[Investigative Legal Brief under §356J]
    end
```

---

## 5. Technology Choices & Justification

| Layer | Component | Choice | Justification |
| :--- | :--- | :--- | :--- |
| **Frontend** | National SPA | **React 18 + Leaflet** | Zero-cost tile rendering, native GeoJSON layers, responsive component tree. |
| **Backend API** | Web Service | **FastAPI (Python 3.11+)** | High performance, async request handling, automated OpenAPI documentation. |
| **Ingestion Worker** | Scheduled Engine | **Cron Worker on VPS** | Reliable execution for multi-minute satellite queries, NetCDF slicing, and advection simulations without serverless timeout limits. |
| **Database** | Persistent Store | **PostgreSQL (Supabase Free Tier) or SQLite on VPS** | See [`04_DATABASE_AND_SPATIAL_DESIGN.md`](04_DATABASE_AND_SPATIAL_DESIGN.md) for detailed evaluation. |
| **Satellite Data** | SAR Ingestion | **Copernicus CDSE OData API** | Official free Sentinel-1 radar repository with full Indian coastal coverage. |
| **Hydrodynamics** | Advection Drift | **Pure-Python Lagrangian retro-advection** | Avoids heavy Fortran/C compilation failures while rigorously implementing hydrodynamic advection equations. |
| **Vessel AIS** | Telemetry | **Global Fishing Watch API** | Free developer tier with global AIS coverage and transponder gap tracking. |
| **Legal Intelligence** | Dossier Generator | **Local Domain-Aligned Engine** | Zero-latency, 100% deterministic, 0.0% statutory hallucination, free. |
