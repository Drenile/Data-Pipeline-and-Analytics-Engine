import pandas as pd

from pipeline.schema import Schema


def numeric_distributions(df: pd.DataFrame, schema: Schema) -> dict:
    """Summary statistics for numeric columns that actually vary."""
    stats = {}
    for col in schema.numeric:
        series = df[col]
        if not series.std() > 0:  # also false for NaN
            continue
        stats[col] = {
            "mean": series.mean(),
            "std": series.std(),
            "min": series.min(),
            "max": series.max(),
        }
    return stats
