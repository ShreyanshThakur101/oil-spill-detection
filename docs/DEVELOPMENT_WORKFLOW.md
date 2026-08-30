# Development Workflow & Ownership Guide

This document defines the team collaboration workflow, ownership boundaries, and contribution guidelines for the 3-person hackathon team.

---

## 1. Team Ownership Boundaries

To avoid merge conflicts and ensure parallel execution, each team member has strictly designated ownership areas:

### Person 1 (Repository Owner / Integration Lead)
* `backend/app/main.py`
* `backend/app/config.py`
* `backend/app/database.py`
* `backend/app/models.py`
* `backend/app/schemas.py`
* `backend/app/routers/`
* `backend/app/pipeline/`
* `backend/app/utils/geo.py` (and other shared utilities)
* `backend/tests/test_geo_utils.py`, `backend/tests/test_api.py`
* `frontend/` (all React components, styles, and API clients)
* Repository root configs, CI/CD, and merging PRs

### Person 2 (Detection / ML)
* `backend/app/ml/` (all files: `dataset.py`, `model_utils.py`, `train.py`, `infer.py`, `shape_features.py`)
* `backend/tests/test_detection.py`
* `backend/scripts/download_training_data.py`
* `backend/data/models/README.md` (and training data documentation in `backend/data/raw/README.md`)
* `backend/requirements.txt` (append only under `# --- Person 2 additions ---`)

### Person 3 (Drift Physics & Vessel Scoring)
* `backend/app/physics/` (all files: `environmental_data.py`, `drift_model.py`)
* `backend/app/scoring/` (all files: `ais_client.py`, `features.py`, `scorer.py`)
* `backend/tests/test_drift.py`, `backend/tests/test_scoring.py`
* `backend/data/raw/README.md` (environmental data / AIS documentation section)
* `backend/requirements.txt` (append only under `# --- Person 3 additions ---`)

> **Rule:** Never modify files outside your assigned ownership without coordinating with Person 1 first.

---

## 2. Getting Started (Person 2 & Person 3)

### Step 1: Clone the Repository
```bash
git clone https://github.com/ShreyanshThakur101/oil-spill-detection.git
cd oil-spill-detection
```

### Step 2: Create Your Feature Branch
For Person 2:
```bash
git checkout -b person2/detection
```

For Person 3:
```bash
git checkout -b person3/drift-scoring
```

### Step 3: Set Up Python Environment
```bash
cd backend
python -m venv .venv

# On Windows:
.venv\Scripts\activate

# On macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
```

---

## 3. Pull Request & Merging Workflow

1. **Rebase regularly:** Keep your branch updated with `main`:
   ```bash
   git fetch origin
   git rebase origin/main
   ```
2. **Run tests before committing:**
   ```bash
   pytest backend/tests
   ```
3. **Push branch:**
   ```bash
   git push origin <your-branch-name>
   ```
4. **Open a Pull Request:** Target `main` branch with clear description of module and interface implementation.
5. **Review & Merge:** Person 1 reviews interface conformity, runs tests, and merges.
