"""Amardeep Singh waiver brief: the facts on file for each condition. It never grades a condition."""

from . import __version__
from .engine import RULES_DIR, load_rules, load_yaml
from .models import CaseFile, Report, WaiverBrief, WaiverCondition

SETTLEMENT_HEADS = ["maintenance", "property", "custody", "visitation", "child_support", "pending_cases_plan"]


def build_brief(case: CaseFile, report: Report) -> WaiverBrief:
    w = load_yaml(RULES_DIR / "waiver" / "amardeep.yaml")
    _, local = load_rules(case.jurisdiction)
    fm, sep = case.first_motion_date, case.separation_date
    sep18 = report.timeline["eighteen_months_of_separation"]

    a_on = [f"Separation began {sep}.", f"Eighteen months of separation were reached on {sep18}."]
    if fm:
        a_on.append(f"The first motion is dated {fm}; eighteen months of separation had "
                    f"{'already passed' if sep18 <= fm else 'not passed'} by then.")

    m = case.mediation
    b_on = [f"Referred to mediation: {'yes' if m.referred else 'no'}."]
    if m.outcome:
        b_on.append(f"Mediation outcome on file: {m.outcome.replace('_', ' ')}.")

    s = case.settlement
    covered = [h.replace("_", " ") for h in SETTLEMENT_HEADS if getattr(s, h)]
    c_on = [f"Terms on file: {', '.join(covered) or 'none'}.", f"Stridhan: {s.stridhan.replace('_', ' ')}."]
    c_missing = [f.issue for f in report.findings if f.rule_id == "hma13b.settlement" and f.severity != "info"]

    d_on = [f"Pending cases between the parties: {len(case.pending_cases)}."]
    if fm:
        d_on.insert(0, f"{(fm - sep).days} days between separation and the first motion.")

    facts = {
        "a": (a_on, [] if fm else ["First motion date"]),
        "b": (b_on, [] if m.outcome else ["Mediator's report or outcome"]),
        "c": (c_on, c_missing),
        "d": (d_on, []),
    }
    return WaiverBrief(
        version=__version__,
        case_id=case.case_id,
        authority=w["authority"],
        conditions=[WaiverCondition(id=k, text=v["text"], facts_on_file=facts[k][0], facts_missing=facts[k][1],
                                    for_the_court=v["for_the_court"]) for k, v in w["conditions"].items()],
        local_position=local["local_position"],
        local_position_verified=local["local_position_verified"],
        disclaimer=report.disclaimer,
    )
