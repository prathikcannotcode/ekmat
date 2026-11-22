# Sahmati M1 — Requirements

**Scope:** Deterministic YAML rules engine for HMA s.13B (Delhi jurisdiction), scrutiny report, Amardeep Singh waiver brief, CLI, and synthetic eval suite. No LLM anywhere in this milestone.

---

## Actors

| ID | Actor | Description |
|----|-------|-------------|
| A1 | Petitioner (couple or lawyer) | Submits a case JSON/YAML file for evaluation |
| A2 | Registry operator | Runs the CLI to produce reports for a filed petition |
| A3 | Developer / evaluator | Runs the eval suite to verify engine correctness |

---

## User Stories and Acceptance Criteria

Criteria use EARS notation: **WHEN** [event] **THE SYSTEM SHALL** [behaviour]; **IF** [precondition] **THE SYSTEM SHALL** [behaviour]; **WHERE** [feature exists] **THE SYSTEM SHALL** [behaviour].

---

### REQ-01 — Case file ingestion

**Story:** As a registry operator, I want to submit a structured case file so that the engine has all the facts it needs to run every rule.

**Acceptance criteria:**

- AC-01.1: WHEN a valid case file (JSON or YAML) conforming to the CaseFile schema is passed to the CLI, THE SYSTEM SHALL accept it and proceed to evaluation without error.
- AC-01.2: WHEN a case file is missing a required field, THE SYSTEM SHALL emit a schema validation error naming the missing field and exit with code 2.
- AC-01.3: WHEN a case file contains a date string that is not ISO 8601, THE SYSTEM SHALL emit a parse error naming the offending field and exit with code 2.
- AC-01.4: WHEN a case file passes schema validation, THE SYSTEM SHALL log the case ID and the jurisdiction it resolved to.
- AC-01.5: WHERE the jurisdiction field is absent, THE SYSTEM SHALL default to `delhi` and log a warning.

---

### REQ-02 — Rule loading and versioning

**Story:** As a developer, I want rules to live in YAML files with explicit statute citations so that any rule change is auditable and traceable to the law.

**Acceptance criteria:**

- AC-02.1: WHEN the engine starts, THE SYSTEM SHALL load all YAML rule files from `rules/hma_13b/` and `rules/jurisdictions/delhi.yaml`.
- AC-02.2: WHEN two rules share the same `id`, THE SYSTEM SHALL raise a configuration error and refuse to start.
- AC-02.3: WHEN a rule file is missing any of the required fields (`id`, `statute`, `condition`, `on_fail`, `citation_required`), THE SYSTEM SHALL raise a configuration error naming the file and the missing field.
- AC-02.4: WHEN a rule has `citation_required: true`, THE SYSTEM SHALL enforce that any finding produced by that rule includes a `statute` and `source_page` field.
- AC-02.5: WHEN a rule has a `valid_from` date and the case's `first_motion_date` precedes that date, THE SYSTEM SHALL skip that rule and log which rule was skipped.
- AC-02.6: WHERE a jurisdiction override exists in `rules/jurisdictions/delhi.yaml` for a given rule id, THE SYSTEM SHALL apply the override in place of the base rule.

---

### REQ-03 — Separation period check

**Story:** As a registry operator, I want the engine to verify the one-year separation period under s.13B(1) so that defective petitions are caught at filing.

**Acceptance criteria:**

- AC-03.1: WHEN `first_motion_date - separation_start_date >= 365 days`, THE SYSTEM SHALL mark rule `hma13b.separation_one_year` as PASS.
- AC-03.2: WHEN `first_motion_date - separation_start_date < 365 days`, THE SYSTEM SHALL mark the rule as FAIL and emit a finding with `on_fail = flag_waivable`, citing HMA s.13B(1).
- AC-03.3: WHEN the separation rule fails and a waiver application is present in the case file, THE SYSTEM SHALL record `waiver_route: "s.14 proviso (Delhi HC FB, Dec 2025)"` in the finding.
- AC-03.4: WHEN the separation rule fails and no waiver application is present, THE SYSTEM SHALL list it as a defect requiring attention before filing.

