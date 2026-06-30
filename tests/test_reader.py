from pathlib import Path

import pytest

from shiftreport.reader import _to_number, detect_numeric_columns, load_rows

EXAMPLE = Path(__file__).resolve().parents[1] / "examples" / "sample_shift_data.csv"


def test_to_number_variants():
    assert _to_number(10) == 10.0
    assert _to_number("420") == 420.0
    assert _to_number("1.250,50") == 1250.50
    assert _to_number("") is None
    assert _to_number("Empaque") is None
    assert _to_number(None) is None


def test_load_csv():
    headers, rows = load_rows(EXAMPLE)
    assert "area" in headers
    assert "units_processed" in headers
    assert len(rows) == 12
    assert rows[0]["area"] == "Empaque"


def test_detect_numeric_columns():
    headers, rows = load_rows(EXAMPLE)
    numeric = detect_numeric_columns(headers, rows)
    assert "units_processed" in numeric
    assert "errors" in numeric
    assert "area" not in numeric
    assert "operator" not in numeric


def test_missing_file():
    with pytest.raises(FileNotFoundError):
        load_rows("no_existe.csv")


def test_unsupported_format(tmp_path):
    bad = tmp_path / "data.txt"
    bad.write_text("hola")
    with pytest.raises(ValueError):
        load_rows(bad)
