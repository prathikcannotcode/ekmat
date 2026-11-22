# AI for Mutual Consent Divorce: Research and Repo Plan

Nov 21, 2026 · Prathik

## Bottom line

Not a bad idea, but the headline version is, and the data points somewhere the speech didn't. A 24/7 AI court saves little time because the judge isn't the slow part; the law's six-month wait is. In the best data I found, a study of Mumbai's family court, mutual consent cases closed in a median of one hearing and about 221 days on average, most of it the statutory wait.

- What holds up: most of a mutual consent file is checklist work: separation period, proof of marriage, jurisdiction, settlement terms, waiver conditions. Code can check all of that.
- What doesn't: the judge's real job is making sure consent is free, especially the wife's, and that money and children are dealt with fairly. That can't go to a model, and Section 13B(2) says "the court" passes the decree. An AI decree needs Parliament to amend the law.
- Where the time actually goes: the six-month cooling-off period. Courts can waive it under Amardeep Singh, but family courts apply that unevenly and High Courts keep reversing them. A tool that shows, case by case, whether the waiver conditions are met goes after the real delay. Build that first.
- Backlog caveat: in the Mumbai study (2010 to 2014), mutual consent was about 34% of filings but only about 10% of pending cases. It's already the fast lane. Speeding it up helps couples far more than it dents the 5 crore figure. Bagchi's procedural ideas (affidavits, extensions, listing) are the bigger backlog lever.
- The bigger idea underneath: France, Brazil and Japan already let couples divorce by consent without a judge. The honest reform is a registrar or notary route with a human consent check, not an "AI court". The repo can be the reference build for both.

## What Justice Bagchi said (verified)

He spoke on Saturday 21 November 2026 at the JUSTECH National Conclave, run by Dharmashastra National Law University, Jabalpur, at PDPM IIITDM Jabalpur. Sources: Bar & Bench report, The Week, event notice.

| Proposal | What he said |
|---|---|
| 24/7 AI divorce courts | "hive off the mutual divorce cases and have 24/7 AI divorce courts", for ease of access and so human time isn't spent on "non-adjudicatory" work |
| Early-hearing applications | Should go to AI, "completely taken away from the human agency"; criteria like pendency, case age, cases involving women |
| Procedural directions | AI to handle affidavits, extensions of time, getting cases ready for hearing |
| Predictive verdicts | AI predictions in cheque bounce, land acquisition and money recovery cases, shared with judges before arguments |
| Pre-hearing stages | "from the date of filing till arguments, you don't require a judge" |

His limits: human agency is "the most precious virtue", and AI has no place in constitutional adjudication. His backlog figure was "over five crore cases". In January 2026 he said technology can never replace justice itself. He also sits with CJI Surya Kant on the bench hearing a plea against unregulated AI in courts. So this is a cautious judge carving out mutual consent as "routine". That label, non-adjudicatory, is the claim to test.

## How mutual consent divorce works in India today

It depends on personal law, and only Muslim couples can already do it without a court. Everyone else needs a joint petition, a waiting period and a decree from a family court.

| Law | Section | Separation before filing | Notes |
|---|---|---|---|
| Hindu Marriage Act 1955 (Hindus, Sikhs, Jains, Buddhists) | 13B | 1 year | Second motion 6 to 18 months after first; s.14 bars filing within 1 year of marriage without leave |
| Special Marriage Act 1954 (civil and interfaith) | 28 | 1 year | Same structure as 13B |
| Divorce Act 1869 (Christians) | 10A | 2 years in the text | Kerala HC read it down to 1 year (2010), followed by Karnataka HC (2014); Kerala HC then struck down even the 1-year minimum (2022). Position varies by state |
| Parsi Marriage and Divorce Act 1936 | 32B | 1 year | Filed as a joint suit; verify second-motion rule before coding |
| Muslim personal law | Mubara'at, khula | None | Extra-judicial; no court needed for mubara'at |

### The Hindu Marriage Act route, step by step

