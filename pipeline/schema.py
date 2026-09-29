from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class Schema:
    """Column roles used to decide which analytics apply."""
    timestamps: list[str]
    numeric: list[str]      # measurable values; excludes booleans and the label
    boolean: list[str]
    categorical: list[str]
    label: str | None


def infer_schema(df: pd.DataFrame, label_column: str) -> Schema:
    label = label_column if label_column in df.columns else None
    timestamps, numeric, boolean, categorical = [], [], [], []

    for col in df.columns:
        if col == label:
            continue
        series = df[col]
        if pd.api.types.is_datetime64_any_dtype(series):
            timestamps.append(col)
        elif pd.api.types.is_bool_dtype(series):
            boolean.append(col)
        elif pd.api.types.is_numeric_dtype(series):
            numeric.append(col)
        else:
            categorical.append(col)

    return Schema(timestamps, numeric, boolean, categorical, label)
