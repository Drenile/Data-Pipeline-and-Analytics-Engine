import pandas as pd

from pipeline.schema import Schema


def zscore_anomalies(df: pd.DataFrame, schema: Schema, threshold: float = 3.0) -> dict:
    """Per numeric column, the count and share of rows whose |z-score| exceeds the threshold."""
    anomalies = {}
    for col in schema.numeric:
        series = df[col]
        std = series.std()
        if not std > 0:  # also false for NaN
            continue
        flagged = ((series - series.mean()) / std).abs() > threshold
        anomalies[col] = {"count": int(flagged.sum()), "rate": flagged.mean()}
    return anomalies
