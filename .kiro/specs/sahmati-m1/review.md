# Sahmati M1 — Critical Review

This document records where the brief is wrong, ambiguous, or underspecified, and the decisions a person must make before building. It does not soften disagreements.

---

## 1. Legal errors and inaccuracies

### 1.1 The 18-month window is not 548 days

The brief says the second motion window is "6 to 18 months after the first". 18 calendar months is not 548 days. It is between 547 days (18 × 30.4) and 549 days depending on which months are involved. The HMA does not say "548 days"; it says "18 months". Date arithmetic using a fixed integer will produce wrong answers for certain calendar combinations. The engine must compute "first motion date + 18 months" using calendar-month arithmetic (Python's `dateutil.relativedelta` or equivalent), not a fixed day count. This is a correctness bug, not a style issue.

The same applies to "1 year" — the HMA says "one year", not "365 days". A marriage that started on 1 March 2023 and separated on 1 March 2024 is exactly one year regardless of leap years. Using 365 days gives a wrong answer in leap years. The spec must specify whether the engine uses calendar-based arithmetic or day-count arithmetic and must document the choice.

### 1.2 The Amardeep Singh conditions are not settled law

The brief states the four Amardeep Singh conditions as if they are fixed and enumerable. They are not. *Amardeep Singh v. Harveen Kaur* (2017) 8 SCC 746 is a two-judge bench decision. Its conditions have been read differently by different High Courts. *Shilpa Sailesh v. Varun Sreenivasan* (Constitution Bench, 2023) confirms the Supreme Court can exercise Article 142 power but does not codify the family court waiver conditions into five or four or any fixed number. The brief treats the four conditions as a closed checklist; they are a discretionary framework. The waiver brief must make this explicit. Building a status display that says "CONDITION A: MET" may give petitioners false confidence that a family court will waive.

### 1.3 The Delhi HC December 2025 Full Bench ruling

The brief cites "Delhi HC Full Bench, December 2025" as authority for the independent waiver of s.13B(1) and s.13B(2). This is used as a foundation rule in the spec. This ruling needs a citation: case name, court, date, and citation number. Without it, the engine cannot correctly populate the `statute` and `source_page` fields it requires, and the rules will fail their own `citation_required: true` invariant. Before writing any rule that relies on this ruling, verify its existence and obtain the citation. If it cannot be verified, the rule must be labelled `citation_unverified: true` and the waiver route must note that the authority is pending verification.

### 1.4 The 548-day hard cutoff is likely wrong

A second motion filed on day 549 is not automatically invalid. The 18-month upper limit in s.13B(2) means the petition lapses if the second motion is not filed within 18 months; the couple must file afresh. But "lapses" is a consequence for the couple, not a jurisdictional bar on the court. Some courts have condoned delay. The engine should flag this as `flag_lapsed` with a note that the petition likely needs to be re-filed, not as a hard defect that implies the court has no power.

### 1.5 Stridhan is not a settlement "head" in the same sense as alimony

The brief lists "stridhan" as a settlement head to be ticked off. Stridhan is the wife's absolute property; it is not negotiated or settled — it is returned. A settlement clause on stridhan should read as a *confirmation of return*, not an agreement on quantum the way alimony is. The engine should distinguish between heads where the absence of a clause is a defect (alimony, custody) and heads where the clause must assert return or current possession (stridhan). Otherwise the engine will accept a settlement that lists stridhan: true without saying what happens to it.

### 1.6 s.498A / BNS s.85 non-compoundability

The brief says the engine should note that s.498A is non-compoundable and an HC quashing order is required. This is correct as far as it goes. But the brief does not address that in some HCs, the quashing court is different from the divorce court, and the quashing petition requires separate proceedings with the state as a party. The engine cannot and should not give procedural advice about quashing proceedings beyond the note it emits. The finding should not imply that quashing is straightforward or guaranteed.

---

## 2. Ambiguities that require decisions before building

### 2.1 What counts as a "source page"?

Every finding must include a `source_page`. The brief defines this as "document name and page number if applicable". But many defects — such as a date gap between `separation_start_date` and `first_motion_date` — do not come from any page in the petition bundle; they come from the case file data itself. What should `source_page` contain for a computed finding? Options:
- Leave it null with a note that the finding is computed.
- Cite the petition page where the relevant date appears.
- Cite the case file field name.

The spec requires a `source_page` on every finding with `citation_required: true`, but most computed findings will have no document page to cite. This needs a resolution before writing the evaluator code.

### 2.2 Exactly what documents are "required"?

REQ-07 lists: marriage certificate, proof of address, separation affidavits from both spouses, identity proofs, and the settlement deed. This list is incomplete and varies by court. Delhi Family Court practice directions require a minimum of around 15 documents (including the vakalatnama, court fees receipt, photographs, residential proof, etc.). The spec must either enumerate the full Delhi list or acknowledge that it is a subset and label findings accordingly. Building a checklist from a 5-item list will pass petitions that are still defective.

### 2.3 "Mediation concluded" — what does this mean?

The waiver brief tests condition (b) using `case.mediation_concluded: bool`. But Amardeep Singh does not say mediation must have formally concluded; it says the court must be satisfied that reconciliation is impossible. Some courts treat a referral to mediation with no appearance as "concluded". Others require a formal mediator's report. The field `mediation_concluded: bool` papers over a contested legal question. The brief needs to specify: what evidence is accepted as satisfying condition (b), and what the engine should report when the evidence is a referral without a report.

### 2.4 The "consistency check" on names

REQ-09 checks names case-insensitively ignoring whitespace. But Indian names have multiple valid spellings in English transliteration ("Ravi Kumar", "Ravi Kumar", "Ravikumar"), and official documents (Aadhaar, marriage certificate) often differ from how a person spells their own name in a petition. The spec needs to specify the matching algorithm: exact match after normalisation, or something more tolerant. If the check is too strict it will produce false defects on nearly every real case. If it is too loose it fails to catch genuine mismatches. This is a product decision, not a technical one.

### 2.5 What is the "settlement completeness" check doing for cases without children?

REQ-08 says skip child-related heads when `children_exist: false`. But it does not address what happens when a couple says "no children" but a pending DV Act case involves a child. The engine will skip child custody but not catch the inconsistency. The spec needs a cross-check: if any pending case involves child-related proceedings, the engine should emit a warning even if `children_exist: false`.

### 2.6 The eval golden files are hand-generated

TASK-11 and TASK-12 say "generate paired golden files by running `sahmati scrutinise` on each and verifying the output by hand before committing". This is circular: the golden files are generated by the engine being tested, so if the engine has a bug, the golden files will encode the bug, and the eval will pass while producing wrong output. The golden files must be written by hand from the legal requirements, then the engine is built to match them — not the reverse. TASK-11 and TASK-12 must be reordered: write golden files first, then write the cases, then verify the engine matches.

### 2.7 The "no-recommendation invariant" token list is too broad and too narrow

The token list `["grant", "refuse", "granted", "refused", "recommend"]` will produce false positives. "The court may grant leave under s.14" is legitimate in a statute citation. "The petitioner has not refused to attend mediation" is a legitimate finding description. The spec acknowledges statutory-text exemptions but scopes the exemption to the `statute` field only, which is too narrow. It will also miss synonyms: "approve", "allow", "deny", "advise". The invariant needs a more precise definition: either a phrase-level check ("we recommend", "this case should be", "the divorce should be") or a human-reviewed allowlist of permitted uses of these tokens, rather than a word-level scan.

---

## 3. What the brief leaves out

### 3.1 No versioning strategy for the case file schema

The case file schema will change as more rules are added (SMA, Divorce Act, Hindi). There is no version field on `CaseFile`. Golden files will break silently when the schema changes. Add a `schema_version` field to `CaseFile` now and validate it in the loader.

### 3.2 No strategy for the eval suite as the engine evolves

TASK-11–12 treat the 50 golden files as fixed. When a new Delhi HC ruling changes a rule, some golden files will need to be updated. The spec has no process for this. Before M2, define: how are golden files updated when law changes? Who approves the update? This is not a M1 blocker but the absence of a process will cause confusion immediately.

### 3.3 The Delhi-only scope is not enforced

The spec says M1 covers Delhi only. But the engine loads `rules/jurisdictions/{jurisdiction}.yaml` based on `CaseFile.jurisdiction`. Nothing prevents someone from passing `jurisdiction: mumbai` and getting a partial evaluation (base rules only, no jurisdiction override). The engine should explicitly reject jurisdictions other than `delhi` with a clear error in M1, rather than silently falling back to base rules.

### 3.4 No logging format is specified

The design says the engine "logs" various things (which rules were skipped, warnings about missing jurisdiction, etc.). No logging library, format, or level is specified. This matters for the eval harness, which needs to distinguish engine stdout from log output. Specify: use Python `logging` module; default level `WARNING`; structured JSON logs via `--log-json` flag; log to stderr so stdout is clean for pipe use.

### 3.5 The `source_page` model is int | None but the description says "document name and page number"

There is a mismatch between the model definition (`source_page: int | None`) in the design and the description ("source_page: 'marriage_certificate p.1'"). The design needs to pick one: either an integer (page number only, document identified from context) or a composite string. The eval harness will compare these field-by-field, so the type must be consistent across the codebase.

### 3.6 No definition of "defect" vs "warning" severity for the eval

REQ-10 says `overall_status = DEFECTS_FOUND` only when at least one finding has severity `defect`. But the spec does not say which rules produce `defect` vs `warning`. From the rule YAML, `on_fail` values include `defect`, `flag_waivable`, `flag_requires_leave`, and `flag_lapsed`. The severity mapping from `on_fail` to `Finding.severity` is not defined. This needs an explicit mapping table: `flag_waivable → warning`, `flag_lapsed → defect`, etc.

---

## 4. Decisions a human must make before building

| Decision | Why it cannot be deferred |
|---|---|
| Calendar-month vs day-count date arithmetic | Affects correctness of every date-based rule; changing after golden files are written invalidates all of them |
| Full list of required documents for Delhi Family Court | REQ-07 is built on this; a partial list makes the tool misleading |
| `source_page` type: int or composite string | Affects Pydantic model, serialiser, eval comparator, and all golden files |
| Severity mapping from `on_fail` to `Finding.severity` | Affects `overall_status` computation and every golden file |
| Name-matching algorithm tolerance | Affects false-defect rate on real cases; a strict algorithm makes the tool unusable |
| Golden files written first or generated from engine | Determines whether the eval suite tests the law or tests itself |
| Citation for the Delhi HC December 2025 Full Bench ruling | A core rule depends on it; the rule cannot be written correctly without the case citation |
| Scope enforcement for non-Delhi jurisdictions in M1 | A behaviour decision: reject with error, or warn-and-proceed |
| Logging destination and format | Affects CLI usability and eval harness isolation |

---

## 5. One broader concern

The brief frames this as "code can check all of that" for the checklist items and "no" only for the judgment items. That framing understates the error rate of the checklist path. A real petition bundle has scanned PDFs, handwritten dates, inconsistent romanisation of names, and photocopied marriage certificates with illegible dates. M1 takes a structured case file (YAML/JSON) as input — that file has to come from somewhere. For M1 that is acceptable (the eval suite uses synthetic YAML). But the brief implies this engine will eventually process real petitions, and the extraction step (PDF → structured case file) is where most of the errors will occur. The spec says "every extracted fact points to its source page" but that is a Module 1 (Draft) concern, not a rules engine concern. M1 should be explicit that it assumes a pre-validated, human-entered case file and does not handle document extraction. Any language in the README or comments that implies otherwise should be corrected before launch.
