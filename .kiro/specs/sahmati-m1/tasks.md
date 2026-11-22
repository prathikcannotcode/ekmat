# Sahmati M1 — Implementation Tasks

Tasks are ordered for sequential execution. Each task is small enough to complete and test in one sitting. A task is done when its stated verification passes.

Dependencies are listed where a task's output is a prerequisite for another.

---

## TASK-01 — Project scaffold and pyproject.toml

**Requires:** nothing  
**Satisfies:** REQ-12 (CLI entry point exists)

Create the top-level package structure:

```
sahmati/
  __init__.py
  __main__.py          # stub: prints "Sahmati M1"
  models/
    __init__.py
  rules/
    hma_13b/
    jurisdictions/
  evals/
    cases/
    golden/
  tests/
pyproject.toml
README.md              # one-paragraph stub with the disclaimer
```

`pyproject.toml` must declare:
- package name `sahmati`, version `0.1.0`
- Python `>=3.12`
- Dependencies: `pydantic>=2.0`, `typer>=0.9`, `pyyaml>=6.0`, `jinja2>=3.1`
- Dev dependencies: `pytest>=8.0`, `pytest-cov>=5.0`
- Entry point: `sahmati = "sahmati.__main__:app"`

**Verification:** `python -m sahmati` prints "Sahmati M1" without error. `pip install -e .[dev]` completes without error.

---

## TASK-02 — CaseFile and Document models

**Requires:** TASK-01  
**Satisfies:** REQ-01 (case file ingestion schema), REQ-07 (Document), REQ-08 (settlement dict)

Implement `sahmati/models/case.py` with `PendingCase`, `Document`, and `CaseFile` as specified in design §3.1.

Constraints:
- `case_id` must be a non-empty string.
- `personal_law` is currently a `Literal["HMA"]`.
- `settlement` keys are validated against the fixed required set; unknown keys are allowed (for forward compatibility) but missing required keys raise `ValidationError`.
- All `date` fields reject non-ISO strings at the Pydantic parse level.

**Verification:** `tests/test_models_case.py` — a valid dict round-trips; a dict missing `marriage_date` raises `ValidationError`; a dict with a non-ISO date string raises `ValidationError`; a dict missing a required settlement key raises `ValidationError`.

---

## TASK-03 — Rule, Finding, and report models

**Requires:** TASK-01  
**Satisfies:** REQ-02 (Rule), REQ-10 (ScrutinyReport), REQ-11 (WaiverBrief)

Implement `sahmati/models/rule.py` and `sahmati/models/report.py` as specified in design §3.2–3.6.

Constraints:
- `Finding.statute` must be non-empty when `citation_required` is True; this is enforced at the builder level, not in the model itself.
- `WaiverCondition.status` can only be `MET | PARTIALLY_MET | NOT_MET | UNVERIFIABLE`.

**Verification:** `tests/test_models_rule.py` — each model instantiates correctly from a valid dict; invalid `OnFail` raises `ValidationError`.

---

## TASK-04 — RuleLoader

**Requires:** TASK-03  
**Satisfies:** REQ-02 (all AC-02.x)

Implement `sahmati/loader.py` with class `RuleLoader`:
- `load(rules_dir: Path, jurisdiction: str) -> list[Rule]`
- Loads all YAML files from `rules_dir / "hma_13b/"`.
- If `rules_dir / "jurisdictions" / f"{jurisdiction}.yaml"` exists, applies overrides and additions.
- Raises `ConfigurationError` on duplicate id or missing required field.

**Verification:** `tests/test_loader.py` — loads a known fixture directory; duplicate id raises; missing field raises; override replaces base rule; addition appends; `valid_from` field parses to a `date`.

---

## TASK-05 — YAML rule files for HMA s.13B

**Requires:** TASK-04  
**Satisfies:** REQ-02 (rule format), REQ-03–REQ-09 (each rule has a file)

Write the following YAML files:

- `rules/hma_13b/separation.yaml` — `hma13b.separation_one_year`
- `rules/hma_13b/one_year_bar.yaml` — `hma13b.one_year_bar`
- `rules/hma_13b/jurisdiction.yaml` — `hma13b.jurisdiction`
- `rules/hma_13b/second_motion.yaml` — `hma13b.second_motion_window`
- `rules/hma_13b/documents.yaml` — `hma13b.document_completeness`
- `rules/hma_13b/settlement.yaml` — `hma13b.settlement_completeness`
- `rules/hma_13b/consistency.yaml` — `hma13b.consistency`

Write `rules/jurisdictions/delhi.yaml` with:
- Override for `hma13b.separation_one_year` updating `waiver_route`.
- Addition `delhi.cooling_off_independent_waiver` citing the December 2025 Full Bench.

