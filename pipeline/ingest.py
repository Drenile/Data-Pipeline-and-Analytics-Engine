import pandas as pd
from pipeline.schema import infer_structural_schema
from pipeline.semantic_schema import infer_semantic_schema

def ingest_csv(path: str):
    df = pd.read_csv(path)

    # Attempt datetime parsing
    for col in df.columns:
        try:
            df[col] = pd.to_datetime(df[col])
        except Exception:
            pass

    structural_schema = infer_structural_schema(df)

    try:
        semantic_schema = infer_semantic_schema(df)
    except ValueError as e:
        semantic_schema = None
        print(f"[WARN] Semantic schema not inferred: {e}")

    return df, structural_schema, semantic_schema
