# Oil Spill Detection & Vessel Attribution

A decision-support system that combines satellite Synthetic Aperture Radar (SAR) imagery, physics-based backward drift modeling, and AIS vessel tracking to detect marine oil spills and attribute potential source vessels.

## Team Structure

* **Person 1** — Repository Owner / Backend API / Frontend / Integration Lead
* **Person 2** — Detection Module / Machine Learning (SAR Oil-Slick Segmentation)
* **Person 3** — Drift Modeling & Vessel Scoring (Lagrangian Physics & AIS Ranking)

## Repository Structure

```text
oil-spill-detection/
├── backend/
│   ├── app/
│   │   ├── ml/          # Person 2: SAR segmentation model (U-Net)
│   │   ├── physics/     # Person 3: Backward drift simulation (OpenDrift)
│   │   ├── scoring/     # Person 3: AIS ingestion and vessel scoring heuristics
│   │   ├── pipeline/    # Person 1: End-to-end pipeline orchestrator
│   │   ├── routers/     # Person 1: FastAPI route handlers
│   │   └── utils/       # Shared utilities (geometry, logging)
│   ├── data/            # Demo cases, raw datasets, model weights
│   ├── scripts/         # Data download and utility scripts
│   └── tests/           # Unit and integration test suite
├── frontend/            # Person 1: React + Leaflet decision-support UI
└── docs/                # Architecture and development handoff documentation
```

## Development Workflow

1. Clone `main` branch: `git clone https://github.com/ShreyanshThakur101/oil-spill-detection.git`
2. Create your assigned feature branch (e.g., `git checkout -b person2/detection` or `git checkout -b person3/drift-scoring`).
3. Work only inside your assigned modules and directories.
4. Commit changes with clear, descriptive commit messages.
5. Push your feature branch to GitHub.
6. Open a Pull Request against `main`.
7. Person 1 reviews, tests, and merges.

For detailed branch and file ownership rules, see [docs/DEVELOPMENT_WORKFLOW.md](docs/DEVELOPMENT_WORKFLOW.md).

## Setup

Setup instructions: TBD (see [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for architecture and tech stack details).
