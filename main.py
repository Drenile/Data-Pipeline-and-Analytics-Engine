import os
from pipeline.ingest import ingest_csv
from pipeline.transform import clean_data
from pipeline.load import load_to_sql
from analytics.metrics import compute_metrics
from config.settings import DB_PATH, TABLE_NAME

DATA_PATH = "data/raw/data.csv"

def ensure_directories():
    os.makedirs("db", exist_ok=True)

def run_pipeline():
    ensure_directories()

    df, structural_schema, semantic_schema = ingest_csv(DATA_PATH)

    print("\nStructural Schema:")
    print(structural_schema)

    print("\nSemantic Schema:")
    print(semantic_schema)

    df = clean_data(df)
    load_to_sql(df, DB_PATH, TABLE_NAME)

    metrics = compute_metrics(DB_PATH, TABLE_NAME, semantic_schema)
    print("\nAnalytics Metrics:")
    print(metrics)

if __name__ == "__main__":
    run_pipeline()
