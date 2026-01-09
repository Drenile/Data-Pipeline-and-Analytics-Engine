import sqlite3
import pandas as pd

def label_distribution(db_path, table_name, label_col="label"):
    conn = sqlite3.connect(db_path)
    df = pd.read_sql(f"SELECT * FROM {table_name}", conn)
    conn.close()

    if label_col not in df.columns:
        return None

    return df[label_col].value_counts(normalize=True).to_dict()
    