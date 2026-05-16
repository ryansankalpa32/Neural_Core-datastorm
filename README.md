# Data Storm 7.0 — Potential-Based Allocation Model

## Problem Statement

The objective of this challenge is to estimate the latent maximum monthly beverage purchase potential for traditional retail outlets across Sri Lanka for January 2026.

Historical sales are treated as censored demand because observed sales may be limited by operational constraints such as stockouts, delivery caps, or credit limitations.

---

# Project Structure

```text
project/
│
├── data/
│   ├── bronze/
│   ├── silver/
│   ├── gold/
│   ├── rejected/
│   └── external/
│
├── outputs/
│   ├── charts/
│   ├── predictions/
│   └── submission/
│
├── src/
│   ├── data_pipeline/
│   ├── features/
│   ├── models/
│   ├── scraper/
│   └── utils/
│
├── report/
├── presentation/
├── tests/
├── config/
│
├── README.md
├── gemini.md
└── requirements.txt
```

---

# Setup

## 1. Create Virtual Environment

```bash
python -m venv venv
```

### Windows

```bash
venv\Scripts\activate
```

### Linux / Mac

```bash
source venv/bin/activate
```

---

## 2. Install Dependencies

```bash
pip install -r requirements.txt
```

---

# Running the Pipeline

## Step 1 — Add Raw Data

Copy all provided CSV files into:

```text
data/bronze/
```

---

## Step 2 — Run Data Pipeline

```bash
python src/data_pipeline/ingest.py
python src/data_pipeline/clean.py
python src/data_pipeline/transform.py
```

---

## Step 3 — Run POI Scraper

```bash
python src/scraper/poi_scraper.py
```

---

## Step 4 — Build Features

```bash
python src/features/build_features.py
```

---

## Step 5 — Train Model & Generate Predictions

```bash
python src/models/train_model.py
python src/models/predict.py
```

---

# Final Outputs

## Predictions

```text
outputs/predictions/teamname_predictions.csv
```

Required columns:

* Outlet_ID
* Maximum_Monthly_Liters

---

## Report

```text
report/final_report.pdf
```

---

# GenAI Transparency Log

```text
gemini.md
```

---

# Workflow Sequence

## PHASE 1 — PROJECT SETUP (Hour 0–1)

### All Members

1. Clone/open project.
2. Create folder structure.
3. Add raw CSVs into:

```text
data/bronze/
```

4. Check dataset columns.
5. Confirm file names.

### Member 1 Starts

* `src/data_pipeline/ingest.py`
* `src/data_pipeline/clean.py`

### Member 2 Starts

* Inspect datasets.
* Plan feature list.
* Prepare latent demand approach.

### Member 3 Starts

* `src/scraper/poi_scraper.py` setup.
* Report template.

---

## PHASE 2 — DATA CLEANING + POI COLLECTION (Hour 1–3)

### Member 1

1. Build cleaning checks:

   * nulls
   * duplicates
   * invalid coordinates
   * invalid dates
   * negative sales

2. Save rejected records:

```text
data/rejected/
```

3. Save cleaned files:

```text
data/silver/
```

### Member 2

1. Wait for sample cleaned dataset.
2. Prepare feature engineering logic.
3. Prepare latent demand formula.
4. Create:

```text
src/features/build_features.py
```

### Member 3

1. Start POI scraping.

Collect:

* schools
* hospitals
* restaurants
* bus stands
* fuel stations

2. Save:

```text
data/gold/poi_data.csv
```

3. Start simple charts.

---

## PHASE 3 — GOLD DATASET + FEATURES (Hour 3–5)

### Member 1

1. Merge all cleaned datasets.
2. Create:

```text
data/gold/final_dataset.csv
```

3. Send dataset to Member 2.

### Member 2

1. Load:

```text
data/gold/final_dataset.csv
```

2. Merge:

```text
data/gold/poi_data.csv
```

3. Create features:

   * avg_sales
   * historical_max_sales
   * sales_std
   * growth_rate
   * inactive_days
   * poi_score
   * seasonality_score

### Member 3

1. Finish POI dataset.
2. Finish charts/maps.
3. Start `README.md`.
4. Start `gemini.md`.

---

## PHASE 4 — MODELING + REPORT BUILDING (Hour 5–7)

### Member 2

1. Build latent demand logic.
2. Create potential formula.
3. Optional ML refinement.
4. Generate predictions.

Save:

```text
outputs/predictions/teamname_predictions.csv
```

### Member 1

1. Final validation.

2. Check:

   * nulls
   * duplicates
   * dataset consistency

3. Help debugging.

### Member 3

1. Build report sections.
2. Add charts/screenshots.
3. Add architecture diagram.
4. Add GenAI usage section.

---

## PHASE 5 — FINALIZATION (Hour 7–9)

### Member 2

1. Final prediction validation.
2. Check:

   * no negative predictions
   * no nulls
   * no duplicates

### Member 1

1. Cleanup repo.
2. Verify all folders.
3. Final debugging support.

### Member 3

1. Finalize PDF report.
2. Finalize `README.md`.
3. Prepare submission folder.

---

## PHASE 6 — SUBMISSION (Hour 9–10)

### All Members

1. Verify:

   * predictions CSV
   * report PDF
   * repo structure

2. Final package:

```text
outputs/submission/
```

3. Upload:

   * GitHub / ZIP
   * PDF
   * predictions CSV

4. Final sanity check before submission.
