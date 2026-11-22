# Sahmati M1 — Design

---

## 1. Architecture overview

Milestone 1 is a pure-Python, deterministic, stateless pipeline. No network calls. No LLM. No persistent database.

```
                   ┌────────────────────────────────────────────────────┐
                   │  CLI  (sahmati/__main__.py)                        │
                   │  Typer-based; commands: scrutinise, rules, eval    │
                   └──────────────────────┬─────────────────────────────┘
                                          │ CaseFile (Pydantic)
                   ┌──────────────────────▼─────────────────────────────┐
                   │  RuleLoader                                         │
                   │  Reads rules/hma_13b/*.yaml + rules/jurisdictions/  │
                   │  Applies jurisdiction overrides                     │
                   │  Returns: List[Rule]                                │
                   └──────────────────────┬─────────────────────────────┘
                                          │ List[Rule]
                   ┌──────────────────────▼─────────────────────────────┐
                   │  Engine                                             │
                   │  For each Rule: calls evaluate(rule, case)         │
                   │  Collects List[Finding]                             │
                   │  Returns: EvaluationResult                          │
                   └──────────────┬───────────────────┬─────────────────┘
                                  │                   │
         ┌────────────────────────▼──┐    ┌───────────▼──────────────────┐
         │  ScrutinyReportBuilder    │    │  WaiverBriefBuilder           │
         │  Assembles ScrutinyReport │    │  Evaluates 4 Amardeep         │
         │  Applies no-rec invariant │    │  conditions; applies          │
         └────────────────────────┬──┘    │  no-rec invariant             │
                                  │       └───────────┬──────────────────┘
                                  │                   │
                   ┌──────────────▼───────────────────▼─────────────────┐
                   │  Serialiser                                         │
                   │  JSON (default) or Markdown; invariant scan        │
                   └────────────────────────────────────────────────────┘
```

Every component is a plain Python class. No global state. The engine receives a `CaseFile` and a `List[Rule]`; the builders receive an `EvaluationResult`. Each can be tested in isolation.

---

## 2. Repository layout (M1)

```
sahmati/
  __main__.py                # CLI entry point
  loader.py                  # RuleLoader
  engine.py                  # Engine, evaluate()
  report.py                  # ScrutinyReportBuilder
  waiver.py                  # WaiverBriefBuilder
  serialiser.py              # JSON / Markdown; invariant scan
  models/
    case.py                  # CaseFile, Document, PendingCase (Pydantic)
    rule.py                  # Rule, Finding, EvaluationResult (Pydantic)
    report.py                # ScrutinyReport, WaiverBrief (Pydantic)
  rules/
    hma_13b/
      separation.yaml
      one_year_bar.yaml
      jurisdiction.yaml
      second_motion.yaml
      documents.yaml
      settlement.yaml
      consistency.yaml
    jurisdictions/
      delhi.yaml
  evals/
    cases/                   # 50 synthetic CaseFile YAML files
    golden/                  # 50 paired ScrutinyReport JSON files
    runner.py                # eval harness
  pyproject.toml
  README.md
```

---

## 3. Data models

All models use Pydantic v2. Dates are `datetime.date`. Enums are `str` literals where possible to keep YAML readable.

### 3.1 CaseFile