**Verification:** `sahmati rules list --jurisdiction delhi` lists all 8 rules (7 base + 1 Delhi addition) without error. `RuleLoader` test loads the directory and asserts 8 rules are returned.

---

## TASK-06 — Engine core and dispatch table

**Requires:** TASK-04, TASK-05  
**Satisfies:** REQ-03–REQ-09 (evaluation logic), design §5

Implement `sahmati/engine.py`:
- `Engine.__init__(rules: list[Rule])` — validates that every rule id in the list has a registered evaluator; raises `ConfigurationError` otherwise.
- `Engine.run(case: CaseFile) -> EvaluationResult`
- One evaluator function per rule id as listed in design §5.
- `valid_from` skip logic.
- `citation_required` post-check.

Each evaluator (functions, not methods) must implement the logic specified in REQ-03 through REQ-09 exactly.

Date arithmetic: use `datetime.date` subtraction returning `timedelta`; compare `.days` against integer thresholds (365, 180, 548).

**Verification:** `tests/test_engine.py` — for each evaluator: one minimal PASS fixture, one minimal FAIL fixture, one boundary-exact fixture (e.g. exactly 365 days). Engine raises `ConfigurationError` when initialised with a rule that has no evaluator.

---

## TASK-07 — ScrutinyReportBuilder

**Requires:** TASK-06  
**Satisfies:** REQ-10 (all AC-10.x)

Implement `sahmati/report.py` with `ScrutinyReportBuilder.build(result: EvaluationResult) -> ScrutinyReport`:
- Derives `overall_status`: `PASS` if no findings; `DEFECTS_FOUND` if any finding has severity `defect`; otherwise `PASS` (warnings and info do not change overall status to FAIL — they produce `PASS` with findings listed).
- Counts `rules_evaluated`, `rules_passed`, `rules_skipped`.

**Verification:** `tests/test_report.py` — zero findings → PASS; one warning → PASS with one finding; one defect → DEFECTS_FOUND; mixed → DEFECTS_FOUND.

---

## TASK-08 — WaiverBriefBuilder

**Requires:** TASK-06  
**Satisfies:** REQ-11 (all AC-11.x)

Implement `sahmati/waiver.py` with `WaiverBriefBuilder.build(case: CaseFile, result: EvaluationResult) -> WaiverBrief`:
- Implements the four-condition logic specified in design §6.
- `condition_id: "d"` always returns `status: UNVERIFIABLE`.
- `delhi_hc_position` is a module-level constant string — not derived from case facts.
- The builder never emits a recommendation.

**Verification:** `tests/test_waiver.py` — condition (a): short separation → NOT_MET, long separation → MET; condition (b): `mediation_concluded: false` → NOT_MET; condition (c): settlement defect in result → NOT_MET, no settlement defects → MET; condition (d): always UNVERIFIABLE regardless of inputs.

---

## TASK-09 — Serialiser (JSON and Markdown) with invariant check

**Requires:** TASK-07, TASK-08  
**Satisfies:** REQ-10 (AC-10.5), REQ-11 (AC-11.7), REQ-14 (all AC-14.x)

Implement `sahmati/serialiser.py`:
- `to_json(report: ScrutinyReport | WaiverBrief) -> str` — Pydantic `.model_dump_json()` with `indent=2`.
- `to_markdown(report: ScrutinyReport | WaiverBrief) -> str` — Jinja2 templates in `sahmati/templates/scrutiny_report.md.j2` and `waiver_brief.md.j2`.
- `check_invariant(text: str, scope_fields: list[str]) -> None` — scans `description` and `condition_text` substrings of the serialised text for forbidden tokens; raises `InvariantViolation` if found.
- Statutory text in `statute` fields is not scanned.

Write the two Jinja2 templates.

**Verification:** `tests/test_serialiser.py` — valid report serialises to valid JSON parseable back to `ScrutinyReport`; Markdown output contains the case ID and a findings table; `check_invariant` raises on "We recommend you grant the divorce"; does not raise on "s.23(1)(bb): consent not obtained by force, fraud" (statutory text in statute field, not scanned); does not raise on "The court may grant a decree" in `statute` field.

---

## TASK-10 — CLI wiring

**Requires:** TASK-09  
**Satisfies:** REQ-12 (all AC-12.x)

Implement `sahmati/__main__.py` using Typer:
- `scrutinise` command: load case file → load rules → run engine → build report → (optionally) build waiver brief → serialise → write or print.
- `rules list` command: load rules → print table.
- `eval` command: delegate to `evals/runner.py`.
- All exceptions caught and converted to messages + exit codes as specified in design §12.

**Verification:** manually run:
- `sahmati scrutinise` on a valid PASS case → exit 0, JSON on stdout.
- `sahmati scrutinise` on a case with a defect → exit 1, findings present.
- `sahmati scrutinise` on a missing file → exit 2, clear error.
- `sahmati rules list --jurisdiction delhi` → 8 rules printed.
- `sahmati scrutinise <case> --format md` → Markdown output.

