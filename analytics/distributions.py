import sqlite3
import pandas as pd

def numeric_distributions(db_path, table_name):
    conn = sqlite3.connect(db_path)
    df = pd.read_sql(f"SELECT * FROM {table_name}", conn)
    conn.close()

    numeric_cols = df.select_dtypes(include="number")

    stats = {}
    for col in numeric_cols.columns:
        stats[col] = {
            "mean": numeric_cols[col].mean(),
            "std": numeric_cols[col].std(),
            "min": numeric_cols[col].min(),
            "max": numeric_cols[col].max()
        }

    return stats
