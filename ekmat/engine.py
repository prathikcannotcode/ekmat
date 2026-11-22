"""Deterministic scrutiny of a s.13B case file. No model anywhere in this path.

Legal text lives in rules/*.yaml. This module computes facts and picks which message applies.
"""

import calendar
import unicodedata
from datetime import date, timedelta
from pathlib import Path
from typing import Iterator, Literal, NamedTuple

import yaml

from . import __version__
from .models import CaseFile, Finding, FindingSource, Report, Strict

RULES_DIR = Path(__file__).parent / "rules"
SEVERITY = {
    "defect": "defect",
    "flag_waivable": "warning",
    "flag_requires_leave": "warning",
    "flag_lapsed": "warning",
    "warning": "warning",
    "info": "info",
}


class Message(Strict):
    on_fail: Literal["defect", "flag_waivable", "flag_requires_leave", "flag_lapsed", "warning", "info"]
    text: str
    citation: str | None = None


class Rule(Strict):
    id: str
    citation: str
    verified: bool
    condition: str
    note: str | None = None
    valid_from: date | None = None
    waiver_route: str | None = None
    required_documents: list[str] = []
    messages: dict[str, Message]


class Hit(NamedTuple):
    message: str
    args: dict
    fields: list[str]
    document: str | None = None


def load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def add_months(d: date, months: int) -> date:
    """Calendar months, clamped to month end: 31 Aug + 6 months = 28 or 29 Feb."""
    # shortcut: 29 Feb + 12 months gives 28 Feb; if a court counts it as 1 March, change the clamp here.
    y, m = divmod(d.month - 1 + months, 12)
    y, m = d.year + y, m + 1
    return date(y, m, min(d.day, calendar.monthrange(y, m)[1]))


def _norm(s: str | None) -> str:
    # keep letters, digits and combining marks, so Devanagari vowel signs still count
    return "".join(ch for ch in unicodedata.normalize("NFC", (s or "").casefold())
                   if unicodedata.category(ch)[0] in "LNM")


def _s14(c: CaseFile, with_ground: str, without_ground: str, none: str) -> str:
    """Which s.14(1) proviso message applies: the proviso needs exceptional hardship or depravity pleaded."""
    if not c.s14_leave_application:
        return none
    return with_ground if c.exceptional_hardship_pleaded else without_ground


# --- checks: one per rule id. Each yields the facts; the rule YAML supplies the words. ---

def separation_one_year(c: CaseFile, r: Rule) -> Iterator[Hit]:
    if not c.first_motion_date or c.separation_date > c.first_motion_date:  # the latter is a consistency defect
        return
    reached = add_months(c.separation_date, 12)
    if reached > c.first_motion_date:
        key = _s14(c, "short_with_application", "short_application_without_ground", "short_without_application")
        yield Hit(key, dict(separation=c.separation_date, first_motion=c.first_motion_date, reached=reached),
                  ["separation_date", "first_motion_date"])


def marriage_one_year(c: CaseFile, r: Rule) -> Iterator[Hit]:
    if c.first_motion_date and add_months(c.marriage_date, 12) > c.first_motion_date:
        key = _s14(c, "within_year_with_leave", "within_year_leave_without_ground", "within_year_without_leave")
        yield Hit(key, dict(first_motion=c.first_motion_date, marriage=c.marriage_date),
                  ["marriage_date", "first_motion_date"])


def jurisdiction(c: CaseFile, r: Rule) -> Iterator[Hit]:
    grounds = [c.marriage_district, c.last_resided_together_district,
               c.husband_residence_district, c.wife_residence_district]
    if _norm(c.court_district) not in {_norm(g) for g in grounds if g}:
        yield Hit("no_ground", dict(court=c.court_district, marriage=c.marriage_district or "not stated",
                                    together=c.last_resided_together_district or "not stated",
                                    husband=c.husband_residence_district or "not stated",
                                    wife=c.wife_residence_district or "not stated"),
                  ["court_district", "marriage_district", "last_resided_together_district",
                   "husband_residence_district", "wife_residence_district"])


