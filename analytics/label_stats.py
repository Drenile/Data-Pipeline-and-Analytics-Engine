import pandas as pd

from pipeline.schema import Schema


def label_distribution(df: pd.DataFrame, schema: Schema) -> dict:
    """Share of rows per label value, or an empty dict when there is no label column."""
    if schema.label is None:
        return {}
    return df[schema.label].value_counts(normalize=True).to_dict()
