import hashlib
import io
import warnings
from pathlib import Path

import pandas as pd

from pipeline.errors import PipelineError

# Share of non-null values that must parse as dates before a text column is treated as a timestamp.
DATETIME_MIN_PARSE_RATE = 0.8


def read_csv(path: Path, max_bytes: int, max_rows: int) -> tuple[pd.DataFrame, str]:
    """Read a CSV within the given limits and return it with the SHA-256 of its bytes."""
    path = Path(path)
    if path.suffix.lower() != ".csv":
        raise PipelineError(f"Expected a .csv file, got '{path.name}'")
    if not path.is_file():
        raise PipelineError(f"Input file not found: {path}")

    # Read once and hash/parse the same bytes, so the digest describes exactly what was analysed.
    with path.open("rb") as f:
        raw = f.read(max_bytes + 1)
    if len(raw) > max_bytes:
        raise PipelineError(f"'{path.name}' exceeds the {max_bytes:,}-byte limit")

    try:
        df = pd.read_csv(io.BytesIO(raw), nrows=max_rows + 1)
    except (pd.errors.ParserError, pd.errors.EmptyDataError, UnicodeDecodeError) as e:
        raise PipelineError(f"Could not parse '{path.name}': {e}") from e
    if len(df) > max_rows:
        raise PipelineError(f"'{path.name}' exceeds the {max_rows:,}-row limit")

    return parse_datetime_columns(df), hashlib.sha256(raw).hexdigest()


def parse_datetime_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Convert text columns that mostly hold dates. Numeric columns are left alone,
    since pandas would otherwise read any number as nanoseconds since 1970."""
    df = df.copy()
    for col in df.columns:
        series = df[col]
        if not (pd.api.types.is_string_dtype(series) or pd.api.types.is_object_dtype(series)):
            continue
        non_null = series.notna().sum()
        if non_null == 0:
            continue
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            parsed = pd.to_datetime(series, errors="coerce", format="mixed")
        if parsed.notna().sum() >= DATETIME_MIN_PARSE_RATE * non_null:
            df[col] = parsed
    return df
