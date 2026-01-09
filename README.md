# Data Pipeline and Analytics Engine

## Overview
This project is a modular data pipeline and analytics engine that ingests CSV datasets, infers schema safely, validates data quality, persists data into SQLite, and conditionally runs analytics only when the data supports them.

The system prioritizes correctness, explainability, and defensive design, avoiding misleading analytics when datasets are poorly structured or statistically invalid.

---

## Features
- CSV ingestion with automatic schema inference
- Structural vs semantic schema separation
- Data cleaning and normalization
- SQLite-based persistent storage
- Modular analytics framework
- Graceful handling of invalid or insufficient data
- Clear, structured console output

---

## Directory Structure
.
├── main.py                  # Pipeline entry point
├── pipeline/                # Ingestion and transformation logic
│   ├── ingest.py
│   ├── transform.py
│   ├── load.py
│   ├── schema.py
│   └── semantic_schema.py
├── analytics/               # Analytics modules
│   ├── metrics.py
│   ├── data_quality.py
│   ├── distributions.py
│   ├── label_stats.py
│   └── anomalies.py
├── config/
│   └── settings.py          # Database configuration
├── data/                    # Input datasets
│   ├── FastFood.csv
│   └── Security.csv
├── db/
│   └── analytics.db         # SQLite database
├── requirements.txt
└── .gitignore


---

## Pipeline Architecture
CSV → Ingest → Schema Inference → Clean → SQLite → Analytics → Report

---

## Schema Inference
- **Structural schema**: permissive typing (numeric, categorical, timestamp-like)
- **Semantic schema**: identifies columns safe for analytics

If a valid semantic schema cannot be inferred, analytics are skipped explicitly.

---

## Analytics Implemented

### Core Metrics
- Row count
- Column count

### Data Quality Metrics
- Missing value percentage
- Unique value counts
- Constant column detection

### Numeric Distributions
- Mean
- Standard deviation
- Min / max  
(Computed only when numeric variance exists)

### Label Statistics
- Class distribution (optional)

### Anomaly Detection
- Z-score–based anomaly detection

---

## How to Run
```bash
pip install -r requirements.txt
python main.py

