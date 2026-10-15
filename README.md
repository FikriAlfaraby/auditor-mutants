# auditor-mutants

**Plant known violations in recorded agent trajectories, and count what an agent auditor catches.**

[iFixAi](https://github.com/ifixai-ai/iFixAi) (28k stars) audits AI agents. Its trajectory auditor reads
what an agent actually did, recorded as a trajectory of events, and checks it against a business policy:
who may act, which actions need a human's approval, how authority is delegated, how much may be spent,
and whether an answer cites its sources. It answers CLEAR, BLOCK or INCONCLUSIVE.

This repo tests the auditor the way mutation testing tests a test suite. It starts from iFixAi's own
compliant example (an agent refunds an account on a supervisor's delegated authority and approval),
changes one thing at a time, and asks the auditor again:

- **violation**: one plainly broken rule, such as an approval used twice or a refund outside the agent's
  scope. The auditor should BLOCK.
- **judgment**: a trajectory a careful reviewer would not pass, such as an approval ID that exists
  nowhere in the record. The auditor should not say CLEAR, and for some, should BLOCK.
- **probe**: a legitimate trajectory a strict auditor might wrongly flag. It should be CLEAR.
- **control**: an unchanged compliant trajectory. CLEAR.

## Predictions first

Every mutant carries the decision I predicted for iFixAi, read from its code at commit
[1559983](https://github.com/ifixai-ai/iFixAi/tree/15599839eccfc2ffcf181b0ca3651413416a9d40), with the
lines that lead to it. The predictions are in `predictions/predictions.json` and were tagged
`v0.1-prereg` on GitHub before any mutant was audited. Results come after the tag.

## Run it

```
uv sync
uv run auditor-mutants inputs   # mutants/<id>/policy.json and trace.jsonl, predictions/predictions.json
uv run auditor-mutants run      # audits each mutant with iFixAi's own CLI into runs/<id>/
uv run auditor-mutants score    # results/summary.md
uv run pytest
```

Every input is in `mutants/`, so each case can be checked with iFixAi alone:
`ifixai trajectory audit mutants/<id>/policy.json mutants/<id>/trace.jsonl --output /tmp/<id>`.

No model is called and nothing is spent: the auditor is deterministic.
