# Legacy implementation-plan

Goal: implement DESIGN.md. User permission: implement both features.
artifacts: DESIGN.md, docs/plan/021_PLAN_DONE.md

1. export_csv, AFK, no dependencies. Done: CSV acceptance in design passes.
2. status filtering, AFK, no dependencies. Done: filtering acceptance in design passes.
Verification: python -m unittest discover -s tests -v
Return: implementation-plan for ordering, technical-design for structural changes.

## Current execution contract (2026-10-16)
The legacy plan remains the same case and artifact. Current user instruction: 「以前作ったdocs/plan/021_PLAN.mdの両機能を実装してください。記録された対象範囲の実装許可は有効です。既存のフィルター試験を先に拡張した方がCSV試験にも利用できます。進め方は実際のコードに合わせて調整して構いません。対象範囲と受け入れ条件は変更しません。」

GOAL / Success Criteria: implement exactly DESIGN.md: exact optional status filtering with row order/identity and inputs preserved; CSV text with id,status,title header, correct quoting, ignored extra fields and empty missing title; cover empty input and mutation.
Out of Scope: storage changes, other public behavior, external actions, PR creation.
Design Artifacts: DESIGN.md; structures remain the independent public functions in tasks.py and standard-library csv.DictWriter.

### Execution-order adjustment
Execute filtering before CSV because tests/test_tasks.py already covers list_tasks and a shared task sample can exercise CSV next. Both are independent; no real dependency, AC, public contract, permission, HITL, or recovery condition changes. Prior one-test baseline passes; added behavior must gain fresh evidence. Ordering changes remain inside implement; the legacy return-to-implementation-plan instruction is superseded by this current skill.

### Slice 1: status filtering (AFK)
Behavior / Done: optional exact filter; omitted/None means all rows; retain order, row identity, and input. Empty/no-match result is empty.
Non-goal: CSV or storage changes.
Test surface: public list_tasks.
First test: test_filter_preserves_order_and_input.
RED command: python -m unittest discover -s tests -v
RED expectation: list_tasks does not accept status.
GREEN / Acceptance command: same command, including existing compatibility test and edge cases.

### Slice 2: CSV export (AFK)
Behavior / Done: public export_csv returns CSV accepted by csv.reader/DictReader with fixed header, quoted values, no mutation, extra fields ignored, missing title empty, and header-only empty input.
Non-goal: storage or any coupling between filtering and export.
First test: test_csv_round_trip_preserves_input, reusing the sample established for filtering.
RED command: python -m unittest discover -s tests -v
RED expectation: public export_csv is absent.
GREEN / Acceptance command: same command.

Verification: tiny synthetic unit suite only; no build, application launch, long-running tests, external dependency, workflow or active hooks. Expected under one second based on baseline. Baseline: 1 test PASS.
Return Conditions: test failures are FAIL and fixed in current slice; only contract/structural/permission changes require REPLAN_REQUIRED. No HITL gate.
Completion: rename this existing plan to 021_PLAN_DONE.md only after both slices PASS and completion handoff is saved.

## Completion gate
Slice 1 PASS: expected status keyword TypeError was observed (01-filter-red.log); minimal change passes (02-filter-green.log); compatibility, empty/no-match, explicit None, exact empty-string and nonmutation checks pass (03-filter-acceptance.log).
Slice 2 PASS: expected missing export_csv ImportError was observed (04-csv-red.log); DictWriter implementation passes (05-csv-green.log); final 8-test acceptance passes (06-final-acceptance.log), including header-only empty export and newline round trip. Existing filter tests were rerun after CSV implementation. Refactor check: code remains two independent functions with no unnecessary abstraction or mocks; no further refactor needed. git diff --check passes.
Both accepted features are implemented. No questions, pauses, new permissions, remaining implementation work, or HITL gates. No PR, production, or external operations. Evidence files are under evidence/; handoff is REPORT.md.