1. First motion: both spouses file together, stating they've lived apart for a year, can't live together, and agree the marriage should end.
2. Reconciliation: the court must first try to reconcile them (s.23(2) HMA; s.9 Family Courts Act). In practice, a referral to mediation or counselling.
3. Cooling off: the second motion can come no earlier than 6 months and no later than 18 months after the first.
4. Second motion and decree: the court hears both, makes "such inquiry as it thinks fit", checks the marriage happened and the petition is true, and checks consent wasn't obtained by force, fraud or undue influence (s.23(1)(bb)). Then it passes the decree.
5. Exit at any time: either spouse can withdraw consent until the decree, even after the 18 months (Sureshta Devi v. Om Prakash, 1991; Hitesh Bhatnagar v. Deepa Bhatnagar, 2011). Continuing consent is what gives the court power to decree at all.

### Case law that has loosened it

- Amardeep Singh v. Harveen Kaur, (2017) 8 SCC 746: the 6-month wait is directory, not mandatory. A family court can waive it if the year plus six months have already passed, mediation has failed, everything is settled (alimony, custody, pending cases), and waiting would only prolong the agony. The waiver can be sought a week after the first motion.
- Shilpa Sailesh v. Varun Sreenivasan, Constitution Bench, 1 May 2023: the Supreme Court can use Article 142 to grant mutual consent divorce without the second motion, and can dissolve a marriage for irretrievable breakdown. Only the Supreme Court has this power.
- Delhi HC full bench, December 2025: the one-year separation under 13B(1) is also waivable, through the s.14 proviso, and the two waivers are decided independently. Binding in Delhi only.
- Gujarat HC, January 2026: quashed a family court that rejected a joint petition as "premature" for lack of a formal waiver application.
- Calcutta HC, July 2026: a family court can't dismiss a mutual consent petition because the couple skipped mediation.

The pattern: the law already says "if both agree and everything is settled, don't make them wait". Family courts apply it unevenly and High Courts keep correcting them. Uneven application of clear rules is exactly what a rules engine fixes.

## Pendency

NJDG showed more than 5.03 crore pending cases across all courts in August 2026. Family courts alone had over 1.11 lakh pending in Kerala, over 70,000 in Bihar and over 66,000 in Maharashtra (LiveLaw, Dec 2025).

Best proxy for the case-type split: Prashant Iyengar's study of about 32,000 Mumbai Family Court cases filed 2010 to 2014.

| Case type | Avg. hearings | Median hearings | Avg. days to decision |
|---|---|---|---|
| Mutual consent divorce | 2 | 1 | 221 |
| Fault-based divorce | 9 | 7 | 451 |
| Restitution of conjugal rights | 9 | 7 | 474 |
| Maintenance under CrPC | 14 | 12 | 648 |

Mutual consent was about 34% of filings, 42% of disposals and only about 10% of pending cases; 53% finished in a single hearing. One court, a decade old: a pointer, not proof.

## What the judge actually does in a 13B case

| Task | Type of work | Can code do it? |
|---|---|---|
| Jurisdiction (s.19 HMA: where married, where the respondent lives, where they last lived together, or where the wife lives) | Checklist | Yes |
| Proof the marriage happened | Document check | Yes, with flags |
| One year since marriage (s.14) and one year apart (13B(1)) | Checklist | Yes for the check; no for granting a waiver |
| Petition is true | Documents plus statements | Partly: cross-checks dates, names, addresses |
| Reconciliation attempt | Process | Scheduling and logging yes; doing it no |
| Amardeep waiver | Four set conditions plus discretion | Lay out the evidence, never decide |
| Settlement complete (alimony, stridhan, custody, child support, property, and a plan for pending 498A, DV and maintenance cases) | Checklist | Yes |
| Settlement fair | Judgment | No |
| Consent free of force, fraud, undue influence | Judgment | No, flags only |
| Children's welfare | Judgment | No |
| Consent still holds at second motion | Confirmation | Capture yes; judge confirms |
| Decree | Template | Yes |

The hard row is consent. In India, "mutual" can mean family pressure, a wife with no income signing away maintenance, or stridhan held back as leverage. A faster pipeline with no consent check makes a coerced divorce faster too. Any design has to make that row stronger, not thinner.

## The rules already on the books

Draft Regulations for Use of AI in Courts, 2026. Released by the Supreme Court's AI Committee on 3 June 2026. Comments due 20 June, extended to 15 July 2026. No final version found yet.

