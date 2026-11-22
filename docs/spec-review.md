# Kiro's M1 spec: what we keep, what we change

Kiro's spec lives in `.kiro/specs/sahmati-m1/`. This file records where we overrule it. Where the two disagree, this file wins.

Decided on 22 November 2026: the project is named **Ekmat**, because "Sahmati" is too close to Sahamati, the Account Aggregator body. The waiver brief lists facts and doesn't grade them. The eval goldens are hand-written answer keys.

## Kiro got wrong

1. **Amardeep condition (a) is misstated.** Kiro tests "one year since marriage". The judgment's first condition is that the six months under s.13B(2), on top of the year under s.13B(1), have already passed at the first motion. In other words, 18 months of separation at first motion. Kiro's version would show the condition as met for a couple who separated 13 months ago.
2. **The Delhi Full Bench is mangled.** Kiro's `delhi_hc_position` says both waivers run "under the s.14 proviso". *Shiksha Kumari v. Santosh Kumar*, MAT.APP.(F.C.) 111/2025 (Full Bench, 17 Dec 2025), puts the 13B(1) waiver under the proviso to s.14(1) (para 57.1). The 13B(2) waiver stays under Amardeep, and the two are considered independently (para 57.2). The 13B(1) waiver needs exceptional hardship or exceptional depravity, tested on the *Pooja Gupta* considerations, and is "not to be granted merely for the asking" (para 57.4). So a short separation is a waivable gap with a high bar, not a formality. The judgment doesn't call the 13B(1) period "directory"; para 43 uses that word only for 13B(2). This was checked against the court's text on 22 November 2026.
3. **Its requirements contradict its own review.** The review says to use calendar months; the requirements use 365 and 548 days. We use calendar arithmetic everywhere: one year means the same date a year later, and 18 months means the same day 18 months later (clamped to month end).
4. **Severity contradicts itself.** The design example marks a waivable short separation as `defect`. A waivable gap is a `warning` that names its waiver route. `defect` is kept for gaps the registry can't proceed past without a fix.
5. **Kiro's "about 15 documents" for Delhi is unsourced.** We don't adopt it. The checklist follows the Hindu Marriage Rules 1979 (Delhi High Court) instead. Required: the Form G joint petition, proof of marriage (r.4(a)), each spouse's non-collusion affidavit (r.8), and the r.13 affidavit when a s.14 application is made. Address proofs and photographs aren't in the rules, so a missing one is reported as info. The rules were read from a secondary reproduction, so the rule stays `verified: false`.

## Kiro got right, adopted

- Golden outputs are written by hand from the law, before the engine. They're answer keys, not engine output.
- Stridhan is the wife's property. The settlement check asks whether the deed records return or current possession, not whether "stridhan" appears.
- A pending child-related case alongside `children: false` gets flagged as an inconsistency.
- Non-Delhi jurisdictions are rejected in M1, with no silent fallback.
- `schema_version` goes on the case file.
- M1 takes a structured, human-entered case file. No document extraction; the README says so.
- A second motion after 18 months is a `warning` (petition likely needs re-filing), not a jurisdictional bar.

## Changes to the design

- **No pass verdicts anywhere.** Following nodal's rule against saying "compliant", the report's status is `DEFECTS_FOUND` or `NO_DEFECTS_FOUND_IN_FILE`, never `PASS`. Every report carries a disclaimer and a `not_checked` list. That list always includes consent under s.23(1)(bb), fairness of the settlement, children's welfare and reconciliation, which are for the court.
- **The waiver brief states facts and doesn't grade.** Each condition lists the facts on file, the facts missing, and a fixed note on what only the court can assess. Condition (a) is pure date arithmetic, so it states the computed dates and whether 18 months had elapsed. There are no `MET` or `NOT_MET` labels: the brief rule is "lay out the evidence, never decide".
- **The no-recommendation guarantee is structural.** No LLM and no free text: every sentence comes from a rule's YAML or a fixed template, and no model field holds an outcome. A test scans all rule YAML and templates for recommendation phrases ("should be granted", "we recommend", "is eligible for"). This replaces a runtime word scan that would trip on "leave under s.14 may be granted".
- **Every finding has one source shape:** `source: {field, document?, page?}`. A computed date finding cites the case-file fields it used and, where the fact carries one, the document and page.
- **Name matching:** casefold, strip punctuation and spaces, then compare. A mismatch is a `warning`, since transliteration varies.
- **Useful dates:** for a case before first motion, the report gives the earliest first-motion date (one year of separation), the earliest Amardeep waiver application (first motion plus one week) and the second-motion window. These are facts the couple can plan around.
- **Rules carry a `verified` flag**, the same pattern as nodal's catalog. A finding from an unverified rule says so.

## Stack, trimmed for M1

Python 3.12, Pydantic v2, PyYAML. CLI on stdlib `argparse`. Markdown output from plain templates in code. Month arithmetic in a 5-line helper, not `dateutil`. FastAPI, Jinja2 and Typer wait until the milestones that need them. Tests on pytest.

## Severity map

| on_fail | severity |
|---|---|
| defect | defect |
| flag_waivable | warning |
| flag_requires_leave | warning |
| flag_lapsed | warning |
| info | info |
