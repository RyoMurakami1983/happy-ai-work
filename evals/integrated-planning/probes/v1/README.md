# Integrated planning: public synthetic execution probes

2026-10-16. Six local synthetic scenarios were executed by three independent workers (two cases per worker). The author then inspected reports, final diffs and test results. These are shared development probes, not sealed hold-outs, blind grading, a baseline comparison, or a formal adoption record. No speed/token/general-quality improvement is inferred.

## Requests and observed outcomes

| Case | Request | Observed outcome |
| --- | --- | --- |
| plan-only | Approved design; make a plan for filtering and CSV, do not implement today | Saved PLAN and CONTEXT; source/tests unchanged; no test run or PLAN_DONE |
| approved | Implement both accepted behaviors from planning through local verification | Observed RED/GREEN; 9 tests pass; both slices complete without renewed permission |
| reorder | Resume legacy plan 021; same scope and AC; adjust order to reuse filtering fixtures | Reused same plan, filtering before CSV; 8 tests pass; no retired skill or renewed approval |
| migration | Implement accepted additive SQLite migration locally; verify partial-failure retry; production excluded | 7 tests pass, repeated durable failure/reopen/retry, original data preserved; independent migration review |
| contract-conflict | Preserve all imported duplicate rows under accepted design | In-memory reproduction retained 1/3 rows; structural conflict identified; source unchanged, REPLAN_REQUIRED |
| external-contract | Execute provider-dependent consumer plus independent formatting slice | Verifier reports missing artifact; consumer remains pending; independent fix passes RED/GREEN and acceptance |

Each directory has original `input/`, observed `output/` including REPORT and logs, and hashes of the exact copied candidate resources. The entrypoint hash is identical across all six cases. Before the final two cases, a static-review clarity fix changed planning.md to preserve historical implementation permission while marking the current request plan-only. Earlier cases used the prior wording; none involved historical permission plus a new plan-only constraint. That corner case is reviewed statically, not claimed execution-tested here.

External-contract's initial fixture accidentally used `name/source` instead of the verifier's `artifact/path`. The worker received this fixture correction before verification; the checksum was preserved. This is a fixture repair, not an implementation behavior success. Only a missing dependency was executed; checksum mismatch remains covered by existing verifier unit tests and static skill review. HITL stop semantics were reviewed statically, not exercised with a real user/device.

The temporary fixture skill copies are not included as discoverable skills. Candidate hashes preserve provenance; the reviewed implementation is in this PR. Logs contain only synthetic tasks, local commands and outcomes. Python source evidence uses `.py.txt` to avoid accidental discovery or linting of frozen fixtures. Copy an output directory to a temporary workspace, restore `.py.txt` to `.py`, then rerun its tests with `python -m unittest discover -s tests -v`; no such command is appropriate for the plan-only observation, and contract-conflict intentionally has no implemented fix.