- Permitted: case management and scheduling, research and summarisation, translation and transcription, chatbots for litigant help, accessibility tools, fraud detection and document verification, court analytics.
- Prohibited outright: AI-only decisions in judicial outcomes, AI adjudication without human control, risk scoring for bail, recidivism or credibility, opaque AI affecting rights, predictive profiling of people in proceedings, surveillance, undisclosed AI material as evidence, anything that compromises confidentiality.
- Also required: an AI register of tools, an incident database, DPDP alignment, limits on sending data to external systems, and disclosure certificates from parties who use AI.
- One LiveLaw analysis reads the draft as also banning outcome prediction.

Kerala High Court policy, 19 July 2025: district judges can't use AI for findings, reliefs, orders or judgments. Only tools approved by the High Court or Supreme Court are allowed; every use must be logged.

Supreme Court White Paper on AI and the Judiciary, November 2025: in-house tools over public chatbots, audit trails, independent verification of every output, personal responsibility of the judge for AI-assisted work.

The statute: Section 13B(2) says "the court" passes the decree. An AI decree needs Parliament to amend HMA, SMA, the Divorce Act and the Parsi Act.

Build "AI prepares, human decides"; it survives either outcome of the draft rules.

## How other countries skip the judge

| Country | Route | Who checks | Safeguards | Since |
|---|---|---|---|---|
| France | Agreement drafted by two lawyers, filed with a notary | Each spouse's own lawyer; notary checks procedure and deadlines | 15-day reflection period; lawyers from different firms; judge required if a minor child asks to be heard | 2017 |
| Brazil | Public deed at a notary (Law 11.441) | Notary, with a lawyer present | No minor children at first; since CNJ Resolution 571 (Aug 2024), allowed with minors if custody and support were settled in court | 2007 |
| Japan | Kyogi rikon: form filed at the city office, two witnesses | Registrar; no review of terms | Minimal; about 90% of Japanese divorces | Long-standing |
| England and Wales | Online service; conditional order reviewed by a court legal adviser | Legal adviser | 20-week wait; no-fault since April 2022 | Online 2018 |

Lesson: replace the judge with a cheaper human checkpoint, and let software do the file work.

## The repo: Sahmati

Sahmati ("consent") is an open-source toolkit that makes an Indian mutual consent divorce case decree-ready at filing and leaves every decision to a person. Name is a placeholder: Sahamati is already the name of India's Account Aggregator industry body. Ekmat is an alternative.

### Design rules

1. Every module maps to a use the draft regulations permit. Nothing outputs "grant" or "refuse".
2. Rules are code, not prompts. Each statutory condition is a versioned rule with its citation. The model handles intake conversation, plain-language explanation, translation and extraction, and every extracted fact points to its source page.
3. A person checks consent. The tool collects answers and raises flags; it never certifies consent. No emotion analysis, voice stress or credibility scores. Flags are fixed rules on facts the spouses themselves state, shown to both of them, never predictions.
4. Runs locally or on court servers. No case data leaves. (Draft regs on external transfer, DPDP Act, s.11 Family Courts Act in camera.)
5. Either spouse can withdraw consent until the decree, in one step, logged, with no questions asked.

### Modules

| Module | Used by | What it does | Permitted-use basis |
|---|---|---|---|
| 1. Draft | Couple, lawyers, legal aid | Guided interview by personal law; joint petition, affidavits, settlement deed, Amardeep waiver application | Litigant assistance |
| 2. Settlement checklist | Couple, lawyers | Forces every term: alimony/maintenance, stridhan, custody, visitation, child support, property, plan for pending cases (498A IPC/BNS 85 non-compoundable, needs HC quashing; DV Act and s.125 CrPC/s.144 BNSS can be withdrawn) | Litigant assistance |
| 3. Scrutiny engine | Court registry | Jurisdiction, s.14 bar, separation, timelines, document consistency, missing annexures; defect list and scrutiny report, each finding linked to a page | Document verification, case management |
| 4. Waiver brief | Registry, judge | Four Amardeep conditions with evidence for each, plus the local HC's position; no recommendation | Summarisation |
| 5. Consent protocol | Counsellor, mediator, judge | Structured separate interview with each spouse in their language; factual red flags such as no independent income plus maintenance waived | Supports a human; no scoring |
| 6. Judge's file | Family court judge | One screen: scrutiny report, settlement summary, flags, template decree; judge edits and signs; audit log and AI register entry | Case management |
| 7. Policy pack | Policymakers | Model amendment for a registrar or legal-adviser route for fully settled cases, plus a metrics spec | Not a court tool |

