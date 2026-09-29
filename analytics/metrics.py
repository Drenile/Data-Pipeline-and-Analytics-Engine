import pandas as pd

from pipeline.schema import Schema


def core_metrics(df: pd.DataFrame, schema: Schema) -> dict:
    return {
        "row_count": len(df),
        "column_count": len(df.columns),
        "time_ranges": {
            col: {"start": df[col].min(), "end": df[col].max()} for col in schema.timestamps
        },
    }
