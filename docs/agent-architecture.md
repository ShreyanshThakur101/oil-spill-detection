# Agent Architecture & Pipeline Specification

This document provides detailed implementation mechanics for AI coding agents inspecting or extending SAGAR-DRISHTI's core backend pipeline, algorithms, and models.

---

## 1. End-to-End Pipeline Orchestration

The active end-to-end processing pipeline is implemented in [`backend/app/pipeline/orchestrator.py`](../backend/app/pipeline/orchestrator.py) via `run_full_pipeline(case_id: int, db_session: Session)`.

### Stage-by-Stage Flow

```
                      [Case Selected: case_id]
                                  │
                                  ▼
        ┌──────────────────────────────────────────────────┐
        │ Stage 1 & 2: SAR Dark Patch Segmentation (CV)    │
        │ - backend/app/ml/infer.py: detect_slick()        │
        │ - Model: U-Net ResNet-34 (backend/app/ml/)       │
        │ - Fallback: Geo-registered polygon from case.json │
        └─────────────────────────┬────────────────────────┘
                                  │ GeoJSON Polygon + Shape Metrics
                                  ▼
        ┌──────────────────────────────────────────────────┐
        │ Stage 3: Backward Lagrangian Drift Modeling      │
        │ - backend/app/physics/drift_model.py             │
        │ - 200 particles seeded over slick geometry       │
        │ - Retro-advection: 18 hours back (dt = 3 hours)  │
        │ - Output: Origin Convex Hull + Dispersion Cloud  │
        └─────────────────────────┬────────────────────────┘
                                  │ Origin Polygon + Time Window
                                  ▼
        ┌──────────────────────────────────────────────────┐
        │ Stage 4: 6-Factor AIS Attribution Scoreboard    │
        │ - backend/app/scoring/scorer.py: rank_vessels()  │
        │ - Telemetry: demo_cases/case_X/ais_cache_*.json  │
        │ - Features: Proximity, Parity, Temporality,      │
        │             AIS Gap, Deceleration, Prior Type    │
        └─────────────────────────┬────────────────────────┘
                                  │ Ranked Suspects
                                  ▼
        ┌──────────────────────────────────────────────────┐
        │ Stage 5: Nugen Decision Engine & Legal Dossier   │
        │ - backend/app/nugen/multi_agent.py               │
        │ - backend/app/nugen/client.py (SLM API/Fallback) │
        │ - backend/app/nugen/dossier_generator.py         │
        │ - Statutory Output: MSA 1958 §356J & MARPOL Brief│
        └──────────────────────────────────────────────────┘
```

### National Case-Study Layer

The National Intelligence view is backed by `backend/app/routers/demo.py` and `backend/app/demo_data.py`. These modules load five isolated illustrative case bundles from `backend/data/demo/`, expose national coastal search envelopes from `backend/app/regions.py`, and provide a repeatable record refresh. The `/api/demo` path is retained for compatibility; the product interface presents these records as case studies.

Every generated record carries `provenance: "SIMULATED_DEMO"` in the fixture and API payload. The records are excluded from `/api/cases` and the live analysis pipeline so they cannot be mistaken for operational observations. The frontend labels them as illustrative and discloses the synthetic data class in the case summary and methodology note.

---

## 2. SAR Machine Learning (Radar CV)

### Architecture
- **Model**: U-Net with ResNet-34 encoder (`segmentation_models_pytorch`).
- **Input Dimensions**: `(3, 256, 256)` float32 normalized `[0, 1]`.
- **Output Dimensions**: `(1, 256, 256)` logits / sigmoid mask.
- **Checkpoint Path**: `backend/data/models/unet_resnet34_oilspill.pth` (configured via `backend/app/ml/model_utils.py:CHECKPOINT_NAME`).

### Shape Feature Extraction (`backend/app/ml/shape_features.py`)
Computes geometric attributes using [`backend/app/utils/geo.py`](../backend/app/utils/geo.py):
- `area_km2`: Equal-area projected surface area (Lambert Azimuthal Equal Area).
- `perimeter_km`: Projected boundary length.
- `elongation`: Ratio of bounding box major to minor axis.
- `fragment_count`: Number of polygon components.
- `age_class`: Rule-based classification:
  - If `fragment_count > 1` and `elongation > 3.0` -> `"old"`
  - Else if `elongation > 1.8` -> `"aging"`
  - Else -> `"fresh"`

