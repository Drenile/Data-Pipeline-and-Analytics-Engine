import argparse
import logging
import sys
from dataclasses import asdict
from pathlib import Path

from analytics.anomalies import zscore_anomalies
from analytics.data_quality import data_quality_metrics
from analytics.distributions import numeric_distributions
from analytics.label_stats import label_distribution
from analytics.metrics import core_metrics
from config.settings import Settings
from pipeline.errors import PipelineError
from pipeline.ingest import read_csv
from pipeline.load import save_to_sqlite
from pipeline.report import to_json
from pipeline.schema import infer_schema
from pipeline.transform import clean_data

log = logging.getLogger("pipeline")


def run_pipeline(settings: Settings) -> dict:
    df, sha256 = read_csv(settings.data_path, settings.max_file_bytes, settings.max_rows)
    rows_read = len(df)
    df = clean_data(df)
    log.info("Read %d rows from %s (%d after cleaning)", rows_read, settings.data_path.name, len(df))

    schema = infer_schema(df, settings.label_column)
    save_to_sqlite(df, settings.db_path, settings.table_name)
    log.info("Saved to %s, table '%s'", settings.db_path, settings.table_name)

    return {
        "source": {
            "file": settings.data_path.name,
            "sha256": sha256,
            "rows_read": rows_read,
            "rows_after_cleaning": len(df),
        },
        "schema": asdict(schema),
        "metrics": core_metrics(df, schema),
        "data_quality": data_quality_metrics(df),
        "distributions": numeric_distributions(df, schema)
            or _skipped("no numeric columns with variance"),
        "labels": label_distribution(df, schema)
            or _skipped(f"no '{settings.label_column}' column"),
        "anomalies": zscore_anomalies(df, schema, settings.zscore_threshold)
            or _skipped("no numeric columns with variance"),
    }


def _skipped(reason: str) -> dict:
    return {"skipped": reason}


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    defaults = Settings()
    parser = argparse.ArgumentParser(description="Ingest a CSV, store it in SQLite and report analytics as JSON.")
    parser.add_argument("csv", nargs="?", type=Path, default=defaults.data_path, help="input CSV file")
    parser.add_argument("--db", type=Path, default=defaults.db_path, help="SQLite database path")
    parser.add_argument("--table", default=defaults.table_name, help="table to write")
    parser.add_argument("--label-column", default=defaults.label_column, help="column holding class labels")
    parser.add_argument("--zscore-threshold", type=float, default=defaults.zscore_threshold)
    parser.add_argument("--max-file-mb", type=float, default=defaults.max_file_bytes / 1024 / 1024)
    parser.add_argument("--max-rows", type=int, default=defaults.max_rows)
    parser.add_argument("-o", "--output", type=Path, help="write the report here instead of stdout")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    args = parse_args(argv)
    try:
        settings = Settings(
            data_path=args.csv,
            db_path=args.db,
            table_name=args.table,
            label_column=args.label_column,
            zscore_threshold=args.zscore_threshold,
            max_file_bytes=int(args.max_file_mb * 1024 * 1024),
            max_rows=args.max_rows,
        )
        report = to_json(run_pipeline(settings))
    except PipelineError as e:
        log.error("%s", e)
        return 1

    if args.output:
        args.output.write_text(report + "\n", encoding="utf-8")
        log.info("Report written to %s", args.output)
    else:
        print(report)
    return 0


if __name__ == "__main__":
    sys.exit(main())