---

### REQ-04 — One-year bar from marriage check

**Story:** As a registry operator, I want the engine to check the s.14 bar on filing within one year of marriage so that petitions that need leave are flagged.

**Acceptance criteria:**

- AC-04.1: WHEN `first_motion_date - marriage_date >= 365 days`, THE SYSTEM SHALL mark rule `hma13b.one_year_bar` as PASS.
- AC-04.2: WHEN `first_motion_date - marriage_date < 365 days`, THE SYSTEM SHALL mark the rule as FAIL, label it `flag_requires_leave`, and cite HMA s.14.
- AC-04.3: IF rule `hma13b.one_year_bar` fails and the case file contains `s14_leave_granted: true`, THE SYSTEM SHALL mark the finding as conditionally resolved and record the leave date.

---

### REQ-05 — Jurisdiction check

**Story:** As a registry operator, I want the engine to verify that at least one of the four HMA s.19 grounds is established so that the petition is filed in a competent court.

**Acceptance criteria:**

- AC-05.1: WHEN at least one of `marriage_place`, `respondent_residence`, `last_cohabitation_place`, or `wife_residence` matches the stated court's district, THE SYSTEM SHALL mark rule `hma13b.jurisdiction` as PASS.
- AC-05.2: WHEN none of the four grounds matches the stated court's district, THE SYSTEM SHALL emit a finding citing HMA s.19 and list which grounds were checked and failed.
- AC-05.3: WHERE the jurisdiction check passes on more than one ground, THE SYSTEM SHALL record all passing grounds.

---

### REQ-06 — Second-motion timing check

**Story:** As a registry operator, I want the engine to verify that the second motion (if already filed) falls within the 6–18 month window so that out-of-window motions are caught.

**Acceptance criteria:**

- AC-06.1: IF `second_motion_date` is present in the case file AND `second_motion_date - first_motion_date >= 180 days` AND `second_motion_date - first_motion_date <= 548 days (18 months)`, THE SYSTEM SHALL mark rule `hma13b.second_motion_window` as PASS.
- AC-06.2: IF `second_motion_date` is present AND the interval is less than 180 days, THE SYSTEM SHALL emit a finding citing HMA s.13B(2) and tag it `flag_waivable` with waiver route `Amardeep Singh (2017) 8 SCC 746`.
- AC-06.3: IF `second_motion_date` is present AND the interval exceeds 548 days, THE SYSTEM SHALL emit a finding citing HMA s.13B(2) and tag it `flag_lapsed`.
- AC-06.4: IF `second_motion_date` is absent, THE SYSTEM SHALL skip this rule and note that the second motion has not yet been filed.

---

### REQ-07 — Document completeness check

**Story:** As a registry operator, I want the engine to list every required document that is absent from the case file so that the petition is complete at filing.

**Acceptance criteria:**

- AC-07.1: WHEN any required document (marriage certificate, proof of address for jurisdiction, separation affidavits from both spouses, identity proofs, settlement deed) is not listed in `documents_present`, THE SYSTEM SHALL emit one finding per missing document, each citing the applicable rule or practice direction.
- AC-07.2: WHEN all required documents are present, THE SYSTEM SHALL mark rule `hma13b.document_completeness` as PASS.
- AC-07.3: WHEN a document is present but its `notarised` field is false and notarisation is required, THE SYSTEM SHALL emit a finding with severity `defect`.
- AC-07.4: WHEN a document's stated date is after `first_motion_date`, THE SYSTEM SHALL emit a finding flagging the anachronism.

---

### REQ-08 — Settlement completeness check

**Story:** As a registry operator, I want the engine to verify that the settlement deed addresses every required head so that the petition is not returned for a missing term.

**Acceptance criteria:**

