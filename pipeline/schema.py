import pandas as pd

def infer_structural_schema(df: pd.DataFrame) -> dict:
 
    #Identify column types without assuming meaning.
    schema = {
        "timestamps": [],
        "numeric": [],
        "categorical": []
    }

    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            schema["timestamps"].append(col)
        elif pd.api.types.is_numeric_dtype(df[col]):
            schema["numeric"].append(col)
        else:
            schema["categorical"].append(col)

    return schema

