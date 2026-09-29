# Data Pipeline and Analytics Engine

## Overview
A modular pipeline that ingests a CSV, infers column roles, cleans the data, stores it in SQLite and produces a JSON analytics report. Each analytic runs only when the data supports it and says why when it is skipped.

The project prioritises correctness, explainability and defensive handling of untrusted input.

---

## Pipeline Architecture
```
CSV → Validate & Read → Parse dates → Clean → Infer schema → SQLite
                                                     ↓
                                     Analytics → JSON report
```

Analytics run on the cleaned in-memory DataFrame. SQLite is the persisted output, so types are not lost in a round trip.

---

## How to Run
```bash
pip install -r requirements.txt
python main.py                                  # analyses data/Security.csv
python main.py data/FastFood.csv -o report.json
python main.py --help
```

| Option | Default | Purpose |
|---|---|---|
| `csv` | `data/Security.csv` | Input file |
| `--db` | `db/analytics.db` | SQLite output |
| `--table` | `events` | Table name (letters, digits, `_` only) |
| `--label-column` | `label` | Column holding class labels |
| `--zscore-threshold` | `3.0` | Anomaly cut-off |
| `--max-file-mb` / `--max-rows` | `100` / `1,000,000` | Input limits |
| `-o`, `--output` | stdout | Write the report to a file |

The report is written to stdout (or `--output`) and logs go to stderr, so `python main.py > report.json` gives clean JSON. The exit code is `1` on invalid input or configuration.

### Tests
```bash
pip install -r requirements-dev.txt
python -m pytest
```

---

## Directory Structure
```
.
├── main.py                 # CLI and pipeline orchestration
├── config/settings.py      # Validated, immutable settings
├── pipeline/
│   ├── ingest.py           # Safe CSV reading and date parsing
│   ├── transform.py        # Cleaning
│   ├── schema.py           # Column role inference
│   ├── load.py             # SQLite persistence
│   ├── report.py           # Strict JSON serialisation
│   └── errors.py           # PipelineError
├── analytics/              # Pure functions: DataFrame + Schema → dict
│   ├── metrics.py
│   ├── data_quality.py
│   ├── distributions.py
│   ├── label_stats.py
│   └── anomalies.py
├── tests/
├── data/                   # Input datasets
├── requirements.txt        # Pinned runtime dependencies
└── requirements-dev.txt
```

---

## Schema Inference
Each column gets one role:
- **timestamps**: text columns where at least 80% of values parse as dates. Numeric columns are never converted.
- **numeric**: measurable values, excluding booleans and the label.
- **boolean**: flags such as one-hot encoded fields.
- **categorical**: everything else.
- **label**: the `--label-column`, if present.

## Analytics
- **Core metrics**: row and column counts, time range per timestamp column
- **Data quality**: missing percentage, unique counts, constant-column detection
- **Distributions**: mean, standard deviation, min and max for numeric columns with variance
- **Label statistics**: class distribution
- **Anomaly detection**: count and rate of rows with |z-score| above the threshold

---

## Security Practices
- **Input limits**: size and row caps, a `.csv` extension check and clean errors for unparseable files.
- **No SQL injection surface**: table names must be plain identifiers, and analytics never build SQL strings.
- **Provenance**: the report records the SHA-256 of the exact bytes analysed.
- **Safe output**: strict JSON (no `NaN`). Escaping stops control characters in CSV data from reaching the terminal.
- **Fail closed**: invalid settings are rejected at start-up, and expected errors exit non-zero without a stack trace.
- **Reproducible dependencies**: pinned versions. Generated files (`db/`, bytecode) are git-ignored.

---

## Future Improvements
- Evaluate anomaly detection against labels (precision / recall)
- Security-specific analytics (port scans, SYN floods)
- Robust detectors (median/MAD, Isolation Forest)
- Dependency scanning with `pip-audit` and `bandit` in CI
