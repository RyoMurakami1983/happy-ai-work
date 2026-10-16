# Local migration fixture
DESIGN.md is the accepted contract. Migration adds nullable normalized_name and backfills only NULL values from name.strip().lower(); original id/name are retained. Per-row commits and retry are the approved roll-forward recovery mechanism. Only temporary local SQLite databases are authorized. Production changes, destructive cleanup, external access and PRs are excluded.
