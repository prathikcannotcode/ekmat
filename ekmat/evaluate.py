"""Runs the synthetic cases against hand-written answer keys, plus the hard checks that hold for every case."""

import re
from collections import Counter
from pathlib import Path

from .engine import load_yaml, scrutinise
from .models import CaseFile
from .waiver import build_brief

# Phrases that would turn a scrutiny into a decision. Positive-controlled in tests/test_guard.py.
RECOMMENDATION = re.compile(
    r"should (not )?be (granted|refused|allowed|dismissed|rejected|waived)"
    r"|\bwe (recommend|advise)|\bis recommended|\brecommend(s|ed)? (that|the|granting|refusing)"
    r"|\b(is|are) eligible for|\b(is|are) entitled to (a |the )?(decree|divorce|waiver)"
    r"|\b(grant|refuse|allow|reject|dismiss) the (petition|waiver|divorce|decree|application)",
    re.IGNORECASE,
)


def hard_check(case: CaseFile) -> list[str]:
    report = scrutinise(case)
    brief = build_brief(case, report)
    problems = [f"{f.id} has no citation or source" for f in report.findings if not (f.citation and f.source.fields)]
    for name, text in (("report", report.model_dump_json()), ("brief", brief.model_dump_json())):
        if m := RECOMMENDATION.search(text):
            problems.append(f"{name} contains a recommendation: {m.group(0)!r}")
    return problems


def run(root: Path) -> list[tuple[str, list[str]]]:
    results = []
    for case_path in sorted((root / "cases").glob("*.yaml")):
        case = CaseFile(**load_yaml(case_path))
        key = load_yaml(root / "answers" / case_path.name)
        report = scrutinise(case)
        got = Counter(f"{f.rule_id}:{f.severity}" for f in report.findings)
        want = Counter(key.get("expected") or [])
        diffs = [f"missing {k} x{n}" for k, n in (want - got).items()]
        diffs += [f"unexpected {k} x{n}" for k, n in (got - want).items()]
        if key.get("status") and key["status"] != report.status:
            diffs.append(f"status {report.status}, expected {key['status']}")
        issues = " ".join(f.issue for f in report.findings)
        diffs += [f"no issue contains {s!r}" for s in key.get("issue_contains") or [] if s not in issues]
        for k, v in (key.get("timeline") or {}).items():
            if str(report.timeline.get(k)) != str(v):
                diffs.append(f"timeline.{k} {report.timeline.get(k)}, expected {v}")
        results.append((case.case_id, diffs + hard_check(case)))
    return results


def summary(results: list[tuple[str, list[str]]]) -> str:
    lines = [f"{cid}  {'PASS' if not d else 'FAIL'}  {len(d)}" + "".join(f"\n    {x}" for x in d) for cid, d in results]
    failed = sum(1 for _, d in results if d)
    return "\n".join(lines + [f"\n{len(results) - failed}/{len(results)} cases match their answer keys."])
