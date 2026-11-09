# Deep-SAR Dataset Verification & Preprocessing Review

**Dataset Name:** Deep-SAR Oil Spill Segmentation (Refined)  
**Kaggle Dataset Slug:** `bakhtiyar2222/deep-sar-oil-spill-segmentation-refined`  
**License:** Creative Commons Attribution 4.0 International (CC BY 4.0)  
**Total Download Size:** ~1.26 GB (1,348,697,223 bytes compressed)  
**Evaluation Date:** November 8, 2026  

---

## 1. Dataset Verification & Technical Characteristics

### 1.1 Source & Licensing
- **Origin**: Curated from historical European Space Agency (ESA) Copernicus Sentinel-1 Synthetic Aperture Radar (SAR) acquisitions over global marine shipping corridors and offshore oil drilling zones.
- **License**: CC BY 4.0 (permits sharing, adaptation, commercial and non-commercial research use with appropriate attribution).
- **Download Method**: Scripted via Kaggle CLI: `kaggle datasets download -d bakhtiyar2222/deep-sar-oil-spill-segmentation-refined` using `backend/scripts/download_training_data.py`.

### 1.2 Structure & Formats
- **Directory Layout**:
  ```
  kaggle_oil_spill/
  ├── images/   # Grayscale SAR image crops (.png), 256x256 to 512x512 pixels
  └── masks/    # Binary segmentation masks (.png), matching filenames
  ```
- **Annotation Semantics**:
  - `0` (Black): Background seawater, land, or low-wind calm surface.
  - `255` or `1` (White): Petroleum dark patch / verified oil slick.
- **SAR Acquisition Properties**:
  - Sensor: Sentinel-1 C-band SAR (5.405 GHz).
  - Polarization: Predominantly VV (vertical transmit, vertical receive) and cross-pol VH in Interferometric Wide (IW) swath mode. VV polarization is optimal for marine surface roughness and capillary wave damping detection.

### 1.3 Suitability & Limitations for Indian Coastal Surveillance
- **Compatibility**: Highly compatible. The pixel resolution (~10m to 20m spatial resolution) and speckle characteristics directly match Sentinel-1 Level-1 GRD products acquired over the Arabian Sea and Bay of Bengal.
- **Severe Class Imbalance**: In marine SAR imagery, oil slicks typically occupy less than 2–5% of the total scene area. Using standard Binary Cross-Entropy (BCE) alone leads to models predicting all-zeros (trivial background convergence). Combining BCE with **Dice Loss** (or Focal Loss) is scientifically mandatory to penalize false negatives on small slick polygons.
- **Generalization Caveat**: The dataset contains global incidents (Mediterranean, Gulf of Mexico, North Sea). While dielectric damping physics of petroleum slicks is universal, tropical monsoonal oceanographic features (e.g. river discharge plumes off the Ganges/Hooghly in West Bengal or severe upwelling off the Malabar coast in Kerala) produce natural low-backscatter lookalikes that require Indian coastal validation.

---

## 2. Training Pipeline Review & Preprocessing Alignment

### 2.1 Model Architecture
- **Backbone**: U-Net with ResNet-34 encoder (`segmentation_models_pytorch`).
- **Input Channels**: Model expects 3 input channels (`in_channels=3`). Because Sentinel-1 GRD single-pol imagery is 1-channel grayscale, `backend/app/ml/dataset.py` duplicates the grayscale band into 3 channels (`np.stack([img, img, img])`) to leverage ImageNet pre-trained encoder weights.
- **Output**: 1-channel binary logits.

### 2.2 Loss Function & Class Imbalance
The loss function in `backend/app/ml/train.py` combines BCE and Dice Loss:
$$\mathcal{L}_{\text{total}} = \text{BCEWithLogits}(y_{\text{pred}}, y_{\text{true}}) + \left(1 - \frac{2 |y_{\text{pred}} \cap y_{\text{true}}| + \epsilon}{|y_{\text{pred}}| + |y_{\text{true}}| + \epsilon}\right)$$
This ensures stable gradient flow even when slick pixels represent <1% of the patch.

### 2.3 Preprocessing Consistency Check
- **Training**: Images are min-max normalized to $[0.0, 1.0]$: `(img - min) / (max - min)`.
- **Inference (`backend/scripts/colab_sar_inference.py`)**: Uses the identical min-max normalization on valid non-nodata pixels. This ensures zero training-serving skew.
- **Sliding Window Tiling**: For full Sentinel-1 scenes (~10,000 x 10,000 pixels), a sliding window with $256 \times 256$ tiles and $64$ pixel overlap (25% stride overlap) prevents edge-boundary clipping artifacts.
