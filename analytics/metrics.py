import sqlite3
import pandas as pd

def compute_metrics(db_path, table_name, semantic_schema=None):
    conn = sqlite3.connect(db_path)
    df = pd.read_sql(f"SELECT * FROM {table_name}", conn)
    conn.close()

    metrics = {
        "row_count": len(df),
        "column_count": len(df.columns),
    }

    if semantic_schema:
        ts = semantic_schema["timestamp"]
        val = semantic_schema["value"]

        metrics["time_range"] = {
            "start": str(df[ts].min()),
            "end": str(df[ts].max())
        }
        metrics["value_mean"] = df[val].mean()
        metrics["value_std"] = df[val].std()

    return metrics