def second_motion_window(c: CaseFile, r: Rule) -> Iterator[Hit]:
    fm, sm = c.first_motion_date, c.second_motion_date
    if not (fm and sm) or sm < fm:  # a second motion before the first is a consistency defect
        return
    opens, closes = add_months(fm, 6), add_months(fm, 18)
    args = dict(first_motion=fm, second_motion=sm, opens=opens, closes=closes)
    fields = ["first_motion_date", "second_motion_date"]
    if sm < opens:
        key = "early_with_application" if c.waiver_application_date else "early_without_application"
        yield Hit(key, args, fields)
    elif sm > closes:
        yield Hit("late", args, fields)


def waiver_application_timing(c: CaseFile, r: Rule) -> Iterator[Hit]:
    fm, wa = c.first_motion_date, c.waiver_application_date
    if fm and wa and wa < fm + timedelta(days=7):
        yield Hit("too_early", dict(applied=wa, opens=fm + timedelta(days=7), first_motion=fm),
                  ["waiver_application_date", "first_motion_date"])


def documents(c: CaseFile, r: Rule) -> Iterator[Hit]:
    kinds = {d.kind for d in c.documents}
    for need in r.required_documents:
        if need not in kinds:
            yield Hit("missing", dict(document=need), ["documents"], need)
    for d in c.documents:
        if d.kind in r.required_documents and d.dated and c.first_motion_date and d.dated > c.first_motion_date:
            yield Hit("dated_after_filing", dict(document=d.kind, dated=d.dated, first_motion=c.first_motion_date),
                      ["documents", "first_motion_date"], d.kind)


CHILD_HEADS = {"custody": "custody", "visitation": "visitation", "child_support": "child support"}
WITHDRAWABLE = {"DV": "Domestic Violence Act", "maintenance_125": "maintenance (s.125 CrPC, s.144 BNSS)"}


def settlement(c: CaseFile, r: Rule) -> Iterator[Hit]:
    s = c.settlement
    if not s.maintenance:
        yield Hit("maintenance_missing", {}, ["settlement.maintenance"])
    if s.stridhan == "not_addressed":
        yield Hit("stridhan_missing", {}, ["settlement.stridhan"])
    if not s.property:
        yield Hit("property_missing", {}, ["settlement.property"])
    if c.minor_children:
        for head, label in CHILD_HEADS.items():
            if not getattr(s, head):
                yield Hit("child_head_missing", dict(children=c.minor_children, head=label),
                          ["minor_children", f"settlement.{head}"])
    if c.pending_cases and not s.pending_cases_plan:
        yield Hit("pending_plan_missing", {}, ["pending_cases", "settlement.pending_cases_plan"])
    for p in c.pending_cases:
        if p.kind == "498A":
            yield Hit("non_compoundable", {}, ["pending_cases"])
        elif p.kind in WITHDRAWABLE:
            yield Hit("withdrawable", dict(kind=WITHDRAWABLE[p.kind]), ["pending_cases"])
    if not c.minor_children and any(p.involves_child for p in c.pending_cases):
        yield Hit("child_inconsistent", {}, ["minor_children", "pending_cases"])


def consistency(c: CaseFile, r: Rule) -> Iterator[Hit]:
    if c.separation_date < c.marriage_date:
        yield Hit("separation_before_marriage", dict(separation=c.separation_date, marriage=c.marriage_date),
                  ["separation_date", "marriage_date"])
    fm, sm = c.first_motion_date, c.second_motion_date
    if fm and c.separation_date > fm:
        yield Hit("separation_after_first_motion", dict(separation=c.separation_date, first_motion=fm),
                  ["separation_date", "first_motion_date"])
    if fm and sm and sm < fm:
        yield Hit("second_before_first", dict(second_motion=sm, first_motion=fm),
                  ["second_motion_date", "first_motion_date"])
    for d in c.documents:
        for spouse, expected, found in (("husband", c.husband_name, d.husband_name),
                                        ("wife", c.wife_name, d.wife_name)):
            if found and _norm(found) != _norm(expected):
                yield Hit("name_mismatch", dict(document=d.kind, spouse=spouse), [f"{spouse}_name"], d.kind)
        for key, expected, found in (("marriage_date_mismatch", c.marriage_date, d.marriage_date),
                                     ("separation_date_mismatch", c.separation_date, d.separation_date)):
            if found and found != expected:
                yield Hit(key, dict(document=d.kind, found=found, expected=expected),
                          [key.removesuffix("_mismatch")], d.kind)


