"""ekmat scrutinise | rules | eval. Exit codes: 0 no defects or all evals match, 1 defects or eval failures, 2 bad input."""

import argparse
import json
import sys
from pathlib import Path

import yaml
from pydantic import ValidationError

from .engine import load_rules, scrutinise
from .evaluate import run, summary
from .models import CaseFile
from .render import brief_md, report_md
from .waiver import build_brief


def _load_case(path: str) -> CaseFile:
    text = Path(path).read_text(encoding="utf-8")
    data = json.loads(text) if path.endswith(".json") else yaml.safe_load(text)
    return CaseFile(**data)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="ekmat", description="Scrutiny of a mutual consent divorce file. It decides nothing.")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("scrutinise", help="scrutiny report for a case file")
    s.add_argument("case")
    s.add_argument("--waiver", action="store_true", help="add the Amardeep Singh waiver brief")
    s.add_argument("--format", choices=["json", "md"], default="json")
    s.add_argument("--out")
    r = sub.add_parser("rules", help="list the rules loaded for a jurisdiction")
    r.add_argument("--jurisdiction", default="delhi")
    e = sub.add_parser("eval", help="run synthetic cases against their answer keys")
    e.add_argument("--dir", default="evals")
    a = p.parse_args(argv)

    try:
        if a.cmd == "rules":
            rules, _ = load_rules(a.jurisdiction)
            for rule in rules.values():
                print(f"{rule.id}\t{rule.citation}\t{'verified' if rule.verified else 'UNVERIFIED'}")
            return 0
        if a.cmd == "eval":
            results = run(Path(a.dir))
            print(summary(results))
            return 1 if any(d for _, d in results) else 0

        case = _load_case(a.case)
        report = scrutinise(case)
        brief = build_brief(case, report) if a.waiver else None
        if a.format == "md":
            text = report_md(report) + ("\n" + brief_md(brief) if brief else "")
        else:
            out = {"report": report.model_dump(mode="json")}
            if brief:
                out["waiver_brief"] = brief.model_dump(mode="json")
            text = json.dumps(out, indent=2, ensure_ascii=False)
        if a.out:
            Path(a.out).write_text(text, encoding="utf-8")
        else:
            sys.stdout.write(text + "\n")
        return 1 if report.status == "DEFECTS_FOUND" else 0
    except (OSError, ValidationError, ValueError, yaml.YAMLError) as err:
        print(f"ekmat: {err}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