---

## TASK-11 — Synthetic eval cases: clean set (25 cases)

**Requires:** TASK-10  
**Satisfies:** REQ-13 (AC-13.1, AC-13.2 clean half)

Write 25 synthetic case files `evals/cases/SYNTH-001.yaml` through `SYNTH-025.yaml`, all clean (every rule passes). Generate paired golden files `evals/golden/SYNTH-001.json` through `SYNTH-025.json` by running `sahmati scrutinise` on each and verifying the output by hand before committing.

Variation requirements:
- At least 3 cases with children.
- At least 3 cases with pending DV Act cases.
- At least 2 cases with `waiver_requested: true` and all four Amardeep conditions met.
- At least 5 cases with second motion already filed within the window.

**Verification:** `sahmati eval --cases-dir evals/cases --golden-dir evals/golden` passes all 25 (or the full set so far).

---

## TASK-12 — Synthetic eval cases: defect set (25 cases)

**Requires:** TASK-10  
**Satisfies:** REQ-13 (AC-13.1, AC-13.2 defect half), REQ-13 (AC-13.3–AC-13.6)

Write 25 synthetic case files `SYNTH-026.yaml` through `SYNTH-050.yaml`, each with at least one planted defect. Cover the defect matrix from design §11:

- 3 cases: wrong jurisdiction (none of the four s.19 grounds matches the stated court).
- 4 cases: separation period < 365 days.
- 4 cases: missing required document (vary which document).
- 4 cases: settlement head absent (vary which head).
- 3 cases: date anachronism (a document is dated after `first_motion_date`).
- 3 cases: name mismatch (petitioner name differs between petition and a document).
- 4 cases: second motion outside 6–18 month window (mix of too-early and lapsed).

Generate paired golden files and verify by hand.

**Verification:** `sahmati eval` passes all 50 cases. Every golden file is confirmed to contain no forbidden tokens and to have a `statute` field in every finding.

---

## TASK-13 — Eval runner

**Requires:** TASK-12  
**Satisfies:** REQ-13 (AC-13.3–AC-13.8)

Implement `evals/runner.py` and wire `sahmati eval` to call it. The runner must:
- Load each case/golden pair.
- Run the engine on the case.
- Compare actual vs. golden field-by-field (sort findings by `rule_id` before comparing).
- Run hard-fail checks on every output.
- Print a results table and summary.
- Exit 0 if all pass, 1 if any fail.

**Verification:** introduce a deliberate engine misconfiguration on a branch, run `sahmati eval`, confirm it exits 1 and identifies the diverging field. Revert.

---

## TASK-14 — Unit test suite to 90% coverage

**Requires:** TASK-13  
**Satisfies:** design §13 (coverage target)

Fill any gaps in unit tests identified after TASK-13. Add `tests/test_integration.py` with 10 hand-crafted full-pipeline cases.

Run `pytest --cov=sahmati --cov-report=term-missing` and confirm ≥ 90% line coverage.

**Verification:** `pytest` exits 0 with ≥ 90% coverage reported.

---

## TASK-15 — README and disclaimer

**Requires:** TASK-14  
**Satisfies:** design §14 (dependency policy, licence), research brief (ground rules)

Write `README.md` covering:
- One-paragraph plain-language description of what Sahmati M1 does and does not do.
- Explicit disclaimer: "Not legal advice. Not deployed in any court. Built to the Supreme Court AI Committee's Draft Regulations for Use of AI in Courts (2026) permitted uses."
- Installation instructions (`pip install -e .[dev]`).
- Quick-start: `sahmati scrutinise <case-file>` with a one-line example.
- Link to `rules/hma_13b/` for the rule definitions.
- Licence statement: Apache-2.0 (code).

**Verification:** README renders without broken syntax on GitHub Markdown preview (visual check). Disclaimer paragraph is present verbatim.

---

## Task dependency summary

```
TASK-01
├── TASK-02
│   └── TASK-06
├── TASK-03
│   ├── TASK-04
│   │   ├── TASK-05
│   │   │   └── TASK-06
│   │   └── TASK-06
│   │       ├── TASK-07
│   │       │   └── TASK-09
│   │       └── TASK-08
│   │           └── TASK-09
│   │               └── TASK-10
│   │                   ├── TASK-11
│   │                   │   └── TASK-12
│   │                   │       └── TASK-13
│   │                   │           └── TASK-14
│   │                   │               └── TASK-15
│   │                   └── TASK-13
```

Minimum viable smoke test after TASK-10: run `sahmati scrutinise` on one hand-written clean case and one defect case. If both behave correctly, proceed to the eval cases.