- AC-08.1: WHEN the settlement deed is missing any of the following heads — alimony/maintenance, stridhan, child custody, child support, visitation schedule, immovable property, or pending case disposition — THE SYSTEM SHALL emit one finding per missing head.
- AC-08.2: WHEN all required settlement heads are addressed, THE SYSTEM SHALL mark rule `hma13b.settlement_completeness` as PASS.
- AC-08.3: WHEN `children_exist: false`, THE SYSTEM SHALL skip the child-related heads and note that they were not evaluated.
- AC-08.4: WHEN `pending_cases` lists any case under s.498A IPC / BNS s.85, THE SYSTEM SHALL emit a finding noting that this offence is non-compoundable and an HC quashing order will be required.
- AC-08.5: WHEN `pending_cases` lists any case under DV Act or s.125 CrPC / s.144 BNSS, THE SYSTEM SHALL note that withdrawal is possible and emit a checklist item for the disposal plan.

---

### REQ-09 — Name and date consistency check

**Story:** As a registry operator, I want the engine to cross-check names and dates across all documents so that internal inconsistencies are caught before filing.

**Acceptance criteria:**

- AC-09.1: WHEN the petitioner name in the petition differs (case-insensitively, ignoring whitespace) from the name in any submitted document, THE SYSTEM SHALL emit a finding citing the conflicting document.
- AC-09.2: WHEN marriage dates are stated in more than one document and they do not match, THE SYSTEM SHALL emit a finding listing each conflicting source.
- AC-09.3: WHEN separation dates are stated in more than one document and they do not match, THE SYSTEM SHALL emit a finding listing each conflicting source.

---

### REQ-10 — Scrutiny report generation

**Story:** As a registry operator, I want a structured scrutiny report so that every defect is documented with its legal basis before the petition is accepted.

**Acceptance criteria:**

- AC-10.1: WHEN evaluation is complete, THE SYSTEM SHALL produce a scrutiny report containing: case ID, evaluation timestamp, jurisdiction, overall status (`PASS` / `DEFECTS_FOUND` / `FAIL`), and an ordered list of findings.
- AC-10.2: WHEN any finding is emitted, it SHALL contain: `rule_id`, `severity` (`defect` / `warning` / `info`), `statute` citation, `source_page` (document name and page number if applicable), `description`, and `waiver_route` if applicable.
- AC-10.3: WHEN no findings are emitted, THE SYSTEM SHALL set overall status to `PASS`.
- AC-10.4: WHEN at least one finding has severity `defect`, THE SYSTEM SHALL set overall status to `DEFECTS_FOUND`.
- AC-10.5: THE SYSTEM SHALL emit the report as valid JSON (default) and optionally as plain-text Markdown when `--format md` is passed to the CLI.
- AC-10.6: THE SYSTEM SHALL NOT include any phrase recommending grant or refusal of the divorce.

---

### REQ-11 — Amardeep Singh waiver brief

**Story:** As a registry operator, I want a structured waiver brief that documents the four Amardeep Singh conditions with the evidence for each so that the judge can assess waiver eligibility without having to locate the case facts.

**Acceptance criteria:**

- AC-11.1: WHEN `waiver_requested: true` is set in the case file, THE SYSTEM SHALL produce a waiver brief alongside the scrutiny report.
- AC-11.2: THE SYSTEM SHALL evaluate each of the four Amardeep Singh conditions: (a) the statutory one-year separation has elapsed since marriage, (b) all efforts at mediation or reconciliation have concluded, (c) all ancillary matters (alimony, custody, stridhan, property, pending cases) are settled, (d) waiting out the remaining cooling-off period would only prolong misery.
- AC-11.3: FOR EACH condition, THE SYSTEM SHALL state: the condition text, the evidence present in the case file, the evidence absent or unverifiable from the case file, and a neutral status (`MET` / `PARTIALLY_MET` / `NOT_MET` / `UNVERIFIABLE`).
- AC-11.4: THE SYSTEM SHALL include a section summarising the Delhi HC's current position on the cooling-off waiver, citing the December 2025 Full Bench ruling.
- AC-11.5: THE SYSTEM SHALL NOT include any phrase recommending that the waiver be granted or refused.
- AC-11.6: THE SYSTEM SHALL NOT make any finding on condition (d) beyond listing the stated facts; it SHALL NOT infer or score subjective suffering.
- AC-11.7: THE SYSTEM SHALL emit the brief as valid JSON (default) and optionally as Markdown when `--format md` is passed.

