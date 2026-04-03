# AI-Assisted Bone Fracture Detection System

A web-based diagnostic tool that uses YOLOv8 object detection and classical
computer-vision techniques to localise fracture zones in X-ray images,
quantify fragment displacement, and generate structured clinical PDF reports.

---

## Repository Structure

```
fracture-detection/
│
├── models/
│   ├── __init__.py
│   └── detector.py            # YOLO inference + per-zone uncertainty scoring
│
├── utils/
│   ├── __init__.py
│   ├── image_processing.py    # Canny edge detection + contour shift analysis
│   ├── report_generator.py    # ReportLab PDF builder
│   ├── ai_doctor.py           # (not included) LLM-generated clinical notes
│   └── pdf_styles.py          # (not included) ReportLab font/style registration
│
├── scripts/
│   └── brightness_analysis.py # Offline X-ray brightness sensitivity study
│
├── static/
│   ├── outputs/               # Runtime-generated images and PDFs
│   └── uploads/               # User-uploaded X-ray images
│
├── tests/                     # Unit tests (see Testing section)
│
├── requirements.txt
└── README.md
```

> **Note:** `utils/ai_doctor.py` and `utils/pdf_styles.py` are part of the
> broader web application and are not included in this code excerpt.  Stub
> implementations suitable for isolated testing are described below.

---

## Pipeline Overview

```
X-ray Image
    │
    ▼
[YOLO Inference]  ──────────────────────────────  models/detector.py
    │  detect bounding boxes (conf ≥ 0.25)
    │
    ▼
[Contour Analysis]  ────────────────────────────  utils/image_processing.py
    │  per ROI: Canny edges → two largest contours
    │  → centroid displacement (px / mm)
    │  → Hu-moment shape dissimilarity
    │
    ▼
[Uncertainty Scoring]  (inside detector.py)
    │  U = 0.4·U_model + 0.3·U_image + 0.3·U_geom
    │
    ▼
[PDF Report]  ──────────────────────────────────  utils/report_generator.py
    │  summary table + AI Doctor notes + annotated images
    ▼
  report.pdf
```

---

## Core Modules

### `models/detector.py` — `run_yolo(model_path, image_path)`

Loads a YOLOv8 model, runs inference at 640 px with a confidence threshold of
0.25, and for each detected bounding box:

1. Crops the region of interest (ROI).
2. Calls `analyze_contours` to extract the shift and shape-dissimilarity
   metrics.
3. Computes a composite **uncertainty score** (0–100 %) as a weighted sum of
   three components:

   | Component | Weight | Rationale |
   |-----------|--------|-----------|
   | Model uncertainty `U_model` = 1 − confidence | 0.40 | Directly reflects detector confidence |
   | Image quality `U_image` = 1 − sharpness/100 | 0.30 | Laplacian variance proxy for blur |
   | Geometric uncertainty `U_geom` = 0.5 × shift_norm | 0.30 | Large displacements are harder to measure precisely |

Returns two annotated images and a list of per-zone metric dictionaries.

---

### `utils/image_processing.py` — `analyze_contours(...)`

Performs sub-zone analysis within each YOLO bounding box:

- **Edge detection:** Canny filter (thresholds 50 / 150) on a greyscale crop.
- **Contour ranking:** The two largest contours by area are retained.
- **Shift measurement:** Euclidean distance between the two centroids,
  reported in pixels and millimetres (conversion factor: 0.2646 mm/px at
  96 DPI).
- **Shape dissimilarity:** `cv2.matchShapes` using the I1 Hu-moment metric.
- **Annotation:** Centroid markers, connecting line, and a labelled
  measurement are drawn onto the detailed output image in place.

---

### `utils/report_generator.py` — `create_pdf_report(...)`

Builds a multi-page A4 PDF with ReportLab:

| Page | Content |
|------|---------|
| 1 | Title, date, welcome paragraph, clinic logo |
| 2 | Summary table + per-zone AI Doctor observation cards |
| 3 | Clean annotated X-ray (bounding boxes only) |
| 4 | Detailed annotated X-ray (centroids, shift lines, labels) |

---

### `scripts/brightness_analysis.py` — Offline sensitivity study

Standalone script (not imported by the web app) that generates two
publication figures showing how ±5 / ±10 / ±15 % brightness adjustments
affect both the visual appearance (Figure 1) and the pixel-intensity
distribution (Figure 2) of four representative X-ray images.

---

## Setup

```bash
# 1. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Place your trained YOLO weights at the project root (or update the path)
#    e.g. best.pt

# 4. Run the web application (entry point not included in this excerpt)
#    python app.py
```

---

## Running the Brightness Analysis Script

```bash
# Place test X-ray images in the project root as test.jpg, test2.jpg, ...
python scripts/brightness_analysis.py
# Outputs saved to static/outputs/figure1_image_grid.png
#                   static/outputs/figure2_intensity_curves.png
```

---

## Pixel-to-Millimetre Conversion

All physical measurements assume **96 DPI** screen capture or scanning:

```
1 px = 25.4 mm / 96 ≈ 0.2646 mm
```

If your imaging equipment uses a different DPI, update `px_to_mm` in
`models/detector.py` accordingly.

---

## Testing

Minimal stubs that allow isolated unit testing without the full web
application are shown below.

```python
# tests/stubs.py
def clean_text(text):
    """Passthrough stub for utils.ai_doctor.clean_text."""
    return text

def register_fonts():
    pass

def get_styles():
    from reportlab.lib.styles import getSampleStyleSheet
    return getSampleStyleSheet()
```

Run tests with:
```bash
pytest tests/
```

---

## Citation

If you use this code in your research, please cite the associated paper
(details to be added upon publication).

---

## Licence

This repository is shared for peer review purposes.  All rights reserved
pending publication.
