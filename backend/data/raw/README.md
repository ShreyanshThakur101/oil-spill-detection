# Raw Data Directory

This directory is intended for raw downloaded datasets, satellite imagery (Sentinel-1 GeoTIFFs), environmental NetCDF files (CMEMS ocean currents, ERA5 wind), and AIS trajectory caches.

## Guidelines
* **Do NOT commit large data files to Git.** This folder is gitignored except for documentation and placeholder files.
* Responsible developers should document dataset sources, download scripts, and manual fallback links in their respective sections below.

---

## Person 2 (ML / Detection) Data Sources
* **Dataset:** Kaggle Sentinel-1 Oil Spill Detection Dataset
* **Download Script:** `backend/scripts/download_training_data.py`
* **Expected layout:** `backend/data/raw/kaggle_oil_spill/`

---

## Person 3 (Physics / Scoring) Data Sources
* **CMEMS Current Data:** Downloaded via Copernicus Marine Toolbox for demo case bounding box and time window.
* **ERA5 Wind Data:** Downloaded via CDS API.
* **AIS Data:** Cached query results from Global Fishing Watch (GFW) REST API.
