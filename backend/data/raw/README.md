# Raw Data Directory

This directory is intended for raw downloaded datasets, satellite imagery (Sentinel-1 GeoTIFFs), environmental NetCDF files (CMEMS ocean currents, ERA5 wind), and AIS trajectory caches.

## Guidelines
* **Do NOT commit large data files to Git.** This folder is gitignored except for documentation and placeholder files.
* Responsible developers should document dataset sources, download scripts, and manual fallback links in their respective sections below.

---

## Person 2 (ML / Detection) Data Sources
* **Dataset:** Deep-SAR Oil Spill Segmentation (Refined)
  * URL: https://www.kaggle.com/datasets/bakhtiyar2222/deep-sar-oil-spill-segmentation-refined
  * License: CC BY 4.0
* **Why this dataset:** It provides **paired grayscale SAR images and binary segmentation masks** (oil = white/1, background = black/0), which is exactly the pixel-level supervision the U-Net requires. Be aware that some other "oil spill" Kaggle datasets (e.g. the CSIRO-based `sentinel-1-sar-oil-spill-detection-dataset`) are **classification-only (no masks)** and would require a different training setup — this one was chosen because it supports segmentation directly.
* **Download Script:** `backend/scripts/download_training_data.py` (requires `kaggle` CLI + API token)
* **Manual fallback URL:** https://www.kaggle.com/datasets/bakhtiyar2222/deep-sar-oil-spill-segmentation-refined/download
* **Expected layout after download:** `backend/data/raw/kaggle_oil_spill/`
  ```
  kaggle_oil_spill/
  ├── images/   # grayscale SAR patches (.png)
  └── masks/    # binary segmentation masks (.png), oil=255/1, bg=0
  ```

---

## Person 3 (Physics / Scoring) Data Sources
* **CMEMS Current Data:** Downloaded via Copernicus Marine Toolbox for demo case bounding box and time window.
* **ERA5 Wind Data:** Downloaded via CDS API.
* **AIS Data:** Cached query results from Global Fishing Watch (GFW) REST API.