---

### REQ-12 — CLI

**Story:** As a registry operator or developer, I want a single CLI entry point so that I can run the engine without writing Python.

**Acceptance criteria:**

- AC-12.1: WHEN `sahmati scrutinise <case-file>` is run, THE SYSTEM SHALL produce a scrutiny report on stdout and exit with code 0 if the case passes, code 1 if defects are found.
- AC-12.2: WHEN `sahmati scrutinise <case-file> --waiver` is run, THE SYSTEM SHALL produce both the scrutiny report and the waiver brief.
- AC-12.3: WHEN `sahmati scrutinise <case-file> --format md` is run, THE SYSTEM SHALL output Markdown instead of JSON.
- AC-12.4: WHEN `sahmati scrutinise <case-file> --out <path>` is run, THE SYSTEM SHALL write the output to that path instead of stdout.
- AC-12.5: WHEN `sahmati rules list` is run, THE SYSTEM SHALL print each loaded rule's id, statute, and jurisdiction to stdout.
- AC-12.6: WHEN `sahmati rules list --jurisdiction delhi` is run, THE SYSTEM SHALL filter to Delhi-applicable rules only.
- AC-12.7: WHEN `sahmati eval` is run, THE SYSTEM SHALL run all cases in `evals/cases/` against their golden outputs and print a pass/fail summary.
- AC-12.8: WHEN any CLI command is given an unreadable or non-existent file path, THE SYSTEM SHALL emit a clear error and exit with code 2.

---

### REQ-13 — Eval suite

**Story:** As a developer, I want a synthetic eval suite so that I can verify the engine produces exactly the expected output for known inputs.

**Acceptance criteria:**

- AC-13.1: THE SYSTEM SHALL include at least 50 synthetic case files in `evals/cases/`, each with a paired golden scrutiny report in `evals/golden/`.
- AC-13.2: AT LEAST half the synthetic cases SHALL contain planted defects covering: wrong jurisdiction, separation period too short, missing documents, settlement head absent, date anachronism, name mismatch, second motion out of window.
- AC-13.3: WHEN `sahmati eval` is run, THE SYSTEM SHALL compare actual engine output against the golden file field-by-field and report any divergence with the case name, the field path, the expected value, and the actual value.
- AC-13.4: WHEN the engine output exactly matches the golden file for a case, THE SYSTEM SHALL report that case as PASS.
- AC-13.5: WHEN any finding in the actual output contains the words "grant" or "refuse" or "granted" or "refused" in a recommendation context, THE SYSTEM SHALL mark the eval as FAIL with a hard-coded no-recommendation violation.
- AC-13.6: WHEN any finding in the actual output lacks both a `statute` citation and a `source_page`, THE SYSTEM SHALL mark the eval as FAIL with a citation-required violation.
- AC-13.7: THE SYSTEM SHALL report eval results as a table: case ID, PASS/FAIL, number of divergences.
- AC-13.8: WHEN all cases pass, `sahmati eval` SHALL exit with code 0; when any case fails, it SHALL exit with code 1.

---

### REQ-14 — No-recommendation invariant

**Story:** As the project, I want a hard runtime invariant that the engine never outputs a recommendation to grant or refuse, so that the tool stays within its permitted use even if a future rule is misconfigured.

**Acceptance criteria:**

- AC-14.1: WHEN the scrutiny report or waiver brief is serialised, THE SYSTEM SHALL scan the serialised text for the tokens `["grant", "refuse", "granted", "refused", "recommend"]` in a recommendation context and raise an internal `InvariantViolation` error rather than return the output.
- AC-14.2: WHEN an `InvariantViolation` is raised, THE SYSTEM SHALL log the offending token and the rule that produced it, and exit with code 3.
