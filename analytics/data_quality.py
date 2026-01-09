import sqlite3
import pandas as pd

def data_quality_metrics(db_path, table_name):
    conn = sqlite3.connect(db_path)
    df = pd.read_sql(f"SELECT * FROM {table_name}", conn)
    conn.close()

    quality = {}

    for col in df.columns:
        quality[col] = {
            "missing_pct": df[col].isna().mean(),
            "unique_values": df[col].nunique(),
            "is_constant": df[col].nunique() == 1
        }

    return quality
