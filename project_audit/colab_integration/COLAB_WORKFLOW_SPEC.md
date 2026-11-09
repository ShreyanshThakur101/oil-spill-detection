# Google Colab Compute Worker: Operator Workflow Specification

**Application:** SAGAR-DRISHTI  
**Workload Category:** Prototype Phase Asynchronous GPU Compute  
**Target Environment:** Google Colab Free Tier (NVIDIA T4 GPU)  

---

## 1. Quick Start Guide for Operators

### Step 1: Open Google Colab & Select GPU Runtime
1. Open [colab.research.google.com](https://colab.research.google.com).
2. Create a new notebook or open `sagar_drishti_worker.ipynb`.
3. In the Colab menu: **Runtime -> Change runtime type -> Hardware accelerator -> T4 GPU**.

### Step 2: Mount Google Drive & Clone Repository
Execute in the first Colab cell:
```python
from google.colab import drive
drive.mount('/content/drive')

!git clone https://github.com/ShreyanshThakur101/oil-spill-detection.git /content/oil-spill-detection
%cd /content/oil-spill-detection
!pip install -q segmentation-models-pytorch rasterio opencv-python shapely requests
```

---

## 2. Workload Execution Workflows

### Workload A: Train SAR U-Net & Save Weights
Execute in Colab to train the model and save checkpoints to Google Drive:
```python
# 1. Download Kaggle Deep-SAR dataset (or use uploaded zip)
!python backend/scripts/download_training_data.py

# 2. Run Colab training script
!python backend/scripts/colab_unet_training.py \
    --data-dir backend/data/raw/kaggle_oil_spill \
    --save-dir /content/drive/MyDrive/sagar_drishti_models \
    --epochs 20 \
    --batch-size 8
```
*Result*: Trained model checkpoint `unet_resnet34_oilspill.pth` is saved safely to your Google Drive. Even if the Colab session disconnects, weights persist.

---

### Workload B: Execute SAR Inference & Push to Live Backend
```python
!python backend/scripts/colab_sar_inference.py \
    --image /content/test_patch.png \
    --weights /content/drive/MyDrive/sagar_drishti_models/unet_resnet34_oilspill.pth \
    --zone-id IN-MH \
    --api-url https://sagar-drishti-indol.vercel.app/api \
    --token sagar-drishti-colab-prototype-2026
```
*Result*: The Colab worker runs GPU inference in <2 seconds, converts detected slick pixels to a GeoJSON polygon, and transmits the detection to the SAGAR-DRISHTI backend. The new slick immediately becomes available on the Leaflet dashboard.

---

## 3. Disconnect & Failure Recovery Strategy

1. **Colab Disconnects During Training**:
   - Checkpoints are saved at every epoch where validation loss improves to `/content/drive/MyDrive/sagar_drishti_models/`.
   - On reconnect, the script checks if a checkpoint exists and resumes training.
2. **Network Interruption During API Result Push**:
   - If the backend is unreachable, the inference script automatically dumps the full JSON payload to `colab_result.json` in the Colab workspace.
   - The operator can manually import this file through the backend dashboard without re-running compute.
