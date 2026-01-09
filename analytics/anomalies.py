import sqlite3
import pandas as pd

def zscore_anomalies(db_path, table_name, threshold=3.0):
    conn = sqlite3.connect(db_path)
    df = pd.read_sql(f"SELECT * FROM {table_name}", conn)
    conn.close()

    numeric_cols = df.select_dtypes(include="number")
    anomalies = {}

    for col in numeric_cols.columns:
        mean = numeric_cols[col].mean()
        std = numeric_cols[col].std()

        if std == 0 or pd.isna(std):
            continue

        zscores = (numeric_cols[col] - mean) / std
        anomaly_rate = (zscores.abs() > threshold).mean()

        anomalies[col] = anomaly_rate

    return anomalies