CHECKS = {
    "hma13b.separation_one_year": separation_one_year,
    "hma13b.marriage_one_year": marriage_one_year,
    "hma13b.jurisdiction": jurisdiction,
    "hma13b.second_motion_window": second_motion_window,
    "hma13b.waiver_application_timing": waiver_application_timing,
    "hma13b.documents": documents,
    "hma13b.settlement": settlement,
    "hma13b.consistency": consistency,
}


def load_rules(jurisdiction: str = "delhi") -> tuple[dict[str, Rule], dict]:
    rules: dict[str, Rule] = {}
    for path in sorted((RULES_DIR / "hma_13b").glob("*.yaml")):
        rule = Rule(**load_yaml(path))
        if rule.id in rules:
            raise ValueError(f"duplicate rule id {rule.id} in {path.name}")
        rules[rule.id] = rule
    local = load_yaml(RULES_DIR / "jurisdictions" / f"{jurisdiction}.yaml")
    for rid, patch in (local.get("overrides") or {}).items():
        if rid not in rules:
            raise ValueError(f"{jurisdiction}.yaml overrides unknown rule {rid}")
        rules[rid] = Rule(**{**rules[rid].model_dump(), **patch})
    if set(rules) != set(CHECKS):
        raise ValueError(f"rules without a check, or checks without a rule: {sorted(set(rules) ^ set(CHECKS))}")
    return rules, local


def timeline(c: CaseFile) -> dict[str, date]:
    t = {
        "earliest_first_motion_without_leave": max(add_months(c.separation_date, 12), add_months(c.marriage_date, 12)),
        "eighteen_months_of_separation": add_months(c.separation_date, 18),
    }
    if c.first_motion_date:
        t["waiver_application_from"] = c.first_motion_date + timedelta(days=7)
        t["second_motion_opens"] = add_months(c.first_motion_date, 6)
        t["second_motion_closes"] = add_months(c.first_motion_date, 18)
    return t


def scrutinise(case: CaseFile) -> Report:
    rules, _ = load_rules(case.jurisdiction)
    common = load_yaml(RULES_DIR / "report.yaml")
    findings: list[Finding] = []
    for rid, check in CHECKS.items():
        rule = rules[rid]
        if rule.valid_from and case.first_motion_date and case.first_motion_date < rule.valid_from:
            continue
        for hit in check(case, rule):
            msg = rule.messages[hit.message]
            src = next((case.sources[f] for f in hit.fields if f in case.sources), None)
            findings.append(Finding(
                id=f"F-{len(findings) + 1:03d}",
                rule_id=rid,
                severity=SEVERITY[msg.on_fail],
                citation=msg.citation or rule.citation,
                issue=msg.text.format(**hit.args),
                waiver_route=rule.waiver_route if msg.on_fail == "flag_waivable" else None,
                source=FindingSource(fields=hit.fields, document=hit.document or (src and src.document),
                                     page=src.page if src and not hit.document else None),
                rule_verified=rule.verified,
            ))
    return Report(
        version=__version__,
        case_id=case.case_id,
        jurisdiction=case.jurisdiction,
        status="DEFECTS_FOUND" if any(f.severity == "defect" for f in findings) else "NO_DEFECTS_FOUND_IN_FILE",
        findings=findings,
        timeline=timeline(case),
        unverified_rules=sorted(rid for rid, r in rules.items() if not r.verified),
        not_checked=common["not_checked"],
        disclaimer=common["disclaimer"],
    )
