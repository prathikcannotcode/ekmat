import shutil
from datetime import date
from pathlib import Path

import pytest
import yaml

from ekmat.cli import main
from ekmat.engine import RULES_DIR, add_months
from ekmat.evaluate import RECOMMENDATION, run

EVALS = Path(__file__).parent.parent / "evals"


@pytest.mark.parametrize("start, months, end", [
    (date(2024, 8, 31), 6, date(2025, 2, 28)),
    (date(2023, 8, 31), 6, date(2024, 2, 29)),
    (date(2024, 6, 10), 18, date(2025, 12, 10)),
    (date(2023, 3, 1), 12, date(2024, 3, 1)),
    (date(2024, 11, 30), 3, date(2025, 2, 28)),
])
def test_add_months_is_calendar_arithmetic(start, months, end):
    assert add_months(start, months) == end


def test_name_match_keeps_devanagari_vowel_signs():
    from ekmat.engine import _norm
    assert _norm("रव") != _norm("रवि")
    assert _norm("RAVI  Example.") == _norm("ravi example")


@pytest.mark.parametrize("text", [
    "The waiver should be granted.",
    "We recommend that the court proceed.",
    "The couple is eligible for a waiver.",
    "Grant the petition.",
    "It is recommended to wait.",
    "The petitioners are entitled to a decree.",
])
def test_guard_catches_recommendations(text):
    assert RECOMMENDATION.search(text)


@pytest.mark.parametrize("text", [
    "An application for leave under the proviso to s.14(1) is on file.",
    "Whether to waive remains the court's discretion.",
    "s.14(1) bars the court from entertaining the petition without leave.",
])
def test_guard_allows_statutory_language(text):
    assert not RECOMMENDATION.search(text)


def test_rule_text_carries_no_recommendation():
    for path in RULES_DIR.rglob("*.yaml"):
        assert not RECOMMENDATION.search(path.read_text(encoding="utf-8")), path.name


def test_all_cases_match_answer_keys():
    assert [(cid, d) for cid, d in run(EVALS) if d] == []


def test_eval_catches_a_wrong_answer_key(tmp_path):
    shutil.copytree(EVALS / "cases", tmp_path / "cases")
    shutil.copytree(EVALS / "answers", tmp_path / "answers")
    key_path = tmp_path / "answers" / "D01.yaml"
    key = yaml.safe_load(key_path.read_text(encoding="utf-8"))
    key["expected"] = []
    key_path.write_text(yaml.safe_dump(key), encoding="utf-8")
    failed = {cid: d for cid, d in run(tmp_path) if d}
    assert list(failed) == ["SYNTH-D01"]
    assert any("unexpected hma13b.jurisdiction:defect" in x for x in failed["SYNTH-D01"])


def test_cli_exit_codes(tmp_path, capsys):
    assert main(["scrutinise", str(EVALS / "cases" / "C01.yaml")]) == 0
    assert main(["scrutinise", str(EVALS / "cases" / "D01.yaml"), "--waiver", "--format", "md"]) == 1
    out = capsys.readouterr().out
    assert "Defects found" in out and "Waiver brief" in out

    case = yaml.safe_load((EVALS / "cases" / "C01.yaml").read_text(encoding="utf-8"))
    case["jurisdiction"] = "mumbai"
    bad = tmp_path / "mumbai.yaml"
    bad.write_text(yaml.safe_dump(case), encoding="utf-8")
    assert main(["scrutinise", str(bad)]) == 2
    assert main(["scrutinise", str(tmp_path / "missing.yaml")]) == 2
