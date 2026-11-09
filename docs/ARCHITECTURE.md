# Oil Spill Detection & Vessel Attribution — Master Architecture

This document provides the foundational engineering and scientific design for the SAGAR-DRISHTI platform. It defines the mathematical and architectural decisions that differentiate the system from existing global platforms (e.g. SkyTruth Cerulean).

---

## 1. Reference Architecture & Scientific Decisions

**Reference Benchmark:** SkyTruth's Cerulean (`SkyTruth/ceruleanserver`, `SkyTruth/cerulean-cloud`, `cerulean.skytruth.org`).

| System Aspect | What Cerulean Does | SAGAR-DRISHTI Decision | Scientific & Practical Justification |
| :--- | :--- | :--- | :--- |
| **SAR Ingestion** | Live global polling of all Sentinel-1 scenes via AWS/GCP event chain. | **Scheduled regional polling via Copernicus CDSE OData API.** | Focuses compute strictly on the Indian EEZ and coastal monitoring sectors. Real-time satellite imagery is physically impossible due to orbital revisits; scheduled discovery matches physical reality. |
| **Slick Detection Model** | Custom instance-segmentation deep model trained at global scale. | **U-Net with ResNet-34 encoder trained on Sentinel-1 SAR dataset.** | Standard, defensible computer vision architecture optimized for dark-patch segmentation and capillary wave damping signature extraction. |
| **Shape/Geometry Features** | In-database PostGIS geometric functions. | **Pure Python evaluation via Shapely and PyProj (LAEA).** | Avoids heavy database infrastructure overhead while delivering millimeter-level geodetic surface area, perimeter, and elongation metrics. |
| **Offshore Platform Attribution** | Distance-decay probability model against fixed global oil platforms. | **Removed from Phase 1.** | No verified, open-access offshore platform dataset exists for Indian littoral waters within initial scope. |
| **AIS Correlation** | Direct Global Fishing Watch API queries. | **Retained & optimized.** | Queries Global Fishing Watch (GFW) API on-demand for candidate vessels within the backward drift origin cone. |
| **Origin Backtracking** | **Cerulean uses a static time window (no hydrodynamic backtracking).** | **Physics-grounded backward Lagrangian particle retro-advection (OpenDrift/Python).** | **Primary scientific point of differentiation.** Advects 200 virtual particles backward in time using regional surface ocean currents and wind drag vectors to determine the exact spatio-temporal release cone ($\pm 15$ minutes). |
| **Vessel Attribution Scoring** | Three independent scores (parity, proximity, temporality) without composite fusion. | **Explainable 6-factor composite attribution score.** | Fuses Proximity (0.25), Parity (0.15), Temporality (0.20), AIS Blackout Gap (0.15), Speed Anomaly (0.10), and Vessel Type Prior (0.15) with natural-language statutory explanations. |
| **Legal Enforcement Intelligence** | None (public environmental awareness tool). | **Nugen Domain-Aligned Maritime Enforcement Engine.** | Synthesizes technical telemetry into court-ready legal dossiers citing MARPOL Annex I Regulation 15 and Indian Merchant Shipping Act 1958 §356E & §356J detention directives. |
| **Deployment Mode** | Heavy multi-cloud Kubernetes & serverless infrastructure. | **Unified, low-cost deployment: Vercel CDN frontend + single Linux VPS backend.** | Highly affordable (< ₹450/month), self-contained, and reliable. |

---

## 2. Mathematical Formulations

### 2.1 Backward Lagrangian Particle Advection
The trajectory of each virtual surface particle $p$ is retro-advected backward in time according to the reversed hydrodynamic surface velocity field:
$$\frac{d\vec{x}_p}{dt} = -\left(\vec{u}_{\text{current}} + \alpha_{\text{wind}}\vec{u}_{\text{wind}}\right) + \vec{\eta}_{\text{diff}}$$
where:
- $\vec{u}_{\text{current}}$ is the surface ocean current vector $(u, v)$ from CMEMS.
- $\vec{u}_{\text{wind}}$ is the 10m surface wind velocity from ECMWF ERA5.
- $\alpha_{\text{wind}} \approx 0.03$ is the surface wind drift factor (3% wind shear).
- $\vec{\eta}_{\text{diff}}$ is turbulent diffusion modeled via random walk: $\sigma = 0.003 \times \sqrt{\text{step} + 1}$.

### 2.2 6-Factor Attribution Score Formulation
$$\text{Score} = \sum_{i=1}^6 w_i \times f_i$$
1. **Proximity ($w_1 = 0.25$)**: $\max\left(0, 1 - \frac{d_{\text{min}}}{25\text{ km}}\right)$, where $d_{\text{min}}$ is the minimum Haversine distance between the vessel track and the backward drift origin cone centroid.
2. **Parity ($w_2 = 0.15$)**: $\left|\cos(\theta_{\text{vessel}} - \theta_{\text{slick\_axis}})\right|$, measuring angular alignment between ship trajectory and slick long-axis.
3. **Temporality ($w_3 = 0.20$)**: Evaluates temporal coincidence of vessel transit with the reconstructed spill release window ($t_{\text{spill}} \pm 15$ min).
4. **AIS Blackout Gap ($w_4 = 0.15$)**: Detects deliberate transponder disablement overlapping the origin cone: $\min\left(1.0, \frac{\text{gap\_minutes}}{60}\right)$.
5. **Speed Anomaly ($w_5 = 0.10$)**: Kinematic deceleration during transit through the spill zone: $\min\left(1.0, \frac{\Delta v_{\text{knots}}}{5.0}\right)$.
6. **Vessel Type Prior ($w_6 = 0.15$)**: Heavy bunker capacity weighting: Tanker = 1.0, Cargo = 0.8, Bulk = 0.6, Tug = 0.4, Fishing = 0.2, Other = 0.1.

---

## 3. Operational Evidence Chain & Human Review Policy
The platform explicitly enforces that:
- **Heuristic attribution scores establish investigative leads, not legal guilt.**
- **Generated enforcement dossiers are investigative drafts.**
- Physical boarding, Oil Record Book Part I inspection, and GC-MS bunker fuel fingerprinting are mandatory prerequisites before formal prosecution under Section 356J of the Indian Merchant Shipping Act 1958.
