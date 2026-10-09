# PLAN 003 — CSV取込プレビュー

## GOAL

CSVの形式不備を更新前に発見し、対象行を確認してから取込を確定できるようにする。これは架空の記入例であり、アプリ実装は含まない。

## Success Criteria

| AC | 観測可能な結果 | Slice |
| --- | --- | --- |
| AC1 | 必須列がない入力は理由付きで拒否し更新しない | S1 |
| AC2 | 有効・無効行をプレビューで判別できる | S1、S2 |
| AC3 | 対象選択と取消を操作して確認できる | S2 |
| AC4 | 確認した対象だけ取込み、失敗時は成功と表示しない | S3 |

## Out of Scope

- 新しい構成・認証方式の決定、アプリの実装、実サービスへの接続。
- 自動の対象補正、バックグラウンド再試行、データ移行。

## Implementation Permission / Command Status

- 実装許可は未取得。この例での依頼は計画作成。
- 下記commandは作成予定・未実行。例にはテストrunnerもアプリも含まない。
- 日程・工数は未見積り。検証のbudgetは上限案であり実測値ではない。

## Progress

- [ ] S1 入力を検証して模擬プレビューを表示
- [ ] S2 対象選択と取消を操作確認
- [ ] S3 確認した対象をテスト用接続へ反映

## Design Artifacts / Fixed Decisions

既存の取込画面が公開操作へ依頼し、更新adapterを呼ぶ境界を維持する。入力判定を画面へ埋め込まず、adapterの呼出し有無を観測できるtest seamを使う。認証と更新方式は設計側の既決契約に従い、検証先の権限確認は開始条件として残す。

## Behavior List

- [ ] 必須列欠落のCSVは理由付きで拒否し更新adapterを呼ばない。
- [ ] 模擬入力の有効・無効行を画面で分けて表示する。
- [ ] 対象行の選択変更・取消・確定が一致する。
- [ ] 接続失敗を成功と扱わない。

## Vertical Slices

### S1 入力検証から模擬プレビューまで

- Type: AFK
- Depends on: なし。G0は必要。
- Done: 公開操作経由で形式不備と模擬プレビューを観測でき、更新adapterの呼出しはゼロ。
- Test surface: 画面の公開操作と表示状態、模擬更新adapterの記録。
- First test: 必須列欠落の理由が表示され、更新されないこと。
- RED command: `python tests/check_import.py --case missing-column`
- RED expectation: 形式不備の理由または更新ゼロの保証が未実装で失敗。
- GREEN command: `python tests/check_import.py --case missing-column`
- Acceptance command: `python tests/check_import.py --slice S1`
- Verification context: 合成CSV3種、実接続なし。所要時間は不明、60秒・1回の上限案。画面のruntime evidenceを保存する。
- Out of scope: 実データの更新、対象選択の操作感、認証設定。

### S2 対象選択と取消

- Type: HITL
- Depends on: S1
- Done: 行の選択変更と取消が画面と確認対象へ同じ状態で反映される。
- Test surface: 公開選択操作、表示状態、確定候補。
- First test: 選択解除した行が確定候補から外れること。
- RED command: `python tests/check_import.py --case deselect-row`
- RED expectation: 選択状態と確定候補の同期が未実装で失敗。
- GREEN command: `python tests/check_import.py --case deselect-row`
- Acceptance command: `python tests/check_import.py --slice S2`
- Verification context: 合成入力10行、自動検証の時間は不明、60秒・1回の上限案。操作確認は10分のセッション上限案。
- Out of scope: 実接続、更新adapterの実装。

#### HITL Review Contract

- Reviewable milestone: 合成CSVのプレビューで対象を変更できる画面。
- Launch: 予定 `python app.py --demo`。実装時に同じbuildを起動する実在手順へ確定。
- Review actions: 行を選択、解除、取消、再選択し確定候補を確認。
- Expected observations: 対象数・表示状態・候補の一致。取消時は更新されない。
- Resume condition: 操作結果が一致すれば次へ。不一致はS2修正、業務判断の不足は要求整理へ戻す。

### S3 確認した対象の取込

- Type: HITL
- Depends on: S2、G1
- Done: 検証先に確認済み対象だけ反映し、接続失敗時に成功表示しない。
- Test surface: 更新adapter、確認対象、完了表示。
- First test: 接続失敗で成功状態にならないこと。
- RED command: `python tests/check_import.py --case connection-failed`
- RED expectation: 失敗時の完了表示抑止が未実装で失敗。
- GREEN command: `python tests/check_import.py --case connection-failed`
- Acceptance command: `python tests/check_import.py --slice S3 --profile authorized-test`
- Verification context: 管理者が許可した検証先のみ、架空2行。所要時間は不明、15分・1セッションの上限案。対象と変更内容を事前通知。
- Out of scope: 本番更新、認証方式変更、失敗時の自動復旧。

#### HITL Review Contract

- Reviewable milestone: 検証先の反映結果と画面の結果を確認できる状態。
- Launch: 実装時にG1の対象を指定する実在手順へ確定。
- Review actions: 対象2行の確定、検証先への反映確認、接続失敗時の表示確認。
- Expected observations: 確認対象と反映結果が一致。失敗時は完了扱いにならない。
- Resume condition: G1の対象・許可を確認してから実行。結果不一致はS3修正。権限未確認ならS3のみ保留。

## Dependencies / Start Conditions

| 条件 | 内容 | 影響 | 担当と再開の証拠 |
| --- | --- | --- | --- |
| G0 | 実装開始の明示指示 | 全slice | 利用者の対象・範囲を含む発言 |
| G1 | 検証先と更新権限・許可範囲 | S3 | 管理者・連携担当による確認記録 |

G1待ちの間も、G0取得後であればS1/S2を進められる。G0未取得なら実装を始めない。

## Order Rationale

S1で入力拒否とプレビューを薄く縦断し、S2で人の判断に必要な操作を確認する。S3はS2とG1の成立後に進める。矢印は実装依存であり、工数・暦日・並列実装の指示ではない。

## Risks / Unknowns

検証先の権限が未確認。S3へ影響し、画面操作や模擬入力の検証とは区別する。未確認の権限をplanで決めず、構造変更が必要なら設計へ戻す。

## Artifacts

このファイルと [表示用入力](003_presentation.json)、[依存図](003_plan/diagrams/dependencies.svg) は実在する資料。記載したアプリ・commandは未実装。

## Return Conditions

- FAIL: 同じ要求・設計内の不具合は対象sliceの修正へ戻す。
- REPLAN_REQUIRED: 依存順は計画へ、更新境界・認証等の構造判断は設計へ戻す。
- 要求不足: 取込対象・完了条件が変わるなら要求整理へ戻す。
