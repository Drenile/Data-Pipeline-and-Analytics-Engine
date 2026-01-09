import os
from pipeline.ingest import ingest_csv
from pipeline.transform import clean_data
from pipeline.load import load_to_sql
from analytics.metrics import compute_metrics
from config.settings import DB_PATH, TABLE_NAME
from analytics.data_quality import data_quality_metrics
from analytics.distributions import numeric_distributions
from analytics.label_stats import label_distribution
from analytics.anomalies import zscore_anomalies

DATA_PATH = "data/Security.csv"


def ensure_directories():
    os.makedirs("db", exist_ok=True)


def section(title):
    print(f"\n{title}")
    print("-" * len(title))


def run_pipeline():
    ensure_directories()

    df, structural_schema, semantic_schema = ingest_csv(DATA_PATH)

    # ─────────────────────────────
    # PIPELINE STATUS
    # ─────────────────────────────
    section("PIPELINE STATUS")

    usable = semantic_schema is not None
    print(f"Dataset usable for analytics: {'YES' if usable else 'NO'}")

    if not usable:
        print("Reason: Insufficient semantic signals detected")

    print(f"Rows ingested: {len(df)}")
    print(f"Columns ingested: {len(df.columns)}")

    # ─────────────────────────────
    # SCHEMA ASSESSMENT
    # ─────────────────────────────
    section("SCHEMA ASSESSMENT")

    print("Structural Schema:")
    print(structural_schema)

    print("\nSemantic Schema:")
    print(semantic_schema if semantic_schema else "Not inferred")

    # ─────────────────────────────
    # LOAD
    # ─────────────────────────────
    df = clean_data(df)
    load_to_sql(df, DB_PATH, TABLE_NAME)

    # ─────────────────────────────
    # CORE METRICS
    # ─────────────────────────────
    section("CORE ANALYTICS METRICS")
    metrics = compute_metrics(DB_PATH, TABLE_NAME, semantic_schema)
    print(metrics)

    # ─────────────────────────────
    # DATA QUALITY
    # ─────────────────────────────
    section("DATA QUALITY SUMMARY")
    dq = data_quality_metrics(DB_PATH, TABLE_NAME)
    print(dq)

    constant_cols = [k for k, v in dq.items() if v.get("is_constant")]
    if constant_cols:
        print("\nConstant columns detected:")
        for col in constant_cols:
            print(f"- {col}")

    # ─────────────────────────────
    # DISTRIBUTIONS
    # ─────────────────────────────
    section("DISTRIBUTION ANALYTICS")
    dist = numeric_distributions(DB_PATH, TABLE_NAME)
    if dist:
        print(dist)
    else:
        print("Skipped — no numeric columns with variance")

    # ─────────────────────────────
    # LABEL ANALYTICS
    # ─────────────────────────────
    section("LABEL ANALYTICS")
    labels = label_distribution(DB_PATH, TABLE_NAME)
    if labels:
        print(labels)
    else:
        print("Skipped — no label column detected")

    # ─────────────────────────────
    # ANOMALY DETECTION
    # ─────────────────────────────
    section("ANOMALY DETECTION")
    anomalies = zscore_anomalies(DB_PATH, TABLE_NAME)
    if anomalies:
        print(anomalies)
    else:
        print("Skipped — no baseline for anomaly detection")


if __name__ == "__main__":
    run_pipeline()

