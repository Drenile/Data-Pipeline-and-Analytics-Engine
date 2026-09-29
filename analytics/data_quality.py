import pandas as pd


def data_quality_metrics(df: pd.DataFrame) -> dict:
    quality = {}
    for col in df.columns:
        unique = df[col].nunique()
        quality[col] = {
            "missing_pct": df[col].isna().mean(),
            "unique_values": unique,
            "is_constant": unique == 1,
        }
    return quality
