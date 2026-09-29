import re
import sqlite3
from contextlib import closing
from pathlib import Path

import pandas as pd

from pipeline.errors import PipelineError

_TABLE_NAME = re.compile(r"[A-Za-z_][A-Za-z0-9_]{0,63}")


def validate_table_name(name: str) -> str:
    """Allow only plain identifiers, so a table name can never inject SQL."""
    if not isinstance(name, str) or not _TABLE_NAME.fullmatch(name):
        raise PipelineError(f"Invalid table name {name!r}: use letters, digits and underscores")
    return name


def save_to_sqlite(df: pd.DataFrame, db_path: Path, table_name: str) -> None:
    validate_table_name(table_name)
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with closing(sqlite3.connect(db_path)) as conn:
        df.to_sql(table_name, conn, if_exists="replace", index=False)