### Fallback Guarantee
If PyTorch model weights are not present on disk, `backend/app/ml/infer.py` and `orchestrator.py` fall back to deterministic benchmark polygons loaded from [`backend/data/demo_cases/`](../backend/data/demo_cases/).

---

## 3. Backward Lagrangian Hydrodynamic Modeling

Implemented in [`backend/app/physics/drift_model.py`](../backend/app/physics/drift_model.py):
1. **Particle Seeding**:
   - Seeds 200 virtual particles inside or within 0.005° of the detected slick GeoJSON polygon using a deterministic random number generator (`np.random.default_rng(seed=42)`).
2. **Backward Advection**:
   - Integrates backwards 18 hours across 6 discrete steps ($\Delta t = 3$ hours, step seconds = 10,800s).
   - Reverses ocean surface current vectors ($u, v$) and incorporates turbulent diffusion ($\sigma = 0.003 \times \sqrt{\text{step} + 1}$).
3. **Origin Cone & Envelope**:
   - Computes the convex hull of all 200 particles at $t - 18\text{h}$.
   - Expands polygon by a hydrodynamic buffer (`buffer(0.008)` degrees) to define the origin cone.
   - Computes max radial distance from centroid as `uncertainty_radius_km`.

---

## 4. 6-Factor AIS Attribution Scoreboard

Implemented in [`backend/app/scoring/features.py`](../backend/app/scoring/features.py) and [`backend/app/scoring/scorer.py`](../backend/app/scoring/scorer.py).

### Feature Formulas & Weights

| Feature | Weight ($w_i$) | Metric & Mathematical Formulation |
| :--- | :--- | :--- |
| **Proximity** | 0.25 | Evaluates minimum Haversine distance ($d_{\text{min}}$) between vessel trajectory points and origin cone centroid. Inside cone ($\le 1.5$ km) yields $0.98$; linearly decays to $0.0$ at 25 km: $\max(0, 1 - d_{\text{min}}/25)$. |
| **Parity** | 0.15 | Angular difference between vessel heading vector and slick polygon minimum bounding box orientation: $\cos(\Delta \theta) = \left\|\cos(\theta_{\text{vessel}} - \theta_{\text{slick}})\right\|$. Score $\ge 0.7$ indicates strong alignment. |
| **Temporality** | 0.20 | Coincidence of vessel transit with origin time window ($t_{\text{spill}} \pm 15$ min). Trajectories intersecting window yield $1.0$; decays to $0.0$ across a 4-hour window. |
| **AIS Blackout Gap** | 0.15 | Intersects GFW `ais-disabling` events with origin window. Gaps $\ge 60$ min yield $1.0$; gaps between 15–60 min scale linearly: $\text{gap\_mins} / 60$. |
| **Speed Anomaly** | 0.10 | Deceleration during transit through spill zone. Drops $\ge 5.0$ knots yield $1.0$; drops between 1–5 knots scale as: $\Delta v / 5.0$. |
| **Vessel Prior** | 0.15 | Static risk based on cargo and bunker capacity: `Tanker` = 1.0, `Cargo/Container` = 0.8, `Bulk Carrier` = 0.6, `Tug/Supply` = 0.4, `Fishing` = 0.2, others = 0.1. |

**Composite Attribution Score:**
$$\text{Score} = \sum_{i=1}^6 w_i \times f_i \quad (\text{Scale } 0.0 \text{ to } 1.0)$$

---

## 5. Nugen SLM Multi-Agent Decision Engine

Implemented in [`backend/app/nugen/`](../backend/app/nugen/):
- **Agent 1 (`RadarGeoJSONParserAgent`)**: Validates radar capillary damping, SAR backscatter drop (-6.4 dB), and calculates surface area.
- **Agent 2 (`PhysicsDriftValidatorAgent`)**: Evaluates hydrodynamic Lagrangian retro-advection vectors and uncertainty envelopes.
- **Agent 3 (`EnforcementDossierAgent`)**: Correlates behavioral telemetry with Indian maritime law and issues enforcement directives.
- **Statutory Enforcement (`legal_engine.py` & `dossier_generator.py`)**:
  - Automatically synthesizes citations for:
    - *MARPOL 73/78 Annex I, Regulation 15* (discharge control from machinery spaces).
    - *Indian Merchant Shipping Act 1958, Section 356E* (prohibition of discharge in Indian EEZ).
    - *Indian Merchant Shipping Act 1958, Section 356J* (statutory detention order).
    - *UNCLOS Articles 194 & 220* (coastal state enforcement jurisdiction).