### Build brief

Start with HMA s.13B in one jurisdiction (Delhi) and get the scrutiny engine right before anything with a model in it.

Stack:
- Python 3.12, Pydantic models for the case file, FastAPI for a local server.
- Rules in YAML, each with id, statute, condition, citation, jurisdiction, valid_from. A small deterministic engine evaluates them. No model in this path.
- Jinja2 templates rendered to DOCX and PDF for petitions, affidavits, waiver applications and the draft decree.
- An LLM adapter with two backends: Claude API for lawyers, and a local model (Ollama) for court deployments where data can't leave.
- English and Hindi first.
- Also ship as a Claude Code plugin with skills like /sahmati:draft, /sahmati:scrutinise, /sahmati:waiver-brief, same pattern as Vigil and nodal.

Repo layout:

```
sahmati/
  rules/hma_13b/          # YAML rules, one file per condition
  rules/jurisdictions/    # HC-specific positions (e.g. delhi.yaml)
  engine/                 # rule evaluator, scrutiny report builder
  intake/                 # guided interview, settlement checklist
  consent/                # separate-interview protocol, flag rules
  templates/              # petition, affidavits, waiver, decree
  judge_file/             # one-screen summary, audit log, AI register
  llm/                    # adapter: claude, local
  evals/                  # synthetic cases + golden outputs
  policy/                 # model amendment, metrics spec
  plugin/                 # Claude Code skills
```

Rule example:

```yaml
id: hma13b.separation_one_year
statute: Hindu Marriage Act 1955, s.13B(1)
condition: separation_start <= first_motion_date - 1 year
on_fail: flag_waivable
waiver_route: s.14 proviso (Delhi HC FB, Dec 2025)
citation_required: true
```

Evals:
- 50 synthetic case files, clearly fictional, half with planted defects (wrong jurisdiction, date gaps, missing stridhan clause, name mismatch).
- Golden scrutiny reports for each; the engine must match them exactly.
- Red-team consent scenarios (wife with no income waiving maintenance, custody given up with no visitation) that must raise flags.
- Hard checks: zero outputs containing a grant or refuse recommendation; every finding cites a statute and a source page.

Milestones:
1. Rules engine, scrutiny report and waiver brief for 13B, with a CLI and the eval suite. Waiver brief first.
2. Draft module and templates.
3. Consent protocol, judge's file, audit log.
4. SMA s.28 and Divorce Act s.10A; Hindi.
5. Policy pack, README, demo, launch.

Ground rules:
- Apache-2.0 for code, CC BY 4.0 for the policy pack.
- Synthetic data only. No real matrimonial records.
- README states plainly: not legal advice, not deployed in any court, built to the draft regulations' permitted uses.

## Risks

| Risk | What could happen | Mitigation |
|---|---|---|
| Coercion laundering | A pressured spouse moves through faster | Consent protocol, separate interviews, human hearing, one-step withdrawal |
| Forged documents and impersonation | Fake certificates, someone else on the video call | Document verification; rely on the court's own ID checks |
| Fragmented law | Five personal-law regimes, each HC with own rules and forms | Start with 13B in Delhi; jurisdiction files per HC |
| Rules change | Draft regulations finalised differently | Map every module to a named permitted use |
| Optics | "AI ends marriages" headlines | Lead with "AI prepares, judge decides" |

Legal wrinkles: court-side modules likely fall within the DPDP Act exemption for courts in judicial functions (s.17(1)(b)); litigant-side intake doesn't, so it needs notice and consent. Some HCs hold that withdrawing consent after a full settlement needs a reasonable ground, so the withdrawal step should record and notify, never judge.

## Open questions

- What share of family court pendency is mutual consent? NJDG doesn't break it out.
- Parsi s.32B: confirm the second-motion procedure before writing its rules.
- Divorce Act s.10A: confirm which HCs follow Kerala's one-year reading.
- Will the final regulations keep the outcome-prediction ban?
- Pilot partner: Kerala (highest family court pendency, strictest AI policy).
