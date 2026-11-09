# SAGAR-DRISHTI Case Study Walkthrough

## Purpose

This walkthrough covers the **National Intelligence** dashboard, the five illustrative case studies, and the **Analysis Pipeline** reference cases. It is written for evaluators, reviewers, and new team members who need a reproducible tour of the product without relying on presentation-only language.

## Data Integrity and Provenance

The five national case studies are **illustrative synthetic scenarios** created to exercise the complete detection, drift, attribution, and investigation workflow. Their observations, vessel tracks, drift results, and investigation records are not verified historical incidents, real satellite acquisitions, confirmed vessel identities, or completed enforcement actions.

Synthetic provenance is retained in the source fixtures and API responses. The interface labels the case studies as illustrative and includes a technical metadata panel with the record class, source identifiers, and intended use. Do not describe these records as operational evidence.

The two **Analysis Pipeline** reference cases are benchmark records used to exercise the same workflow. Treat their figures as analytical scenario outputs unless a separate, verified source is supplied.

---

## 1. Start the Application

Backend:

```bash
cd backend
uv run uvicorn app.main:app --reload --port 8000
```

Frontend:

```bash
cd frontend
npm run dev
```

Open `http://localhost:5173`.

The header identifies **SAGAR-DRISHTI** and exposes the legal dossier, scientific validation, economics, and multi-agent pipeline panels. The primary navigation contains:

- **National Intelligence** — national coastal picture and five case studies.
- **Analysis Pipeline** — benchmark cases and the end-to-end workflow.

---

## 2. National Intelligence Dashboard

Open **National Intelligence**.

The left panel summarises 13 coastal states and Union Territories, including 9 states, 4 Union Territories, and the represented coastline length. Use **All coasts**, **West coast**, **East coast**, and **Islands** to filter the zone list; use the state/UT filter to narrow it further. Zone rectangles are provisional satellite catalog search envelopes, not legal or administrative boundaries.

The centre map shows:

- Coastal zone envelopes, color-coded by coast.
- Five case-study markers.
- The selected case study's slick detections, drift origin envelope, vessel candidates, and investigation alerts.

The right panel contains the **Case Study** selector and **Reset Case Records** control. Reset reloads the five case-study records and is intended for repeatable testing; it does not remove or modify unrelated project cases.

### The five case studies

| Case study | Region | Coast | Primary coordination |
| :--- | :--- | :--- | :--- |
| Mumbai High | Maharashtra | West | MRCC Mumbai |
| Gujarat Offshore Corridor | Gujarat | West | MRCC Gandhinagar / MRCC Mumbai |
| Paradip | Odisha | East | MRCC Paradip / MRCC Chennai |
| Kerala Coast | Kerala | West | MRCC Kochi |
| Andaman & Nicobar | Andaman and Nicobar Islands | Islands | MRCC Port Blair |

Switch cases with the selector, a case-study marker, or a zone card marked **CASE**. The map focuses the selected case; **National view** returns to the full coastal picture.

---

## 3. Review a Case Study

The case-study header shows the active case, region, coast, and primary MRCC. The six summary tiles cover observations, slick detections, vessel candidates, investigations, slick area, and top attribution.

### Overview

The **Case summary** collects the detail a reviewer needs before opening a tab:

- Incident location, including the detection sector and coordinates.
- Observation window with date and time.
- Satellite record: observation count, sensor, and polarization.
- Slick detection count and total area.
- Lead vessel attribution and score.
- Drift reconstruction count and maximum uncertainty radius.
- Investigation status, split into open and under-review records.
- Record class: illustrative / synthetic.

Expand **Technical metadata & provenance** for the case-study ID, surveillance zone, primary MRCC, peak detection confidence, and the provenance statement. The **Satellite observations** card lists each observation's timestamp, sensor, polarization, and footprint. **Priority investigations** summarises the highest-severity records.

### Slick Analysis

Each detection card provides the sector, confidence, detection ID, linked observation, area, perimeter, elongation, and age class.

### Attribution

Vessel candidates are ordered by rank. Each card shows vessel identity, flag, type, MMSI, length, attribution score, AIS gap, speed drop, drift-overlap confidence, and destination. **Focus on map** centres the candidate's position.

### Investigations

Use the status filter to review all, open, or under-review investigations. Each record includes severity, status, report time, description, MRCC, response asset, linked vessel, linked detection, estimated area, and observation. **Focus on map** centres the linked vessel position.

### Drift Analysis

Each reconstruction shows uncertainty radius, particle count, trajectory fixes, estimated origin time, linked detection, current and wind conditions, and the origin window. **Focus origin** fits the map to the drift origin envelope.

The map tooltips identify illustrative detections, drift estimates, vessel tracks, and investigation alerts. The legend repeats the same layer names and retains the provisional-envelope disclaimer.

---

## 4. Analysis Pipeline

Open **Analysis Pipeline** to run the benchmark workflow on a reference case.

1. Select a reference case.
2. Choose **Run Analysis Pipeline**.
3. Review the detection, drift, ranked vessel candidates, confidence panel, and dossier.

The pipeline chain is:

1. SAR dark-patch segmentation and georeferenced slick polygon.
2. Backward Lagrangian drift reconstruction and origin envelope.
3. Six-factor AIS attribution scoring.
4. Confidence and plausibility review.
5. Investigative legal dossier generation.

All generated dossiers remain investigative drafts requiring qualified human review. The interface does not present them as issued enforcement orders.

---

## 5. Technical Differentiation

| Capability | SkyTruth Cerulean | SAGAR-DRISHTI |
| :--- | :--- | :--- |
| **Origin estimation** | Fixed-window heuristic buffer without backward physics simulation. | Lagrangian backward particle drift modeling using hydrodynamic current and wind fields. |
| **AIS scoring and ranking** | Separate metrics without unified explanatory fusion. | Six-factor weighted scoring with human-readable rationale for proximity, heading parity, AIS gaps, speed anomalies, and vessel type. |
| **Deployment** | Multi-cloud enterprise serverless infrastructure. | Self-contained FastAPI + React architecture capable of offline or air-gapped operation. |
| **ML discipline** | Multiple classifiers, including experimental models. | Focused U-Net segmentation where visual detection is required, with physics and rules for drift, attribution, and legal reasoning. |

---

## 6. Review Checklist

- National Intelligence loads with 13 coastal zones and five case-study markers.
- Coast, state/UT, and investigation-status filters work.
- All five case studies load and switch correctly.
- The case summary shows location, observation window, satellite details, slick detection, vessel attribution, drift, and investigation status.
- Slick Analysis, Attribution, Investigations, and Drift Analysis tabs render their records.
- Map layers and focus controls work for detections, vessel positions, and drift origins.
- **Reset Case Records** refreshes the records without affecting unrelated cases.
- No interface text presents synthetic records as verified operational evidence.
