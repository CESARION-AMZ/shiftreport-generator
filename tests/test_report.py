from pathlib import Path

import pytest

from shiftreport.reader import load_rows
from shiftreport.report import build_html, summarize, write_excel, write_html

EXAMPLE = Path(__file__).resolve().parents[1] / "examples" / "sample_shift_data.csv"


@pytest.fixture
def data():
    return load_rows(EXAMPLE)


def test_summarize_groups_and_totals(data):
    headers, rows = data
    s = summarize(headers, rows, group_by="area", metrics=["units_processed", "errors"])
    assert s.row_count == 12
    keys = {g["key"] for g in s.groups}
    assert keys == {"Empaque", "Linea 1", "Linea 2"}
    total_units = sum(g["sums"]["units_processed"] for g in s.groups)
    assert total_units == s.totals["sums"]["units_processed"]
    assert s.totals["sums"]["errors"] == 38.0


def test_summarize_autodetect_metrics(data):
    headers, rows = data
    s = summarize(headers, rows, group_by="area")
    assert "units_processed" in s.metrics
    assert "area" not in s.metrics


def test_summarize_invalid_column(data):
    headers, rows = data
    with pytest.raises(ValueError):
        summarize(headers, rows, group_by="columna_inexistente")


def test_build_html_contains_data(data):
    headers, rows = data
    s = summarize(headers, rows, group_by="area", metrics=["units_processed"])
    html = build_html(s)
    assert "<table" in html
    assert "Empaque" in html
    assert s.title in html


def test_write_outputs(data, tmp_path):
    headers, rows = data
    s = summarize(headers, rows, group_by="area", metrics=["units_processed", "errors"])
    html_path = write_html(s, tmp_path / "r.html")
    xlsx_path = write_excel(s, rows, headers, tmp_path / "r.xlsx")
    assert html_path.exists() and html_path.stat().st_size > 0
    assert xlsx_path.exists() and xlsx_path.stat().st_size > 0