```python
class PendingCase(BaseModel):
    case_number: str
    court: str
    act: str          # e.g. "IPC s.498A", "DV Act", "CrPC s.125"
    status: str       # e.g. "pending", "stayed"

class Document(BaseModel):
    name: str                       # e.g. "marriage_certificate"
    document_type: str
    dated: date | None = None
    notarised: bool = False
    source_page: int | None = None  # page in the petition bundle

class CaseFile(BaseModel):
    case_id: str
    jurisdiction: str = "delhi"
    personal_law: Literal["HMA"] = "HMA"

    # Parties
    petitioner_1_name: str
    petitioner_2_name: str

    # Key dates
    marriage_date: date
    separation_start_date: date
    first_motion_date: date
    second_motion_date: date | None = None

    # Court
    court_district: str
    marriage_place: str | None = None
    respondent_residence: str | None = None
    last_cohabitation_place: str | None = None
    wife_residence: str | None = None

    # Children
    children_exist: bool = False

    # Settlement completeness flags
    settlement: dict[str, bool]
    # Required keys: alimony, stridhan, child_custody, child_support,
    #                visitation, immovable_property, pending_case_plan

    # Documents
    documents_present: list[Document] = []

    # Pending cases
    pending_cases: list[PendingCase] = []

    # Waiver
    waiver_requested: bool = False
    s14_leave_granted: bool = False
    mediation_concluded: bool = False

    # Names as they appear in documents (for consistency check)
    names_in_documents: dict[str, str] = {}
    # e.g. {"marriage_certificate": "Ravi Kumar", "petition": "Ravi K."}

    marriage_dates_in_documents: dict[str, date] = {}
    separation_dates_in_documents: dict[str, date] = {}
```

### 3.2 Rule

```python
class OnFail(str, Enum):
    DEFECT = "defect"
    FLAG_WAIVABLE = "flag_waivable"
    FLAG_REQUIRES_LEAVE = "flag_requires_leave"
    FLAG_LAPSED = "flag_lapsed"
    WARNING = "warning"
    INFO = "info"

class Rule(BaseModel):
    id: str
    statute: str
    condition: str            # human-readable; not eval'd
    on_fail: OnFail
    citation_required: bool = True
    waiver_route: str | None = None
    jurisdiction: str = "all"
    valid_from: date | None = None
    description: str = ""
```

### 3.3 Finding

```python
class Severity(str, Enum):
    DEFECT = "defect"
    WARNING = "warning"
    INFO = "info"

class Finding(BaseModel):
    rule_id: str
    severity: Severity
    statute: str
    source_page: str | None = None   # "marriage_certificate p.1"
    description: str
    waiver_route: str | None = None
    skipped: bool = False
    skip_reason: str | None = None
```

### 3.4 EvaluationResult

```python
class RuleOutcome(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    SKIPPED = "SKIPPED"
    CONDITIONAL_PASS = "CONDITIONAL_PASS"

class RuleResult(BaseModel):
    rule_id: str
    outcome: RuleOutcome
    finding: Finding | None = None

class EvaluationResult(BaseModel):
    case_id: str
    jurisdiction: str
    evaluated_at: datetime
    rule_results: list[RuleResult]
    findings: list[Finding]          # only FAIL findings
```

### 3.5 ScrutinyReport

```python
class OverallStatus(str, Enum):
    PASS = "PASS"
    DEFECTS_FOUND = "DEFECTS_FOUND"
    FAIL = "FAIL"

class ScrutinyReport(BaseModel):
    case_id: str
    jurisdiction: str
    evaluated_at: datetime
    overall_status: OverallStatus
    findings: list[Finding]
    rules_evaluated: int
    rules_passed: int
    rules_skipped: int
```

### 3.6 WaiverConditionStatus

```python
class ConditionStatus(str, Enum):
    MET = "MET"
    PARTIALLY_MET = "PARTIALLY_MET"
    NOT_MET = "NOT_MET"
    UNVERIFIABLE = "UNVERIFIABLE"

class WaiverCondition(BaseModel):
    condition_id: str             # "a", "b", "c", "d"
    condition_text: str
    evidence_present: list[str]
    evidence_absent: list[str]
    status: ConditionStatus

class WaiverBrief(BaseModel):
    case_id: str
    evaluated_at: datetime
    conditions: list[WaiverCondition]
    delhi_hc_position: str        # static text, Dec 2025 FB ruling
    authority: str = "Amardeep Singh v. Harveen Kaur, (2017) 8 SCC 746"
```

---

## 4. Rule file format

Each YAML file in `rules/hma_13b/` contains one rule. The rule `condition` field is prose for human readers; evaluation logic lives in the Python evaluator for that rule, keyed by `id`.

