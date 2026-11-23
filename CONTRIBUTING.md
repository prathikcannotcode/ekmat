# Contributing

## Ground rules

- **No real case data.** Every case file in this repository is synthetic and clearly fictional. Never commit a real petition, name or date.
- **Ekmat decides nothing.** No output may say a decree, leave or waiver should be granted or refused. `tests/test_ekmat.py` scans rule files and outputs for recommendation phrases. Reword the text; don't loosen the guard.
- **Legal wording lives in YAML.** Rules are in `ekmat/rules/`. Python computes facts and picks which message applies; it doesn't write legal sentences.

## Changing or adding a rule

1. Edit or add the YAML in `ekmat/rules/hma_13b/`. Each rule has an `id`, a `citation`, a `verified` flag, and `messages`, each message with an `on_fail` severity.
2. If it's a new rule id, add its check function to `CHECKS` in `ekmat/engine.py`. The engine refuses to start if a rule and a check don't pair up.
3. Add cases to the `CASES` table in `evals/make_cases.py`. Write the expected findings from the law before you run the engine, then run `python evals/make_cases.py`.
4. Run `ekmat eval` and `pytest`. Both must pass.

## The verified flag

Set `verified: true` only after reading the statute, rule or judgment itself, not a news report or summary. Record what you read and which paragraphs in the rule's `note`. If part of the rule rests on something unread, leave it `false` and say which part in the note. The README lists what's verified and what isn't, so update it in the same change.
