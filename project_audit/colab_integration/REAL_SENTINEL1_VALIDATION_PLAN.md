# Real Sentinel-1 Scene Ingestion & Validation Plan

**Document Purpose:** Defines the strict, verifiable protocol for testing the complete end-to-end processing pipeline on a genuine Copernicus Sentinel-1 Synthetic Aperture Radar (SAR) acquisition over Indian coastal waters.  
**Target Scenario:** Sentinel-1 C-band SAR Ground Range Detected (GRD) Interferometric Wide (IW) product.  
**Status:** VALIDATION PROTOCOL SPECIFICATION (Pending Live Execution)  
**Date:** November 8, 2026  

---

## 1. Obtaining a Genuine Sentinel-1 Scene

### 1.1 Target Benchmark Coordinates: Kochi Port Approaches (MSC Elsa III Sinking)
- **Geographic Bounds**: $[75.40^\circ\text{E}, 9.20^\circ\text{N}, 76.50^\circ\text{E}, 10.30^\circ\text{N}]$.
- **Incident Date**: May 24–25, 2025.
- **Acquisition Identification**:
  - Orbit: Descending Track.
  - Sensor Platform: Sentinel-1A C-SAR.
  - Product Level: Level-1 GRD (Ground Range Detected, High Resolution).
  - Mode: Interferometric Wide (IW), dual-polarization ($\text{VV} + \text{VH}$).
  - Spatial Resolution: $10\text{m} \times 10\text{m}$ pixel spacing ($20\text{m} \times 22\text{m}$ spatial resolution).

### 1.2 Acquisition Method via Copernicus Data Space Ecosystem (CDSE)
Using the free Copernicus CDSE OData API:
```bash
# 1. Search available products over Kochi bounding box
curl -s "https://catalogue.dataspace.copernicus.eu/odata/v1/Products?\$filter=OData.CSC.Intersects(area=geography'SRID=4326;POLYGON((75.4 9.2, 76.5 9.2, 76.5 10.3, 75.4 10.3, 75.4 9.2))')%20and%20Collection/Name%20eq%20'SENTINEL-1'%20and%20contains(Name,'GRD')" | jq .
```
The full SAFE package is downloaded using free user credentials, and the primary measurement GeoTIFF (`measurement/s1a-iw-grd-vv-*.tiff`) is extracted.

---

## 2. Complete End-to-End Processing & Validation Chain

```
[Raw Sentinel-1 GeoTIFF (VV Band)]
               │
               ▼
┌────────────────────────────────────────────────────────┐
│ STAGE 1: Radiometric & Spatial Preprocessing           │
│ - Radiometric Calibration: DN to Backscatter (σ⁰ dB)   │
│ - Speckle Filtering: 3x3 Lee filter to reduce noise    │
│ - Nodata / Saturated Masking                           │
└──────────────────────┬─────────────────────────────────┘
                       │ Calibrated Backscatter Raster
                       ▼
┌────────────────────────────────────────────────────────┐
│ STAGE 2: Sliding-Window Tiling & U-Net Inference       │
│ - 256x256 window with 64px overlap                     │
│ - Min-max intensity scaling ([0.0, 1.0])               │
│ - Sigmoid activation with 0.5 threshold                │
│ - Overlap blending to eliminate tile-edge seams        │
└──────────────────────┬─────────────────────────────────┘
                       │ Full-Resolution Binary Mask
                       ▼
┌────────────────────────────────────────────────────────┐
│ STAGE 3: Genuine Georeferenced Polygon Extraction      │
│ - rasterio.features.shapes() with native Affine Matrix │
│ - Reprojection to EPSG:4326 (WGS84)                    │
│ - Geodesic surface area in km² (Lambert Azimuthal EA)  │
│ - Minimum area filter (> 0.1 km²)                      │
└──────────────────────┬─────────────────────────────────┘
                       │ Validated GeoJSON Features
                       ▼
┌────────────────────────────────────────────────────────┐
│ STAGE 4: Verification & Provenance Confirmation        │
│ - Compare extracted polygon against SAR quicklook      │
│ - Record: product_id, confidence, IoU, area_km2        │
│ - Tag Provenance: LIVE_OBSERVATION                     │
└────────────────────────────────────────────────────────┘
```

---

## 3. Strict Truthfulness Policy

- **Current State**: The pipeline components have been verified individually on synthetic georeferenced rasters (`backend/tests/test_geospatial_inference.py`).
- **Confirmation Rule**: SAGAR-DRISHTI **will not claim genuine satellite detection capability** until an operator executes this pipeline on an actual downloaded Sentinel-1 scene and visually confirms the polygon matches the radar capillary wave damping signature.
