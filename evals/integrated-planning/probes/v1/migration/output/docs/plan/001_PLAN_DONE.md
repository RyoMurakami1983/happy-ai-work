# Local SQLite migration implementation plan

## GOAL / Permission
Implement and verify the accepted DESIGN.md in temporary local SQLite fixtures, including rerun after partial failure.
User request: 「この設計の移行をローカルfixtureで実装・検証してください。本番DBの変更は対象外です。途中失敗後の再実行も確認してください。」
This is explicit local implementation authorization, not a plan-only request. No separate plan approval is required. Production authority is not inferred.

## Success Criteria / Behavior List
- migrate(connection, fail_after=None) adds normalized_name TEXT if absent.
- Only NULL normalized_name values are filled using name.strip().lower().
- Every processed row is committed; optional failure raises RuntimeError after the specified processed-row count.
- Repeated invocation resumes remaining rows without overwriting populated values or old id/name rows.
- Full completion verifies no NULL normalized_name remains before returning.

## Out of Scope / Design Artifacts
DESIGN.md is the normative artifact. Preserve open_db and the accepted schema/function contracts. No production operation, data deletion, destructive rollback, access expansion, external action, PR, or unrelated refactor.

## Vertical Slice: resumable normalization (AFK)
A single observable behavior encompasses additive schema preparation, row backfill, injected failure, and recovery; these are not independent DB-only/test-only slices.
Test surface: public migrate/open_db with real temporary file-backed SQLite connections, reading results through SQL and reconnecting to verify durable commits.
First test: test_migrates_preserving_original_rows.
RED command: python -m unittest discover -s tests -v
RED expectation: migrate is absent. Subsequent one-test loops cover unsupported injected-failure behavior and missing completion verification.
GREEN / Acceptance command: python -m unittest discover -s tests -v
Done: normalization, additive schema, empty/repeated runs, existing populated values, committed partial failure/reopen/retry, and final NULL check pass; independent gate passes.
No HITL criterion. Migration is independently evaluated because persistence/recovery is high risk even in this safe fixture.

## Dependencies, Compatibility and Recovery
Input: people(id INTEGER PRIMARY KEY, name TEXT NOT NULL). Additive nullable column leaves original consumers' id/name reads and every original value intact. Existing non-NULL normalized values are not overwritten. No other consumer or deploy switch is in scope.
Stages: create column if absent; select remaining NULL rows; update and commit each; verify NULL count is zero. Users/data affected: synthetic fixture rows only.
Failure detection: injected RuntimeError after N committed rows; final verification rejects remaining NULLs. SQLite errors propagate.
Recovery: approved roll-forward via rerunning migrate on the same persisted database; completed rows are excluded by the NULL predicate. Per-row commits intentionally remain after failure; destructive rollback is neither required nor permitted. Original id/name acts as the preserved normalization source. Tests recreate their own temporary fixture and clean up only those test-generated files.
Recovery confirmation: reopen the fixture, inspect exactly N completed rows and unchanged original data, call migrate again, assert zero NULLs and original values retained, rerun once more for idempotence.
Do not generalize fixture success to production. A production rollout/backup decision would need a separate request and authorization.

## Verification and Return Conditions
Baseline: clean repo; no active hooks/workflows; 0 tests (NO TESTS RAN), so not implementation evidence. No build/interactive launch command is needed.
Tests use a handful of local synthetic rows, standard library only; expected under one second (small SQLite fixtures; no long/load/external tests).
FAIL: fix implementation/evidence in this slice. REPLAN_REQUIRED: only a changed contract, new structural decision, or missing authority; unaffected safe local work can continue.
Save evidence and REPORT.md, then rename to 001_PLAN_DONE.md only after all accepted behavior and independent gate pass.

artifacts:
- DESIGN.md
- CONTEXT.md
- docs/plan/001_PLAN_DONE.md

## Completion gate: PASS
All accepted behavior is implemented and verified. Evidence: 01/02 migration RED/GREEN, 03/04 partial-failure recovery RED/GREEN, 05/06 completion-verification RED/GREEN, 07 acceptance (7 PASS). Boundary additions needed no further implementation; no artificial REDs. Refactor check found no needless abstraction or internal mocks; no behavior-changing refactor was required.
Independent read-only evaluation PASS with a separate 7-test run in 0.005 seconds; evidence/08-independent-review.md records the verdict. Original id/name and existing normalized values remain intact, durability is observed after close/reopen, and completion checks residual NULLs.
No remaining implementation item, authorization question, design return, or HITL gate. Only local synthetic data was touched. Completion handoff: REPORT.md. Next verification: python -m unittest discover -s tests -v.
