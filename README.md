# Ekmat

Ekmat (एकमत, "of one mind") checks an Indian mutual consent divorce file before it reaches the judge, and leaves every decision with the judge.

On 21 November 2026 a Supreme Court judge proposed 24/7 AI divorce courts for mutual consent cases. In the Mumbai Family Court study we used (cases filed 2010 to 2014), mutual consent cases closed in a median of one hearing and about 221 days. Most of those days were the statutory six-month wait, not time waiting for a judge. Since *Amardeep Singh v. Harveen Kaur* (Supreme Court, 2017), a family court can waive that wait, but family courts apply the waiver unevenly. Ekmat goes after that delay: it checks the file at filing and sets out the waiver facts for the court. It never says whether to grant anything.

> Not legal advice. Not deployed in any court. Built to the permitted uses in the Supreme Court's Draft Regulations for Use of AI in Courts, 2026. Synthetic data only.

## What milestone 1 does

For a petition under s.13B of the Hindu Marriage Act in a Delhi family court, Ekmat reads a structured case file and writes:

- **A scrutiny report.** Each finding cites a statute or case and the case-file field or document it came from. It covers jurisdiction (s.19), the s.14(1) one-year bar, one year of separation (s.13B(1)), the second-motion window (s.13B(2)), the waiver application timing, missing documents, missing settlement terms, and names and dates that disagree across documents.
- **A waiver brief.** It covers the four Amardeep Singh conditions, with the facts on file and the facts missing for each, plus the Delhi High Court's current position. It grades nothing. Every condition ends with what only the court can assess.
- **The dates that matter:** earliest first motion, earliest waiver application, the second-motion window, and when eighteen months of separation are reached.

There is no model anywhere in this path. The rules are YAML in [ekmat/rules](ekmat/rules), the legal wording lives there too, and every rule carries a `verified` flag. Findings from unverified rules say so.

## What Ekmat never does

- Outputs "grant", "refuse" or "eligible". A test scans every rule file and every eval output for recommendation phrases.
- Assesses consent, the fairness of a settlement or a child's welfare. Every report lists these under "Not checked".
- Scores anyone's credibility, emotion or hardship.
- Sends case data anywhere. It runs locally.

## Run it

```
python -m venv .venv
.venv/Scripts/pip install -e ".[dev]"      # Linux/macOS: .venv/bin/pip
ekmat scrutinise evals/cases/D15.yaml --waiver --format md
ekmat eval
pytest
```

Exit codes: 0 means no defects, 1 means defects found (or an eval mismatch), 2 means bad input. A case file for any court outside Delhi is rejected, not partly checked.

Start from [evals/cases/C01.yaml](evals/cases/C01.yaml) to see the case file format. The schema is in [ekmat/models.py](ekmat/models.py).

## Evals

There are 57 synthetic cases: 26 without defects and 31 with planted gaps. The answer keys were written by hand from the statute before the engine ran, so the eval tests the law rather than the engine's own output. [evals/make_cases.py](evals/make_cases.py) holds the table of cases and expected findings.

## Permitted uses under the draft regulations

| Module | Status | Permitted-use basis |
|---|---|---|
| Scrutiny report | M1, built | Document verification; case management |
| Waiver brief | M1, built | Research and summarisation |
| Drafting (petition, affidavits, waiver application) | M2 | Litigant assistance |
| Consent protocol (separate interviews, factual flags) | M3 | Supports a human; no scoring |
| Judge's file, audit log, AI register entry | M3 | Case management |
| Special Marriage Act s.28, Divorce Act s.10A, Hindi | M4 | |
| Policy pack: registrar or legal-adviser route | M5 | Not a court tool |

## Verified, and not yet verified

Checked against the court's own text:

- The Delhi waiver position: *Shiksha Kumari v. Santosh Kumar*, MAT.APP.(F.C.) 111/2025 (Full Bench, 17 December 2025), paras 41-44, 49 and 57.
- s.19 and the last-residence rule: *Poonam v. State (NCT of Delhi)*, MAT.APP.(F.C.) 285/2026 (7 September 2026), paras 10 and 13-14.

Not yet verified:

- **Documents.** The checklist follows the Hindu Marriage Rules 1979 (Delhi High Court): proof of marriage (r.4(a)), each spouse's non-collusion affidavit (r.8), and the r.13 affidavit for a s.14 application. It's read from a secondary reproduction, not the Delhi Gazette. Address proofs and photographs aren't in the rules, so a missing one is reported as info.
- **s.19 for a joint petition.** Reading s.19(ii) "respondent" as either spouse. *APS v. Nil*, 2026 LiveLaw (Mad) 432 is reported to support it. That's persuasive and unread, and no Delhi ruling was found.
- **Leap-day starts.** 29 February plus a year is treated as 28 February, under the corresponding-date rule. No Indian ruling on leap-day starts has been read.

The research behind the design is in [docs/research.md](docs/research.md). [docs/spec-review.md](docs/spec-review.md) records where we departed from the first spec.

## Licence

Code: Apache-2.0. The policy pack (M5) will be CC BY 4.0.
