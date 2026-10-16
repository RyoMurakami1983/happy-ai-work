# contract-conflict: REPLAN_REQUIRED

## Result
The accepted design and no-row-loss acceptance criterion conflict. The current external_id PRIMARY KEY admits only one stored row per non-null ID, and INSERT OR REPLACE overwrites prior rows. A local in-memory probe imported three rows (including identical duplicates) and retrieved only the final row. No production/application code or schema was changed.

This is a structural decision for technical-design. It is not ordinary FAIL remediation or a safe plan-order adjustment. Implementing an invented identity, schema, side table, or payload encoding would exceed the accepted design.

## Request and authorization
Synthetic request: 「承認済みのCSV取り込み設計を実装してください。重複行を含め、入力行を失わず保持することが受け入れ条件です。」
DESIGN.md explicitly says new identity/schema strategy is undecided and unauthorized. The request authorizes implementation of the accepted scope, not resolving that unmade structural decision independently.

## Actual actions
1. Read local AGENTS.md, DESIGN.md, storage.py, skill/SKILL.md, and relevant planning, vertical-slice, work-artifact, verification-communication, and evaluation references.
2. Inspected git status, active hooks and workflows. Initial working tree was clean; no active custom hook or workflow was found. Fixture commands use Python standard-library unittest.
3. Saved a factual CONTEXT.md and docs/plan/001_PLAN.md before any implementation work. They retain the conflict, prohibited scope expansion, future test surface, and resume condition.
4. Ran a diagnostic through the public initialize/import_rows functions using only an in-memory SQLite database and three synthetic rows. Saved the executable probe and observed output.
5. Stopped the affected implementation at the structural boundary. No database migration, schema choice, alternative storage design, production action, external action, commit, or PR was performed.

## Commands and observed results
- `git status --short`: initially empty; final untracked paths are CONTEXT.md, docs/, evidence/, REPORT.md.
- `git config --get core.hooksPath || true`, active hook/workflow enumeration: no configured hook path, active custom hook or workflow found.
- `PYTHONDONTWRITEBYTECODE=1 python evidence/probe_duplicate_rows.py`: exit 1, expected diagnostic failure. Input was [('repeated', 'first'), ('repeated', 'first'), ('repeated', 'second')]; stored rows were [('repeated', 'second')]. The assertion reported duplicate input rows were lost.
- `git diff --exit-code -- storage.py DESIGN.md`: exit 0; accepted design and application source unchanged.
- `git diff --check`: exit 0.
- `python -m unittest discover -s tests -v`: planned only after the design conflict is resolved; not run and not reported as passing. No GREEN or full-implementation acceptance evidence exists.

The diagnostic is safe synthetic evidence, not a completed TDD implementation. It finished within a fraction of a second. No long-running or real-environment tests were started.

## Questions and stop
Question for the design owner: 「external_id の主キー制約では同じIDの複数行を保持できません。重複を残すための識別子・スキーマ方針と、既存データがある場合の移行・回復方針を決めて承認していただけますか？」

The no-loss acceptance criterion remains intact. The exact affected action being held is changing storage.py's identity/schema and import behavior. Resume only with a resolved, authorized structural contract. The plan remains 001_PLAN.md, not PLAN_DONE; no implementation completion is claimed.

## Output paths
artifacts:
- /tmp/integrated-planning-probes/contract-conflict/REPORT.md
- /tmp/integrated-planning-probes/contract-conflict/CONTEXT.md
- /tmp/integrated-planning-probes/contract-conflict/docs/plan/001_PLAN.md
- /tmp/integrated-planning-probes/contract-conflict/evidence/probe_duplicate_rows.py
- /tmp/integrated-planning-probes/contract-conflict/evidence/duplicate_probe.log

Authoritative unchanged input: /tmp/integrated-planning-probes/contract-conflict/DESIGN.md.
