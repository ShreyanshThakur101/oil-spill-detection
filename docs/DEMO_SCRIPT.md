# Demo Script: Oil Spill Detection & Vessel Attribution Platform

## Overview & Demo Goal
Showcase an operational decision-support tool that takes Sentinel-1 SAR imagery, detects marine oil slicks via CNN instance segmentation, backtracks their trajectory using backward particle drift modeling, and attributes responsibility to candidate vessels by cross-correlating with AIS trajectory data and behavioral anomaly scoring.

---

## Click-by-Click Live Walkthrough

### 1. Launch System
- **Backend API**: `cd backend && uv run uvicorn app.main:app --reload --port 8000`
- **Frontend App**: `cd frontend && npm run dev`
- Open browser at `http://localhost:5173`.

### 2. Case Selection Screen
- **Action**: In the header / case selector bar, select **"Case 1 — 2025 Kerala Coast (MSC Elsa III)"**.
- **Talking Point**:
  > *"We start with a real-world documented bunker spill incident off the coast of Kochi, Kerala. Sentinel-1 SAR captured the slick spreading across active coastal shipping corridors."*

### 3. Running the Attribution Pipeline
- **Action**: Click the primary action button: **"Run Analysis Pipeline"**.
- **What happens behind the scenes**:
  1. **Stage 1 (ml/)**: Ingests the SAR scene, extracts pixel-level segmentation mask, projects to real-world GeoJSON polygon, and computes geometric shape metrics (area, perimeter, elongation ratio, age classification).
  2. **Stage 2 (physics/)**: Seeds a particle cloud on the slick geometry and performs backward drift modeling over 48 hours to estimate the release origin polygon and uncertainty envelope.
  3. **Stage 3 (scoring/)**: Evaluates AIS vessel tracks in the spatial-temporal search window across 6 heuristic features (Proximity, Track Parity, Temporality, AIS Gaps / Disabling events, Speed Anomaly, and Vessel Type Priors).
  4. Stores full audit trail in SQLite and returns unified JSON to the dashboard.

### 4. Exploring the Interactive Map
- **Action**: Zoom in on the map.
  - Point out the **Dark Red Polygon** (Detected Slick geometry).
  - Point out the **Translucent Blue Polygon & Cloud** (Backward drift estimated release origin).
  - Point out the **Colored LineStrings** (Vessel AIS tracks).
- **Talking Point**:
  > *"Notice the backward trajectory advection. While Cerulean uses a fixed time window, our physics-grounded backtracking isolates where the discharge actually occurred 24 to 48 hours earlier."*

### 5. Reviewing the Ranked Suspect Panel
- **Action**: Click on the #1 ranked suspect vessel (**MT OCEAN PIONEER**, Tanker, Final Score: 0.82 / 82%).
  - Highlight the plain-English explanation:
    > *"Passed in close proximity to the backward drift origin; Significant AIS signal transmission gap overlapping the release window; Course aligns strongly with the detected slick long-axis orientation; Vessel classification (Tanker) carries an elevated prior likelihood."*
  - Demonstrate clicking secondary suspects (e.g. MV PACIFIC BREEZE, FV SEA FALCON) and observe lower attribution confidence.

### 6. Decision Support & Confidence Indicator
- **Action**: Point to the **Confidence & Plausibility Panel**.
  - Show Detection Confidence (89%), Origin Uncertainty Radius (6.2 km), and Slick Age ("Fresh").
  - Emphasize the platform disclaimer: *"Decision-support attribution tool, not definitive legal proof."*

---

## Honest Differentiation: "vs. SkyTruth Cerulean"

| Capability | SkyTruth Cerulean | Our Solution |
| :--- | :--- | :--- |
| **Origin Estimation** | Fixed-window heuristic buffer without backward physics simulation. | **Lagrangian backward particle drift modeling** utilizing hydrodynamic ocean current & wind fields. |
| **AIS Scoring & Ranking** | 3 disparate metrics without unified explanatory fusion. | **6-feature weighted heuristic with human-readable rationale** explaining proximity, heading parity, AIS gap events, and speed anomalies. |
| **Deployment Complexity** | Multi-cloud enterprise serverless infrastructure (AWS + GCP + Pulumi). | **Single self-contained FastAPI + React architecture** capable of complete offline air-gapped demo execution. |
| **ML Discipline** | Multiple neural networks including experimental classifiers. | **Focused CNN U-Net only where visual segmentation is genuinely required**, avoiding unvalidated ML models where physics/rules are superior. |
