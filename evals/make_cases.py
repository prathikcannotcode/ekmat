"""Writes the 50 synthetic cases and their answer keys.

The answer keys come from the `expect` column below, written by hand from the statute and case law,
not from running the engine. Every name, date and place is fictional. Run: python evals/make_cases.py
"""

import copy
from pathlib import Path

import yaml

ROOT = Path(__file__).parent
KINDS = ["joint_petition", "affidavit_husband", "affidavit_wife", "marriage_proof",
         "address_proof_husband", "address_proof_wife", "photographs"]

BASE = {
    "schema_version": 1,
    "jurisdiction": "delhi",
    "court_district": "South",
    "husband_name": "Ravi Example",
    "wife_name": "Meera Example",
    "marriage_date": "2019-02-14",
    "marriage_district": "South",
    "separation_date": "2023-03-01",
    "last_resided_together_district": "South",
    "husband_residence_district": "New Delhi",
    "wife_residence_district": "South",
    "first_motion_date": "2024-06-10",
    "minor_children": 0,
    "settlement": {"maintenance": True, "stridhan": "returned", "property": True},
    "mediation": {"referred": True, "outcome": "failed"},
    "documents": [{"kind": k, "dated": "2024-06-01"} for k in KINDS],
    "sources": {"marriage_date": {"document": "marriage_proof", "page": 1},
                "separation_date": {"document": "joint_petition", "page": 3}},
}
BASE["documents"][0].update(husband_name="Ravi Example", wife_name="Meera Example")

CHILD_TERMS = {"custody": True, "visitation": True, "child_support": True}


def drop_docs(*kinds):
    return lambda c: c.update(documents=[d for d in c["documents"] if d["kind"] not in kinds])


def doc(kind, **fields):
    return lambda c: next(d for d in c["documents"] if d["kind"] == kind).update(fields)


def merge(dst, patch):
    for k, v in patch.items():
        if isinstance(v, dict) and isinstance(dst.get(k), dict):
            merge(dst[k], v)
        else:
            dst[k] = v


S, D, W = "hma13b.separation_one_year", "hma13b.documents", "hma13b.settlement"
M, J, SM = "hma13b.marriage_one_year", "hma13b.jurisdiction", "hma13b.second_motion_window"
WT, CO = "hma13b.waiver_application_timing", "hma13b.consistency"

