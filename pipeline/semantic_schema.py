import pandas as pd

def detect_timestamp_column(df):
    for col in df.columns:
        parsed = pd.to_datetime(df[col], errors="coerce")
        if parsed.notna().mean() > 0.8:
            return col
    raise ValueError("No timestamp column detected")

def detect_numeric_column(df):
    numeric_cols = df.select_dtypes(include="number")
    for col in numeric_cols.columns:
        if numeric_cols[col].std() > 0:
            return col
    raise ValueError("No suitable numeric column detected")

def detect_category_column(df, exclude_cols):
    for col in df.select_dtypes(include="object").columns:
        if col not in exclude_cols and df[col].nunique() < 50:
            return col
    raise ValueError("No categorical column detected")

def infer_semantic_schema(df):

    #Assign analytic roles to columns.
  
    ts = detect_timestamp_column(df)
    val = detect_numeric_column(df)
    cat = detect_category_column(df, {ts, val})

    return {
        "timestamp": ts,
        "value": val,
        "category": cat
    }

