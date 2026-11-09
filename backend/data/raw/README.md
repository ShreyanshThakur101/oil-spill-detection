# Guidelines for Raw Data and Environmental Inputs

This directory is intended for raw satellite imagery, environmental NetCDF files, and AIS telemetry datasets.

## Guidelines
- Do NOT commit large raw data binaries to Git. This folder is gitignored except for documentation and directory placeholder files.
- Document dataset sources, download procedures, and manual fallback URLs below.

## Data Sources

### 1. Sentinel-1 SAR Training Data
- **Dataset**: Deep-SAR Oil Spill Segmentation (Refined)
- **Source**: Kaggle (`bakhtiyar2222/deep-sar-oil-spill-segmentation-refined`)
- **Format**: Paired grayscale SAR image patches and binary segmentation masks (oil = 255/1, background = 0).
- **Download Utility**: `backend/scripts/download_training_data.py`.

### 2. Environmental Hydrodynamics & Meteorology
- **Copernicus Marine Service (CMEMS)**: Surface ocean current vectors ($u, v$).
- **Copernicus Climate Data Store (CDS)**: ECMWF ERA5 10m neutral surface wind fields.

### 3. Vessel AIS Telemetry
- **Global Fishing Watch (GFW)**: AIS vessel positions and transponder blackout gap events.
