# Baseline instruction snapshot

The baseline generators in adoption evaluation 001 received the following public instruction block. Scenario prompts are versioned separately in `evals/skill-eval/cases.v3.json`.

> Preserve evaluation integrity. Never call a prior-aware grader independent, overwrite prior records, adopt with a contaminated/missing required holdout, store raw responses/transcripts publicly, or misuse A/B/C. A is ordinary decidable PASS/FAIL; B only genuine indeterminacy; C only safety or owner-approved deadline emergency. For final adoption or reevaluation called independent, ordinary prose does not substitute for this six-line checkpoint; select one value per line and include it in the same answer/record:
>
> checkpoint:
> - hold-out: valid | contaminated | missing | not-required
> - independence: valid | invalid — reason
> - prior record: preserved
> - new record: required | not-required
> - public artifact: sanitized-only — no public raw response or transcript
> - decision: <A | B | C> — <adopted | continued | rejected | PASS | FAIL>
>
> Same grader after FAIL is invalid; preserve old FAIL and require new grader/subagent plus new record. Model/time observations that do not change criteria are ordinary improvements; future measured values only, no inferred backfill.
