import pandas as pd


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Drop fully empty rows and exact duplicate rows."""
    return df.dropna(how="all").drop_duplicates().reset_index(drop=True)