```yaml
# rules/hma_13b/separation.yaml
id: hma13b.separation_one_year
statute: "Hindu Marriage Act 1955, s.13B(1)"
condition: "separation_start_date <= first_motion_date - 365 days"
on_fail: flag_waivable
waiver_route: "s.14 proviso (Delhi HC Full Bench, December 2025)"
citation_required: true
valid_from: "1976-05-27"   # HMA amendment adding s.13B
description: "Both parties must have lived apart for at least one year before the first motion."
```

Jurisdiction override files add or replace rules for a specific HC:

```yaml
# rules/jurisdictions/delhi.yaml
jurisdiction: delhi
overrides:
  - id: hma13b.separation_one_year
    waiver_route: "s.14 proviso (Delhi HC Full Bench, December 2025; also independently waivable)"
    notes: "Delhi HC FB Dec 2025: s.13B(1) separation and s.13B(2) cooling-off waivers are independent."
additions:
  - id: delhi.cooling_off_independent_waiver
    statute: "Delhi HC Full Bench, December 2025"
    condition: "s.13B(1) and s.13B(2) waivers are assessed independently"
    on_fail: info
    citation_required: true
    description: "Delhi HC held the two waivers are decided independently."
```

---

## 5. Engine semantics

The engine is a simple dispatch table: a dictionary mapping `rule.id` to a Python evaluator function. Each evaluator takes `(rule: Rule, case: CaseFile) -> RuleResult`.

```python
EVALUATORS: dict[str, Callable[[Rule, CaseFile], RuleResult]] = {
    "hma13b.separation_one_year": evaluate_separation,
    "hma13b.one_year_bar": evaluate_one_year_bar,
    "hma13b.jurisdiction": evaluate_jurisdiction,
    "hma13b.second_motion_window": evaluate_second_motion,
    "hma13b.document_completeness": evaluate_documents,
    "hma13b.settlement_completeness": evaluate_settlement,
    "hma13b.consistency": evaluate_consistency,
    "delhi.cooling_off_independent_waiver": evaluate_delhi_note,
}
```

Execution order: rules are evaluated in the order they are listed in the evaluator table. Rule evaluation is not short-circuited; every applicable rule runs regardless of earlier failures.

**valid_from handling:** if `rule.valid_from` is set and `case.first_motion_date < rule.valid_from`, the engine creates a `RuleResult(outcome=SKIPPED)` and moves on.

**citation_required enforcement:** after each evaluator returns, the engine checks: if `rule.citation_required` and `result.finding` is not None, the finding must have a non-empty `statute`. If not, the engine raises `ConfigurationError`.

**Unknown rule IDs:** if a loaded rule has no matching evaluator, the engine raises `ConfigurationError` at startup, not at runtime.

---

## 6. Waiver brief semantics

The `WaiverBriefBuilder` is called after `Engine.run()`. It reads the `EvaluationResult` and the original `CaseFile`.

**Condition (a) — statutory separation:**
- Evidence present: separation_start_date, first_motion_date, computed interval.
- Status: MET if interval >= 365 days; NOT_MET otherwise.

**Condition (b) — mediation concluded:**
- Evidence present: `case.mediation_concluded`.
- Status: MET if `True`; NOT_MET if `False`; UNVERIFIABLE if the field is absent (future-proofing for cases filed before the mediation step).

**Condition (c) — all ancillary matters settled:**
- Reads `EvaluationResult.findings` for rule `hma13b.settlement_completeness`.
- Status: MET if no settlement findings; PARTIALLY_MET if warnings only; NOT_MET if any defect finding.

**Condition (d) — waiting prolongs misery:**
- Evidence present: list of facts from the case file that bear on this (pending cases, employment status if present, duration already elapsed).
- Status: always UNVERIFIABLE. The brief states the facts; it does not assess subjective suffering.
- The `delhi_hc_position` field is a static string populated from a constant, not derived from case facts.

---

