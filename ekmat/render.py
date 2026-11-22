"""Markdown for people. JSON is the model's own dump."""

from .models import Report, WaiverBrief


def _cell(s: str | None) -> str:
    return (s or "").replace("|", "\\|")


def report_md(r: Report) -> str:
    status = "Defects found" if r.status == "DEFECTS_FOUND" else "No defects found in the file reviewed"
    out = [f"# Scrutiny report: {r.case_id}", "", f"**{status}.** Jurisdiction: {r.jurisdiction}. Ekmat {r.version}.", ""]
    if r.findings:
        out += ["| # | Severity | Citation | Issue | Source | Waiver route |", "|---|---|---|---|---|---|"]
        for f in r.findings:
            src = ", ".join(x for x in [f.source.document, f.source.page and f"p.{f.source.page}"] if x)
            issue = f.issue + ("" if f.rule_verified else " (rule not yet verified)")
            out.append(f"| {f.id} | {f.severity} | {_cell(f.citation)} | {_cell(issue)} | "
                       f"{_cell(src or ', '.join(f.source.fields))} | {_cell(f.waiver_route)} |")
        out.append("")
    out += ["## Dates", ""] + [f"- {k.replace('_', ' ')}: {v}" for k, v in r.timeline.items()] + [""]
    if r.unverified_rules:
        out += ["## Unverified rules relied on", ""] + [f"- {x}" for x in r.unverified_rules] + [""]
    out += ["## Not checked", ""] + [f"- {x}" for x in r.not_checked] + ["", f"_{r.disclaimer}_", ""]
    return "\n".join(out)


def brief_md(b: WaiverBrief) -> str:
    out = [f"# Waiver brief: {b.case_id}", "", f"Authority: {b.authority}. This brief lists facts. It does not say whether the conditions are met.", ""]
    for c in b.conditions:
        out += [f"## Condition ({c.id})", "", c.text, "", "On file:"] + [f"- {x}" for x in c.facts_on_file]
        if c.facts_missing:
            out += ["", "Missing:"] + [f"- {x}" for x in c.facts_missing]
        out += ["", f"For the court: {c.for_the_court}", ""]
    note = "" if b.local_position_verified else " (not yet verified against the judgment)"
    out += [f"## Delhi High Court position{note}", "", b.local_position, "", f"_{b.disclaimer}_", ""]
    return "\n".join(out)
