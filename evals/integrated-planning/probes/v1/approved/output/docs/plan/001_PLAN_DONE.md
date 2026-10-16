# PLAN 001 — 状態フィルターと CSV 出力

## GOAL / Success Criteria

承認済み `DESIGN.md` の2機能をローカルで実装・検証する。

- `list_tasks(tasks, status=None)` の全件取得互換性、指定状態の完全一致、入力順・行の保持、空入力・一致なし、入力非変更
- `export_csv(tasks)` の `id,status,title` 順ヘッダー、正しいカンマ・引用符処理、余分な列の無視、欠けた title の空欄、空入力、入力非変更

## Out of Scope

ストレージ、UI、既存の他の公開動作、異常入力型の新契約、外部依存、PR、本番操作。

## Implementation Permission / Command Status

- 利用者発言: 「この承認済み設計の状態フィルターとCSV出力を、必要な計画からローカル実装・検証まで進めてください。両機能の実装を許可します。」
- 両機能の実装・ローカル検証が明示的に許可済み。計画承認や slice 間の追加承認を求めない
- 設計は既存の承認済み文書を再利用。計画は保存し、TDD / gate を省略しない
- `AGENTS.md` の既存 command: `python -m unittest discover -s tests -v`
- 実行時は `PYTHONDONTWRITEBYTECODE=1 timeout 30s python -m unittest discover -s tests -v` としてローカル合成testだけを行う
- この計画保存時点では検証未実行。実績は `docs/evidence/` と完了追記で区別する

## Design Artifacts / Fixed Decisions

- `DESIGN.md` を契約正本とする
- 公開関数は `tasks.py`、test は `tests/test_tasks.py`
- CSV は標準 `csv.DictWriter` と文字列バッファ、外部パッケージなし
- 2関数は独立。外部成果物、migration、HITL、interactive runtime はない

## Vertical Slices / Behavior List

### Slice 1: 状態指定で一覧を取得する

- Type: AFK
- Depends on: なし
- Done: 完全一致フィルターと互換性、順序・行保持、入力非変更、空入力・一致なし・空文字状態を検証
- Test surface: `tasks.list_tasks`
- First test: open / closed / open から open 行だけを同じ順序・行で返す
- RED command: `python -m unittest discover -s tests -v`
- RED expectation: 現行関数が `status` キーワードを受け付けず TypeError
- GREEN command: `python -m unittest discover -s tests -v`
- Acceptance command: `python -m unittest discover -s tests -v`
- Out of scope: CSV、保存、ソート、行のコピー

### Slice 2: CSV 文字列を出力する

- Type: AFK
- Depends on: なし。Slice 1 の関数に依存しない
- Done: ヘッダー、引用符付き値、余分な列、欠けた title、空入力、入力非変更を検証
- Test surface: `tasks.export_csv`、出力の `csv.reader` による復元
- First test: 空入力からヘッダーのみの CSV 文字列を返す
- RED command: `python -m unittest discover -s tests -v`
- RED expectation: `export_csv` が未定義
- GREEN command: `python -m unittest discover -s tests -v`
- Acceptance command: `python -m unittest discover -s tests -v`
- Out of scope: ファイル保存、UI、フィルターとの結合

## Order / Verification / Gates

既存API拡張を小さい tracer bullet として先に行い、gate 後は追加確認待ちを入れず独立した CSV へ進む。各 slice は直前に契約を再確認する。test を1件追加 → 実際の RED → 最小実装 → GREEN → 必要ならリファクターを繰り返す。既に通る境界・非変更testを無理に失敗させず、追加回帰証拠として区別する。

現在のsuiteは短い合成testが1件。新規testもメモリ内のデータのみで、長時間試験・外部資源なし。数秒未満の見込み（未計測）で1回30秒timeout。失敗・timeoutは診断してから再試行し、成功を装わない。build / launch は該当しない。

各 slice の gate: 対象に一致する実際の RED、GREEN、全件acceptance、公開APIテスト、過剰な抽象化・mockなしを確認して PASS とする。低risk局所変更で独立reviewを必要とする条件なし。最終diffを再読し、全対象PASS後に PLAN_DONE へ改名する。

## Progress

- [x] 指示・設計・skill・参照文書の読取り、実装許可確認
- [x] 保存計画
- [x] Bootstrap / baseline test
- [x] Slice 1 PASS
- [x] Slice 2 PASS
- [x] Completion handoff

## Risks / Unknowns / Return Conditions

開始を妨げる未確定事項なし。空文字状態を未指定と混同しない。入力の不正型の扱いを勝手に拡張しない。

- FAIL: test / acceptance が落ちれば同じ slice の最小修正へ戻る
- Plan adjustment: 公開契約・AC・採用済み構造・許可・依存を保つ順序変更なら理由と再検証範囲を更新して継続
- REPLAN_REQUIRED: 要求変更は要求所有者、構造・公開契約変更は設計所有者、追加権限は利用者へ戻す

## Artifacts

artifacts:
  - DESIGN.md
  - CONTEXT.md
  - docs/plan/001_PLAN_DONE.md
  - REPORT.md
  - docs/evidence/

## Slice 1 Gate

PASS. Baseline: 1 test passed. First new test failed with the expected unexpected-`status` TypeError (`01-filter-red.txt`); minimal implementation then passed 2 tests (`02-filter-green.txt`). Additional boundary, empty-string, nonmutation, and compatibility cases were added individually and already passed; they are regression evidence, not invented RED cycles. Acceptance: 5 tests passed (`05-filter-acceptance.txt`). Public interfaces only; no mock or extra abstraction. Refactor review found no behavior-preserving change needed. `git diff --check` passed.

Slice 2 contract rechecked: independent CSV-text API, stdlib DictWriter, no storage/UI, first test is empty/header behavior, missing function expected as RED. Authorization still covers this slice; continue without another approval.

## Slice 2 Gate / Completion Handoff

PASS. Empty export first failed because `export_csv` did not exist (6 tests, one error; `06-csv-header-red.txt`), then passed with the minimal DictWriter header implementation (`07-csv-header-green.txt`). The row/quoting test failed against header-only output (7 tests, one failure; `08-csv-rows-red.txt`), then passed after adding `writerows` (`09-csv-rows-green.txt`). Extra-field input failed with the expected DictWriter ValueError (8 tests, one error; `10-csv-extra-red.txt`), then passed with `extrasaction="ignore"` (`11-csv-extra-green.txt`). The nonmutation regression passed on addition (`12-csv-nonmutation.txt`).

Refactor: moved repeated test imports to module scope and wrapped the writer construction. Final acceptance after refactor: 9 tests passed in 0.001s (`13-final-acceptance.txt`). `git diff --check` passed; final source/test diff was read against DESIGN.md. No mock, speculative feature, new dependency, or storage change. Both independent slices are complete; no HITL gate or unresolved requirement exists.

Bootstrap evidence: initial worktree clean, no configured core.hooksPath, no active local hooks, no `.github` workflow directory. Only one pre-existing local unittest; no build or interactive launch command needed. All verification commands used local synthetic inputs and 30-second timeouts; no timeout occurred.

Changed: `tasks.py`, `tests/test_tasks.py`, `CONTEXT.md`, this plan, local verification logs, and `REPORT.md`. Design and skill files unchanged. No external actions, PR, or commit. All planned behavior is implemented and locally tested; no real-environment claim is made.

Next check: `python -m unittest discover -s tests -v`. Completion report: `REPORT.md`. No return-to-owner or further approval is required. Rename this plan to `docs/plan/001_PLAN_DONE.md` only now that both slices passed.