# (id, what it tests, patch, extra edits, expected "rule:severity" findings, timeline checks)
CASES = [
    ("C01", "clean base case", {}, [], [], {}),
    ("C02", "jurisdiction from where they last lived together", {"court_district": "North West", "marriage_district": "Jaipur", "last_resided_together_district": "North West", "wife_residence_district": "Gurugram"}, [], [], {}),
    ("C03", "jurisdiction from the wife's residence only", {"court_district": "East", "marriage_district": "Jaipur", "last_resided_together_district": "Noida", "wife_residence_district": "East"}, [], [], {}),
    ("C04", "jurisdiction from the husband's residence only", {"court_district": "West", "marriage_district": "Jaipur", "last_resided_together_district": "Noida", "husband_residence_district": "West", "wife_residence_district": "Gurugram"}, [], [], {}),
    ("C05", "jurisdiction from the place of marriage only", {"court_district": "Central", "marriage_district": "Central", "last_resided_together_district": "Noida", "wife_residence_district": "Gurugram"}, [], [], {}),
    ("C06", "one child, every child term settled", {"minor_children": 1, "settlement": CHILD_TERMS}, [], [], {}),
    ("C07", "two children, every child term settled", {"minor_children": 2, "settlement": CHILD_TERMS}, [], [], {}),
    ("C08", "second motion on the day the window opens", {"second_motion_date": "2024-12-10"}, [], [], {"second_motion_opens": "2024-12-10", "second_motion_closes": "2025-12-10"}),
    ("C09", "second motion on the day the window closes", {"second_motion_date": "2025-12-10"}, [], [], {}),
    ("C10", "stridhan with the wife", {"settlement": {"stridhan": "in_possession"}}, [], [], {}),
    ("C11", "no stridhan claimed", {"settlement": {"stridhan": "none_claimed"}}, [], [], {}),
    ("C12", "pending DV case with a plan", {"pending_cases": [{"kind": "DV"}], "settlement": {"pending_cases_plan": True}}, [], [f"{W}:info"], {}),
    ("C13", "pending s.125 maintenance case with a plan", {"pending_cases": [{"kind": "maintenance_125"}], "settlement": {"pending_cases_plan": True}}, [], [f"{W}:info"], {}),
    ("C14", "waiver application exactly one week after first motion", {"separation_date": "2022-01-01", "waiver_application_date": "2024-06-17"}, [], [], {"waiver_application_from": "2024-06-17", "eighteen_months_of_separation": "2023-07-01"}),
    ("C15", "first motion not yet filed", {"first_motion_date": None}, [], [], {"earliest_first_motion_without_leave": "2024-03-01"}),
    ("C16", "separation exactly one year before first motion", {"separation_date": "2023-06-10"}, [], [], {}),
    ("C17", "marriage and separation exactly one year before first motion", {"marriage_date": "2023-06-10", "separation_date": "2023-06-10"}, [], [], {}),
    ("C18", "six months from 31 August ends on 28 February", {"first_motion_date": "2024-08-31", "second_motion_date": "2025-02-28"}, [], [], {"second_motion_opens": "2025-02-28"}),
    ("C19", "six months from 31 August in a leap year ends on 29 February", {"separation_date": "2022-01-15", "first_motion_date": "2023-08-31", "second_motion_date": "2024-02-29"}, [doc(k, dated="2023-08-01") for k in KINDS], [], {"second_motion_opens": "2024-02-29"}),
    ("C20", "same name, different case and spacing", {}, [doc("affidavit_husband", husband_name="RAVI  EXAMPLE"), doc("affidavit_wife", wife_name="meera example.")], [], {}),
    ("C21", "documents agree on the dates", {}, [doc("marriage_proof", marriage_date="2019-02-14"), doc("affidavit_wife", separation_date="2023-03-01")], [], {}),
    ("C22", "court district typed in lower case", {"court_district": "south"}, [], [], {}),
    ("C23", "never referred to mediation (not a scrutiny defect)", {"mediation": {"referred": False, "outcome": None}}, [], [], {}),
    ("C24", "waiver application filed, second motion within the window anyway", {"waiver_application_date": "2024-06-20", "second_motion_date": "2025-01-10"}, [], [], {}),
    ("C25", "no sources recorded", {"sources": {}}, [], [], {}),
    ("D01", "court district matches no s.19 ground", {"court_district": "Shahdara"}, [], [f"{J}:defect"], {}),
    ("D02", "no s.19 ground stated at all", {"marriage_district": None, "last_resided_together_district": None, "husband_residence_district": None, "wife_residence_district": None}, [], [f"{J}:defect"], {}),
    ("D03", "separation under a year, s.14(1) application pleading exceptional hardship", {"separation_date": "2023-09-01", "s14_leave_application": True, "exceptional_hardship_pleaded": True}, [], [f"{S}:warning"], {}),
    ("D04", "separation under a year, no application", {"separation_date": "2023-09-01"}, [], [f"{S}:warning"], {}),
    ("D05", "filed within a year of marriage, no leave application", {"marriage_date": "2023-09-01", "separation_date": "2023-10-01"}, [], [f"{M}:defect", f"{S}:warning"], {}),
    ("D06", "filed within a year of marriage, leave application pleading exceptional hardship", {"marriage_date": "2023-09-01", "separation_date": "2023-10-01", "s14_leave_application": True, "exceptional_hardship_pleaded": True}, [], [f"{M}:warning", f"{S}:warning"], {}),
    ("D07", "marriage proof missing", {}, [drop_docs("marriage_proof")], [f"{D}:defect"], {}),
    ("D08", "wife's affidavit and photographs missing", {}, [drop_docs("affidavit_wife", "photographs")], [f"{D}:defect"] * 2, {}),
    ("D09", "no documents at all", {"documents": []}, [], [f"{D}:defect"] * 7, {}),
    ("D10", "affidavit dated after the first motion", {}, [doc("affidavit_husband", dated="2024-07-01")], [f"{D}:warning"], {}),
    ("D11", "maintenance not addressed", {"settlement": {"maintenance": False}}, [], [f"{W}:warning"], {}),
    ("D12", "stridhan not addressed", {"settlement": {"stridhan": "not_addressed"}}, [], [f"{W}:warning"], {}),
    ("D13", "one child, no child terms", {"minor_children": 1}, [], [f"{W}:warning"] * 3, {}),
    ("D14", "one child, custody only", {"minor_children": 1, "settlement": {"custody": True}}, [], [f"{W}:warning"] * 2, {}),
    ("D15", "498A pending, no plan", {"pending_cases": [{"kind": "498A"}]}, [], [f"{W}:warning", f"{W}:info"], {}),
    ("D16", "498A pending, plan on file", {"pending_cases": [{"kind": "498A"}], "settlement": {"pending_cases_plan": True}}, [], [f"{W}:info"], {}),
    ("D17", "no children on file, but a DV case involves a child", {"pending_cases": [{"kind": "DV", "involves_child": True}], "settlement": {"pending_cases_plan": True}}, [], [f"{W}:info", f"{W}:warning"], {}),
    ("D18", "wife's name spelt differently in her affidavit", {}, [doc("affidavit_wife", wife_name="Mira Exampel")], [f"{CO}:warning"], {}),
    ("D19", "marriage proof gives another marriage date", {}, [doc("marriage_proof", marriage_date="2019-03-14")], [f"{CO}:warning"], {}),
    ("D20", "husband's affidavit gives another separation date", {}, [doc("affidavit_husband", separation_date="2023-05-01")], [f"{CO}:warning"], {}),
    ("D21", "separation before the marriage", {"separation_date": "2018-01-01"}, [], [f"{CO}:defect"], {}),
    ("D22", "second motion early, no waiver application", {"second_motion_date": "2024-10-01"}, [], [f"{SM}:warning"], {}),
    ("D23", "second motion early, waiver application on file", {"second_motion_date": "2024-10-01", "waiver_application_date": "2024-06-20"}, [], [f"{SM}:warning"], {}),
    ("D24", "second motion after eighteen months", {"second_motion_date": "2026-01-15"}, [], [f"{SM}:warning"], {}),
    ("D25", "waiver application within a week of first motion", {"waiver_application_date": "2024-06-12"}, [], [f"{WT}:warning"], {}),
    ("D26", "separation dated after the first motion", {"separation_date": "2024-07-01"}, [], [f"{CO}:defect"], {}),
    ("D27", "second motion dated before the first motion", {"second_motion_date": "2024-05-01"}, [], [f"{CO}:defect"], {}),
    ("D28", "separation under a year, s.14(1) application pleads no exceptional hardship", {"separation_date": "2023-09-01", "s14_leave_application": True}, [], [f"{S}:warning"], {}),
    ("D29", "filed within a year of marriage, leave application pleads no exceptional hardship", {"marriage_date": "2023-09-01", "separation_date": "2023-10-01", "s14_leave_application": True}, [], [f"{M}:warning", f"{S}:warning"], {}),
]

