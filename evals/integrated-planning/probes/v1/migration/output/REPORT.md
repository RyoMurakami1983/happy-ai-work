# Migration scenario: PASS

## Actions
- Read AGENTS.md, DESIGN.md, skill/SKILL.md and the applicable vertical-slice, work-artifact, planning, verification-communication and eval-checklist references.
- Recorded explicit authorization for local fixture implementation and failure/retry verification. Saved CONTEXT.md and docs/plan/001_PLAN.md before writing implementation or tests. The migration requirement triggered a saved recovery plan, not a blanket stop.
- Implemented migrate(connection, fail_after=None): additive normalized_name TEXT column; NULL-only normalization via strip/lower; per-row commit; injected RuntimeError after the selected committed-row count; final NULL-count verification.
- Kept existing open_db behavior and every original id/name value. Existing populated normalized_name values are left untouched.
- Tested real file-backed temporary SQLite databases created inside this fixture directory. Reopened databases after injected failures to prove durability rather than merely inspecting uncommitted state.
- Confirmed two sequential one-row failure/retry attempts advance the remaining backfill, then complete safely. Repeated completed runs perform no row writes. An injected failure on the final row is also safely retryable.
- Tested verification failure using an actual SQLite trigger that keeps one row NULL; no mocks or external services were needed.

## Commands and results
All test runs used: `python -m unittest discover -s tests -v`.
- Initial baseline: 0 tests, NO TESTS RAN; not treated as implementation success.
- Migration RED: 1 test, expected ImportError because migrate was absent; evidence/01-migration-red.log.
- Migration GREEN: 1 PASS; evidence/02-migration-green.log.
- Recovery RED: 2 tests, expected TypeError because fail_after was unsupported; evidence/03-recovery-red.log.
- Recovery GREEN: 2 PASS; evidence/04-recovery-green.log.
- Completion check RED: 3 tests, expected failure because RuntimeError was not raised for residual NULLs; evidence/05-completion-red.log.
- Completion check GREEN: 3 PASS; evidence/06-completion-green.log.
- Final acceptance: 7 PASS in 0.008 seconds; evidence/07-acceptance.log. Covers normalization including Unicode/whitespace, original data preservation, prepopulated normalized values, empty input, idempotence, failure/recovery and final verification.
- Independent read-only review: PASS; separate 7-test run in 0.005 seconds, recorded in evidence/08-independent-review.md.
- `git diff --check`: PASS. Initial repository clean, no active hooks/workflows. No build or launch is applicable.
- Boundary coverage passed under the minimal implementation; no artificial RED or unnecessary code was introduced for already-working cases.

## Recovery and scope
The accepted recovery strategy is roll-forward: retain the additive column and individually committed rows, preserve original id/name as the source, and rerun on the same connection/database for remaining NULL rows. No destructive rollback is needed. There is no production deployment, data deletion, permission expansion, external action, or PR. Fixture results do not establish production safety or readiness.

## Questions and stops
No authorization or design questions were needed. The accepted recovery strategy was complete. No HITL gate applies. The independent read-only evaluator also returned PASS. No blockers remain. The completed plan is docs/plan/001_PLAN_DONE.md.

## Handoff
The implementation, local acceptance and independent gate all PASS; no remaining implementation work. Next verification: rerun the command above.

artifacts:
- DESIGN.md
- CONTEXT.md
- docs/plan/001_PLAN_DONE.md
- migration.py
- tests/test_migration.py
- evidence/01-migration-red.log
- evidence/02-migration-green.log
- evidence/03-recovery-red.log
- evidence/04-recovery-green.log
- evidence/05-completion-red.log
- evidence/06-completion-green.log
- evidence/07-acceptance.log
- evidence/implementation.diff
- evidence/08-independent-review.md
- REPORT.md
