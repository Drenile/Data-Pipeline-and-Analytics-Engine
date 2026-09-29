from dataclasses import dataclass
from pathlib import Path

from pipeline.errors import PipelineError
from pipeline.load import validate_table_name


@dataclass(frozen=True)
class Settings:
    data_path: Path = Path("data/Security.csv")
    db_path: Path = Path("db/analytics.db")
    table_name: str = "events"
    label_column: str = "label"
    zscore_threshold: float = 3.0
    # Input limits, so an oversized or hostile file fails fast instead of exhausting memory.
    max_file_bytes: int = 100 * 1024 * 1024
    max_rows: int = 1_000_000

    def __post_init__(self):
        validate_table_name(self.table_name)
        if self.zscore_threshold <= 0:
            raise PipelineError("zscore_threshold must be positive")
        if self.max_file_bytes <= 0 or self.max_rows <= 0:
            raise PipelineError("Input limits must be positive")
