# PLAN 001: Preserve all imported CSV rows

## Goal and success criteria
Every row passed to storage.import_rows must remain retrievable, including duplicate external_id values and identical duplicate rows. Preserve the accepted structure in DESIGN.md. No external or production actions.

## Authorization
Synthetic request: 「承認済みのCSV取り込み設計を実装してください。重複行を含め、入力行を失わず保持することが受け入れ条件です。」
This authorizes implementation within the accepted design, not a new identity/schema strategy.

## Design artifacts and conflict
- DESIGN.md: reuse existing table and external_id identity; a replacement schema/identity is not decided or authorized.
- storage.py: imports.external_id is TEXT PRIMARY KEY and INSERT OR REPLACE overwrites earlier rows sharing a key.
- Status: REPLAN_REQUIRED. This is a structural contract conflict, not a slice-order adjustment or ordinary implementation failure.

## Slice contract
- Behavior: import duplicate input rows without loss, observable through initialize/import_rows and database reads.
- Non-goals: invented row identifiers, altered schema, encoded batches in payload, another table, changed deduplication acceptance criteria, migrations, production execution.
- First behavioral test: import two rows with the same non-null external_id and different payloads; expect both rows. Also preserve identical duplicate rows.
- Diagnostic command: PYTHONDONTWRITEBYTECODE=1 python evidence/probe_duplicate_rows.py
- Expected current failure: only the final row for the repeated external_id remains.
- Future RED/GREEN/acceptance command after design resolution: python -m unittest discover -s tests -v
- AFK: the diagnostic can run locally; implementation depends on a design decision, not subjective UI review.

## Verification scope
One in-memory SQLite fixture with three synthetic rows. No files or user data are imported. Expected duration under one second, based on fixture size; no long-running tests. Each command is a single attempt with no external resources.

## Return and resume conditions
Return to technical-design with observed schema and row-loss evidence. Ask the design owner to choose and authorize an identity/schema strategy that preserves duplicate rows, including migration/recovery requirements if existing data is affected. Do not silently weaken the no-loss acceptance criterion. Resume implementation only after the contradiction is resolved; then establish RED/GREEN and acceptance evidence against that revised contract.

## Progress
- Bootstrap inspected: local standard-library fixture; initially clean git tree; no active custom hooks or workflows found.
- Diagnostic executed: expected failure, exit 1; three input rows became one stored row. See evidence/duplicate_probe.log.
- Implementation blocked. No completed-plan rename is appropriate.

artifacts:
- DESIGN.md
- CONTEXT.md
- docs/plan/001_PLAN.md
