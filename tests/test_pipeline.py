import json
import sqlite3

import pandas as pd
import pytest

from config.settings import Settings
from main import main, run_pipeline
from pipeline.errors import PipelineError
from pipeline.ingest import parse_datetime_columns, read_csv
from pipeline.load import save_to_sqlite, validate_table_name
from pipeline.report import to_json
from pipeline.schema import infer_schema


def write_csv(path, text):
    path.write_text(text, encoding="utf-8")
    return path


# ── ingest ────────────────────────────────────────────────

def test_numeric_columns_are_not_parsed_as_dates():
    df = parse_datetime_columns(pd.DataFrame({"port": [443, 80], "size": [0.4, 0.5]}))
    assert pd.api.types.is_numeric_dtype(df["port"])
    assert pd.api.types.is_numeric_dtype(df["size"])


def test_text_dates_are_parsed():
    df = parse_datetime_columns(pd.DataFrame({"ts": ["2024-01-01", "2024-01-02 10:00"], "name": ["a", "b"]}))
    assert pd.api.types.is_datetime64_any_dtype(df["ts"])
    assert not pd.api.types.is_datetime64_any_dtype(df["name"])


def test_rejects_non_csv(tmp_path):
    with pytest.raises(PipelineError, match="Expected a .csv"):
        read_csv(write_csv(tmp_path / "data.txt", "a\n1\n"), max_bytes=1000, max_rows=10)


def test_rejects_missing_file(tmp_path):
    with pytest.raises(PipelineError, match="not found"):
        read_csv(tmp_path / "missing.csv", max_bytes=1000, max_rows=10)


def test_rejects_oversized_file(tmp_path):
    path = write_csv(tmp_path / "big.csv", "a\n" + "1\n" * 100)
    with pytest.raises(PipelineError, match="byte limit"):
        read_csv(path, max_bytes=50, max_rows=1000)


def test_rejects_too_many_rows(tmp_path):
    path = write_csv(tmp_path / "rows.csv", "a\n1\n2\n3\n")
    with pytest.raises(PipelineError, match="row limit"):
        read_csv(path, max_bytes=1000, max_rows=2)


def test_rejects_empty_file(tmp_path):
    with pytest.raises(PipelineError, match="Could not parse"):
        read_csv(write_csv(tmp_path / "empty.csv", ""), max_bytes=1000, max_rows=10)


# ── schema ────────────────────────────────────────────────

def test_schema_separates_label_booleans_and_numbers():
    df = pd.DataFrame({"size": [1.0, 2.0], "syn": [True, False], "label": [0, 1], "proto": ["tcp", "udp"]})
    schema = infer_schema(df, "label")
    assert schema.numeric == ["size"]
    assert schema.boolean == ["syn"]
    assert schema.categorical == ["proto"]
    assert schema.label == "label"


# ── load ──────────────────────────────────────────────────

@pytest.mark.parametrize("name", ["events; DROP TABLE x", "a b", "1abc", "", 'x"', "a" * 65])
def test_invalid_table_names_are_rejected(name):
    with pytest.raises(PipelineError):
        validate_table_name(name)


def test_settings_validate_table_name():
    with pytest.raises(PipelineError):
        Settings(table_name="bad-name")


def test_save_to_sqlite_creates_directory(tmp_path):
    db = tmp_path / "nested" / "out.db"
    save_to_sqlite(pd.DataFrame({"a": [1, 2]}), db, "events")
    with sqlite3.connect(db) as conn:
        assert conn.execute("SELECT COUNT(*) FROM events").fetchone() == (2,)


# ── report ────────────────────────────────────────────────

def test_report_is_strict_json_and_escapes_control_characters():
    text = to_json({"\x1b[31mred": float("nan"), "when": pd.Timestamp("2024-01-01"), "missing": pd.NaT})
    assert "\x1b" not in text
    assert json.loads(text) == {"\x1b[31mred": None, "when": "2024-01-01T00:00:00", "missing": None}


# ── end to end ────────────────────────────────────────────

def test_run_pipeline_end_to_end(tmp_path):
    csv = write_csv(
        tmp_path / "events.csv",
        "ts,bytes,proto,label\n"
        "2024-01-01 00:00,100,tcp,0\n"
        "2024-01-01 00:01,120,udp,0\n"
        "2024-01-01 00:02,9000,tcp,1\n"
        "2024-01-01 00:02,9000,tcp,1\n",  # duplicate, removed by cleaning
    )
    report = run_pipeline(Settings(data_path=csv, db_path=tmp_path / "a.db"))

    assert report["source"]["rows_read"] == 4
    assert report["source"]["rows_after_cleaning"] == 3
    assert report["schema"]["timestamps"] == ["ts"]
    assert report["schema"]["numeric"] == ["bytes"]
    assert report["labels"] == pytest.approx({0: 2 / 3, 1: 1 / 3})
    assert "bytes" in report["distributions"]
    json.loads(to_json(report))


def test_main_returns_error_code_on_bad_input(tmp_path, capsys):
    assert main([str(tmp_path / "missing.csv"), "--db", str(tmp_path / "a.db")]) == 1
    assert capsys.readouterr().out == ""