## 7. No-recommendation invariant

The invariant is enforced in two places.

**At serialisation time (Serialiser):** after converting the report or brief to its string form, the serialiser runs:

```python
FORBIDDEN_TOKENS = re.compile(
    r'\b(grant|granted|refuse|refused|recommend|recommendation)\b',
    re.IGNORECASE
)
```

If a match is found, it raises `InvariantViolation(token=..., context=...)` before returning any output. The engine exits with code 3.

**In the eval harness:** `sahmati eval` checks every golden file and every actual output for forbidden tokens and fails fast if any appear.

The invariant does not apply to fields that contain statutory text quoting the word (e.g. a `statute` field that reads "s.23(1)(bb) HMA: consent not obtained by force, fraud or undue influence"). The check is scoped to `description` and `condition_text` fields only.

---

## 8. Scrutiny report format (JSON)

```json
{
  "case_id": "SYNTH-001",
  "jurisdiction": "delhi",
  "evaluated_at": "2026-11-22T10:00:00Z",
  "overall_status": "DEFECTS_FOUND",
  "rules_evaluated": 7,
  "rules_passed": 5,
  "rules_skipped": 0,
  "findings": [
    {
      "rule_id": "hma13b.separation_one_year",
      "severity": "defect",
      "statute": "Hindu Marriage Act 1955, s.13B(1)",
      "source_page": "petition p.3",
      "description": "Separation period is 11 months 12 days. Minimum is 365 days.",
      "waiver_route": "s.14 proviso (Delhi HC Full Bench, December 2025)"
    }
  ]
}
```

Markdown format (--format md) renders as a headed report with a findings table. The table columns are: Rule, Severity, Statute, Source, Description, Waiver Route.

---

## 9. Waiver brief format (JSON)

```json
{
  "case_id": "SYNTH-001",
  "evaluated_at": "2026-11-22T10:00:00Z",
  "authority": "Amardeep Singh v. Harveen Kaur, (2017) 8 SCC 746",
  "delhi_hc_position": "The Delhi High Court Full Bench (December 2025) held that the one-year separation waiver under s.13B(1) and the six-month cooling-off waiver under s.13B(2) are assessed independently under the s.14 proviso. Both waivers remain at the court's discretion.",
  "conditions": [
    {
      "condition_id": "a",
      "condition_text": "The statutory one-year separation period since marriage has elapsed.",
      "evidence_present": [
        "Marriage date: 2024-01-15",
        "Separation start: 2024-03-01",
        "First motion date: 2026-10-01",
        "Interval since separation: 944 days (≥ 365 days)"
      ],
      "evidence_absent": [],
      "status": "MET"
    },
    {
      "condition_id": "b",
      "condition_text": "All efforts at mediation or reconciliation have concluded.",
      "evidence_present": ["mediation_concluded: true"],
      "evidence_absent": [],
      "status": "MET"
    },
    {
      "condition_id": "c",
      "condition_text": "All ancillary matters (alimony, custody, stridhan, property, pending cases) are settled.",
      "evidence_present": ["alimony: settled", "stridhan: settled", "immovable_property: settled"],
      "evidence_absent": ["child_custody: not addressed (children_exist: true)"],
      "status": "NOT_MET"
    },
    {
      "condition_id": "d",
      "condition_text": "Waiting out the remaining cooling-off period would only prolong misery.",
      "evidence_present": ["First motion filed: 2026-10-01", "Pending cases: none"],
      "evidence_absent": ["Subjective evidence of hardship not assessable from case file"],
      "status": "UNVERIFIABLE"
    }
  ]
}
```

---

## 10. CLI design

