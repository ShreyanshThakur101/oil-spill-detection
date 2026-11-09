# 03 — COASTAL DATA STRATEGY & EXTERNAL INTEGRATIONS

**Status:** REVISED & EXPANDED  
**Revision Date:** November 8, 2026  
**Scope:** Satellite, oceanographic, meteorological, and maritime vessel tracking datasets for the entire Indian coastline and configurable offshore zones.

---

## 1. External Data Providers Summary Matrix

| Data Provider | Data Type | Official Registration URL | Auth / Key Required | Free Tier & Quotas | Cost (INR) | Existing Status | Priority |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Copernicus Data Space Ecosystem (CDSE)** | Sentinel-1 SAR Level-1 GRD (C-band) | [dataspace.copernicus.eu](https://dataspace.copernicus.eu/) | Free user account + OAuth2 token | Free open access; up to 4 concurrent downloads; unlimited search queries via OData API | **₹0** (Free) | Documented, not coded | **High (Milestone 3)** |
| **Copernicus Marine Service (CMEMS)** | Global Ocean Surface Currents ($u, v$) | [marine.copernicus.eu](https://marine.copernicus.eu/) | Free user account + credentials for Toolbox | Free open access; daily global analysis at 1/12° resolution (~9 km); unlimited API downloads | **₹0** (Free) | Module stubs exist | **High (Milestone 5)** |
| **Copernicus Climate Data Store (CDS)** | ECMWF ERA5 10m Surface Wind Vectors | [cds.climate.copernicus.eu](https://cds.climate.copernicus.eu/) | Free user account + CDS API key | Free open access; hourly reanalysis data; rate-limited queue | **₹0** (Free) | Module stubs exist | **Medium (Milestone 5)** |
| **Global Fishing Watch (GFW)** | AIS vessel positions & disabling/gap events | [globalfishingwatch.org](https://globalfishingwatch.org/our-apis/) | Developer registration + Bearer API Key | Free tier: generous rate limit for research, conservation, and academic prototyping | **₹0** (Free tier) | Code exists in `ais_client.py` (key empty) | **High (Milestone 5)** |
| **OpenStreetMap / CARTO** | Cartographic basemaps & coastline geometries | [carto.com](https://carto.com/basemaps/) / [openstreetmap.org](https://www.openstreetmap.org/) | None required for public OSM/CARTO tile servers | Free public tile access with standard attribution | **₹0** (Free) | Fully implemented in `MapView.jsx` | **Operational** |
| **Indian Coast Guard MRCC Data** | Station coordinates & cutter patrol assets | Public domain NOS-DCP manuals | None | Public coordinates for MRCC Mumbai, Kochi, Chennai, Port Blair | **₹0** (Public) | Implemented in `ICGCuttersLayer.jsx` | **Operational** |

---

## 2. Technical Ingestion Specifications

### 2.1 Copernicus Data Space Ecosystem (CDSE) — Sentinel-1 SAR
- **Purpose**: Systematic, all-weather radar surveillance of Indian coastal waters. C-band SAR penetrates heavy monsoon cloud cover and detects surface oil slicks via capillary-gravity wave damping.
- **Search API**: OData REST API (`https://catalogue.dataspace.copernicus.eu/odata/v1/Products`).
- **Sentinel-1 Revisit Cadence in India**:
  - Revisit time: 6–12 days depending on orbital track (ascending/descending passes over Indian coastal corridors).
  - *Scheduled Ingestion Cadence*: A scheduled background poller running every 6 hours queries for completed acquisitions over the past 24 hours.
- **Storage & Bandwidth Optimization**:
  - Raw Sentinel-1 Level-1 GRD scenes are 1.0–1.6 GB each. Downloading complete scenes nationwide would overwhelm low-cost storage.
  - *Strategy*: Stream spatial subsets or crop localized bounding-box GeoTIFF windows around coastal sectors. Store only the extracted 256x256 pixel patches (~200 KB PNG) and the resulting GeoJSON polygons in the database.

### 2.2 Copernicus Marine Service (CMEMS) — Ocean Currents
- **Purpose**: Ingests surface current vectors ($u, v$ in m/s) to power backward Lagrangian hydrodynamic retro-advection in Arabian Sea, Bay of Bengal, and Indian Ocean waters.
- **Product**: `GLOBAL_ANALYSISFORECAST_PHY_001_024` (Global Ocean Physics Analysis and Forecast).
- **Resolution**: Daily/hourly at 0.083° (~9 km grid), surface layer (depth = 0.49m).
- **Strategy**: Retrieve regional NetCDF subsets bounded to the active incident coordinates ($\pm 1.5^\circ$), eliminating the need to store global hydrodynamic files.

### 2.3 Copernicus Climate Data Store (CDS) — ERA5 Winds
- **Purpose**: Ingests 10m $u$-component and $v$-component surface wind fields to calculate wind drift shear (typically 2–3% of wind speed added to surface current drift).
- **Product**: `reanalysis-era5-single-levels`.
- **Tooling**: Official Python library `cdsapi`. Free with account registration and API key in `~/.cdsapirc`.

### 2.4 Global Fishing Watch (GFW) — AIS Telemetry
- **Purpose**: Identifying candidate commercial vessels, transiting tankers, and detecting deliberate AIS transponder blackouts (Class-A transponder disablement).
- **Endpoints**:
  - Vessel Search: `https://gateway.api.globalfishingwatch.org/v3/vessels`
  - Vessel Events: `https://gateway.api.globalfishingwatch.org/v3/events?event-types=ais-disabling`
  - Vessel Positions: `https://gateway.api.globalfishingwatch.org/v3/vessels/events`
- **Rate-Limit & Coverage Management**:
  - GFW free tier is rate-limited. The system must only query GFW when a candidate slick is confirmed by radar, restricting the query window to $t_{\text{spill}} \pm 4\text{ hours}$ and the spatial bounds to the backward drift origin cone.
  - Vessel trajectories are cached locally in SQLite to prevent duplicate billable calls.

---

## 3. Strict Data Provenance Architecture

To prevent synthetic demonstration data from contaminating operational records, all ingested records must carry explicit provenance metadata:

```
┌────────────────────────────────────────────────────────┐
│                   PROVENANCE TIERS                     │
├───────────────────────┬────────────────────────────────┤
│ LIVE_OBSERVATION      │ Downloaded from CDSE & verified│
│ HISTORICAL_VERIFIED   │ Ground-truth confirmed spill   │
│ SYNTHETIC_DEMO        │ Artificial bench case (1 & 2)  │
│ SIMULATED_ANALYSIS    │ Synthetic drift / test model   │
│ UNVERIFIED_EXTERNAL   │ Raw unconfirmed AIS or alert   │
└───────────────────────┴────────────────────────────────┘
```

The database schema, API serialization, and frontend dashboards enforce these tags, ensuring that `SYNTHETIC_DEMO` cases never leak into operational statistics or legal enforcement briefs.
