# PLAN 001 — 状態フィルターと CSV 出力

## GOAL

承認済みの `DESIGN.md` を、実装時に再開できる2つの独立した振る舞い単位へ分ける。今回は計画のみを保存して停止する。

## Success Criteria / Behavior List

- `list_tasks(tasks, status=None)` は指定なしなら従来どおり全行を返し、指定時は状態が完全一致した行だけを入力順で返す
- フィルターで入力コンテナ・行を変更せず、返す行を保持する。空入力・一致なし・空文字の状態も確認する
- `export_csv(tasks)` は `id,status,title` の順のヘッダーを持つ CSV 文字列を返す
- `csv.DictWriter` を使用し、カンマ・引用符を正しく扱い、余分なフィールドを無視し、欠けた title を空欄にする
- CSV でも入力を変更せず、空入力はヘッダーのみとなる

## Out of Scope

ストレージ、UI、他の公開動作、異常な入力型の新しい契約、外部依存、PR、本番操作。今回のコード・test・設定変更とtest実行も対象外。

## Implementation Permission / Command Status

- 利用者発言: 「設計は承認済みです。implementで、タスク一覧の状態フィルターとCSV出力の実装計画だけを作ってください。今日は実装には着手しません。」
- 実装許可: 未取得。明示的な plan-only 指定があり、本日は実装しない
- 設計を再作成せず採用済み設計を使う。必要な計画は保存するため、計画工程の省略なし
- 確認済み既存 test command: `python -m unittest discover -s tests -v` (`AGENTS.md` に記載)
- 下記 RED / GREEN / acceptance はすべて将来の予定。今回は未実行

## Design Artifacts / Fixed Decisions

- 正本: `DESIGN.md`
- `tasks.py` に公開関数を維持し、`tests/test_tasks.py` から public interface を確認する
- CSV は標準ライブラリ `csv.DictWriter` とメモリ上の文字列バッファを使う
- 再設計、移行、外部成果物、HITL acceptance は不要

## Vertical Slices

### Slice 1: 状態指定で一覧を取得する

- Type: AFK
- Depends on: なし。開始には将来の明示的な実装許可が必要
- Done: 全件取得の互換性と完全一致フィルターが成立し、順序・行・入力非変更・空入力の公開契約を検証済み
- Test surface: `tasks.list_tasks`
- First test: open / closed / open の入力から open の2行だけが元の順序・行のまま返る
- RED command: `python -m unittest discover -s tests -v`
- RED expectation: 現行関数が `status` 引数を受け付けず TypeError
- GREEN command: `python -m unittest discover -s tests -v`
- Acceptance command: `python -m unittest discover -s tests -v`
- 各 test を1つ追加して実行し、その失敗を満たす最小実装を追加。既存実装で通る境界testは回帰証拠として区別する
- Out of scope: CSV、保存処理、ソート、行コピーへの変更

### Slice 2: タスクを CSV 文字列に出力する

- Type: AFK
- Depends on: なし。状態フィルターを呼び出す必要はない
- Done: ヘッダー、行、引用符、余分な列、欠けた title、空入力、入力非変更を public interface から検証済み
- Test surface: `tasks.export_csv` と標準 `csv.reader` による出力の読取り
- First test: 空入力に対して `id,status,title` ヘッダーだけの CSV を返す
- RED command: `python -m unittest discover -s tests -v`
- RED expectation: `export_csv` が未定義
- GREEN command: `python -m unittest discover -s tests -v`
- Acceptance command: `python -m unittest discover -s tests -v`
- 最初の test を GREEN にしてから、引用符付きの行、余分なフィールド、欠けた title、非変更の順で必要な test を1つずつ追加する
- Out of scope: ファイル保存、ダウンロード UI、フィルターとの結合処理

## Order Rationale / Verification

既存の一覧API拡張を最初の小さい tracer bullet とし、その gate 後に独立した CSV 出力へ進む。これは実依存ではなく、互換性を先に観測する順序。各 slice の先頭で契約を再確認する。

検証はローカルの合成入力による標準 unittest のみ。現状は短い test が1件で、長時間・外部資源を使用する検証はない。拡張後も数秒未満を想定するが未計測。実装再開時は各実行を30秒で制限し、timeout や失敗があれば診断してから再試行する。build / interactive launch は該当しない。

## Progress / Unknowns / Next Decision

- [x] 設計・現状・範囲の読取りと計画保存
- [ ] 実装許可
- [ ] 実装 bootstrap と baseline test
- [ ] Slice 1 の RED / GREEN / acceptance / gate
- [ ] Slice 2 の RED / GREEN / acceptance / gate
- [ ] 実装 completion handoff

設計内の範囲に実装を妨げる未確定事項はない。次に必要な判断は、別の日にこの範囲の実装開始を明示的に依頼すること。現時点で再確認質問はしない。計画完了を実装完了と扱わず、`PLAN_DONE` へ改名しない。

## Return Conditions

- FAIL: 実装後の test / acceptance 失敗は同じ slice の修正へ戻る
- Plan adjustment: 目的・AC・公開契約・許可・依存が維持される順序変更はこの計画に理由と再検証範囲を記載する
- REPLAN_REQUIRED: AC変更は要求の所有者、新しい構造・公開契約は設計の所有者、追加権限は利用者へ戻す

## Artifacts

artifacts:
  - DESIGN.md
  - CONTEXT.md
  - docs/plan/001_PLAN.md