# Where the severity alone can't tell two messages apart, the answer key also names words the issue must contain.
ISSUE_CONTAINS = {
    "D03": ["and pleads exceptional hardship"],
    "D04": ["No application under the proviso to s.14(1)"],
    "D06": ["and pleads exceptional hardship"],
    "D28": ["does not plead exceptional hardship"],
    "D29": ["does not plead exceptional hardship"],
    "D18": ["differently from the case file"],
    "D26": ["after the first motion"],
    "D27": ["dated before the first motion"],
}


def main() -> None:
    for sub in ("cases", "answers"):
        (ROOT / sub).mkdir(exist_ok=True)
        for old in (ROOT / sub).glob("*.yaml"):
            old.unlink()
    for cid, what, patch, edits, expect, timeline in CASES:
        case = copy.deepcopy(BASE)
        merge(case, copy.deepcopy(patch))
        for edit in edits:
            edit(case)
        case = {"case_id": f"SYNTH-{cid}", **{k: v for k, v in case.items() if v is not None}}
        has_defect = any(e.endswith(":defect") for e in expect)
        answer = {"case_id": case["case_id"], "tests": what, "expected": expect,
                  "status": "DEFECTS_FOUND" if has_defect else "NO_DEFECTS_FOUND_IN_FILE"}
        if timeline:
            answer["timeline"] = timeline
        if cid in ISSUE_CONTAINS:
            answer["issue_contains"] = ISSUE_CONTAINS[cid]
        for sub, data in (("cases", case), ("answers", answer)):
            (ROOT / sub / f"{cid}.yaml").write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")
    print(f"wrote {len(CASES)} cases")


if __name__ == "__main__":
    main()