The CLI uses [Typer](https://typer.tiangolo.com/). Entry point is `sahmati` (registered in `pyproject.toml` via `[project.scripts]`).

```
sahmati scrutinise <case-file> [--waiver] [--format json|md] [--out <path>]
sahmati rules list [--jurisdiction <name>]
sahmati eval [--cases-dir <path>] [--golden-dir <path>]
```

Exit codes:
- 0: success (all rules pass, or eval all pass)
- 1: defects found (scrutinise) or eval failures (eval)
- 2: input error (bad file, schema error)
- 3: invariant violation

---

## 11. Eval harness design

`evals/runner.py` is a standalone module callable via `sahmati eval`.

**Case file naming:** `evals/cases/SYNTH-NNN.yaml` paired with `evals/golden/SYNTH-NNN.json`.

**Comparison logic:** both actual and golden are deserialised to `ScrutinyReport` Pydantic objects and compared field-by-field. Order of findings is sorted by `rule_id` before comparison so that evaluation-order changes do not break evals.

**Planted defect matrix (minimum 25 cases with defects):**

| Defect type | Minimum count |
|---|---|
| Wrong jurisdiction | 3 |
| Separation period too short | 4 |
| Missing required document | 4 |
| Settlement head absent | 4 |
| Date anachronism (doc dated after motion) | 3 |
| Name mismatch across documents | 3 |
| Second motion out of 6–18 month window | 4 |

**Clean cases (minimum 25):** all rules pass; golden status is `PASS`.

**Waiver cases:** at least 5 cases with `waiver_requested: true`, testing each of the four conditions in various states.

**Hard-fail checks (run on every case regardless of PASS/FAIL):**
1. No forbidden tokens in `description` or `condition_text` fields.
2. Every finding with `citation_required: true` on its rule has non-empty `statute`.
3. `overall_status` is consistent with the presence of `defect`-severity findings.

---

## 12. Error handling

| Situation | Behaviour |
|---|---|
| Schema validation failure on case file | Print field name and error; exit 2 |
| Rule file missing required field | Print file name and field; exit 2 (startup) |
| Duplicate rule id | Print both file names and id; exit 2 (startup) |
| Unknown rule id (no evaluator) | Print id; exit 2 (startup) |
| InvariantViolation | Print offending token and rule_id; exit 3 |
| Output path not writable | Print path and OS error; exit 2 |
| Eval golden file not found | Print case id; mark as FAIL; continue |

No exceptions bubble to the top level. All are caught in `__main__.py` and converted to messages + exit codes.

---

## 13. Testing strategy

All tests live in `tests/`. The project uses `pytest`. No external services. No LLM.

**Unit tests (per module):**
- `tests/test_loader.py`: valid YAML loads correctly; duplicate id raises; missing field raises; jurisdiction override is applied.
- `tests/test_engine.py`: each evaluator tested with a minimal `CaseFile` fixture — one PASS case, one FAIL case, edge cases (exact boundary dates, missing optional fields).
- `tests/test_report.py`: `ScrutinyReport` overall_status computed correctly for 0 defects, 1 warning, 1 defect.
- `tests/test_waiver.py`: each of the four conditions in MET / NOT_MET / UNVERIFIABLE state.
- `tests/test_serialiser.py`: JSON and Markdown outputs are well-formed; invariant check fires on a seeded forbidden token; statutory text quoting a forbidden word is not falsely blocked.

**Integration tests:**
- `tests/test_integration.py`: run the full pipeline on 10 hand-crafted case files and assert the full output matches expected JSON.

**Eval suite (not pytest):**
- `sahmati eval` is the acceptance gate. All 50 synthetic cases must pass before M1 is considered complete.

**Coverage target:** 90% line coverage across `sahmati/` (excluding `__main__.py` boilerplate).

---

## 14. Dependency policy

M1 dependencies are intentionally minimal:
- `pydantic >= 2.0` — data models and validation
- `typer >= 0.9` — CLI
- `pyyaml >= 6.0` — rule file loading
- `jinja2 >= 3.1` — Markdown template rendering (report)
- `pytest`, `pytest-cov` — test tooling (dev only)

No network dependencies. No model runtime. The `pyproject.toml` will specify a `[project.optional-dependencies]` group `dev` for test tools.

Python version: 3.12 minimum.
