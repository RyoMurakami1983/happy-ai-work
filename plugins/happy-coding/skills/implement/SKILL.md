---
name: implement
description: >
  実装契約を受け取り、bootstrap 確認、vertical slice 分割、TDD loop、slice gate、completion handoff まで進める。
  technical-design / implementation-plan / issue から実装可能な契約を受け取り、PR やふりかえりではなくローカル実装を完了したいとき。
---

# implement — TDD で実装して閉じる

実装契約を、観測可能な vertical slice ごとに TDD で通してから handoff します。`implementation-plan` がある場合はそのslice境界を維持し、planを省略した単一の明確な変更だけをここでslice化します。
この skill は実装フェーズだけを扱います。PR 作成、PR review 対応、pre-PR review、furikaeri は別 skill に任せます。

## こんなときに使う

- 実装契約からローカル実装を始めたいとき
- 受け入れ条件を vertical slice に分けたいとき
- TDD の RED/GREEN/REFACTOR を崩さず進めたいとき
- slice ごとに evidence gate を通したいとき
- 実装完了後に handoff だけ残して閉じたいとき

## Core Loop

```text
implementation contract
  -> bootstrap check
  -> slice contract
  -> RED
  -> GREEN
  -> REFACTOR
  -> slice gate
  -> next slice or completion handoff
```

## ワークフロー: TDD で実装して閉じる

### ステップ 1 — 実装契約を確認する

次が揃っていれば実装に入ります。不足が要求をブロックする場合は `interview-with-docs`、構造判断なら `technical-design`、順序やslice分割なら `implementation-plan` に戻します。

- 目的、対象、非対象
- 受け入れ条件
- 主要な user-visible behavior または外から観測できる contract
- handoff に `artifacts:` フィールドがある場合は、その意味（保存済み path か、例外理由付きの `conversation-only` か）
- 実行する test / build / launch command
- 失敗時の戻り先: `FAIL` は実装修正、`REPLAN_REQUIRED` は前段へ戻す

実装に不要な設計議論をここで広げません。必要十分な契約に圧縮してから進みます。

### ステップ 2 — bootstrap を軽く確認する

対象 repo で次を確認します。

- repo instructions、local hooks、workflow の有無
- git 管理状態
- build / test / launch command
- interactive app なら `references/interactive-app-bootstrap-checklist.md`
- 複数リポで `plan.md` の `dependencies.contracts.requires` がある場合だけ、`checkpoints/contract_verify.py` で required artifact を検証する
- handoff に `artifacts:` フィールドがあり path が列挙されている場合は、その file が repo に存在することを確認する。存在しない場合は `REPLAN_REQUIRED` として `implementation-plan` に戻す
- `artifacts: conversation-only` の場合は `exception reason:` があり、利用者の明示指定またはsmall one-sliceの例外条件を満たすことを確認する。複数repo、複数slice、public contract、migration / operationsを伴う場合は `REPLAN_REQUIRED` とする

bootstrap の不足が今の slice を壊すなら修正します。関係ない整備は実装 scope に混ぜません。

### ステップ 3 — slice contract を固定する

planがある場合はslice境界を変更せず、直前にcontractを再確認します。planを意図的に省略した単一の明確な変更だけ、1受け入れ条件または1ユーザー行動を1 vertical sliceとして切ります。slice境界の変更が必要なら実装を始めず `REPLAN_REQUIRED` として `implementation-plan` へ戻します。最初のsliceはtracer bulletとして必要な層を薄く縦断します。

各 slice で必ず短く固定すること:

- 対象振る舞い
- 非対象
- public interface 経由の確認観点
- 最初に追加または更新する test
- `RED` を確認する command と期待する失敗理由
- `GREEN` を確認する command
- acceptance command

層ごとに「DB だけ」「UI だけ」「テストだけ」を横に広げる horizontal slice は避けます。

### ステップ 4 — TDD loop を回す

各 slice は次の順で進めます。

1. **RED**: 失敗する test を 1 つ書く。失敗理由が対象振る舞いと一致することを確認する。
2. **GREEN**: その test を通す最小実装だけを入れる。
3. **REFACTOR**: 振る舞いを変えずに読みやすさ、重複、境界を整える。
4. 次の test が必要なら同じ slice 内で繰り返す。

既存コードの保守性改善が主目的の場合は、[safe-refactoring.md](references/safe-refactoring.md)を読み、守る振る舞いと比較手段を先に固定する。

TDD の規律:

- 1 test → 1 minimal implementation を守る
- test は public interface 経由の振る舞いを主語にする
- private method や内部 collaborator の呼び出し回数を固定しない
- mock は外部 API、時刻、乱数、ファイル I/O、コマンド実行など system boundary に限る
- speculative code を足さない
- all tests first の horizontal slicing をしない

docs-only / config-only など RED が成立しない slice では、TDD を装いません。代わりに verification command と期待結果を slice contract に明記します。

### ステップ 5 — slice gate で評価する

各 slice の最後に、実装者の自己正当化ではなく証拠として gate を通します。

詳細観点が必要なら[eval-checklist.md](references/eval-checklist.md)から関係する項目だけを使います。

- RED を実際に見たか
- RED の失敗理由は対象振る舞いと一致したか
- GREEN を実際に見たか
- acceptance command は通ったか
- public interface 経由で確認しているか
- speculative code、不要な抽象化、過剰な mock を入れていないか
- contract と違う発見があれば `FAIL` か `REPLAN_REQUIRED` に分類したか

verdict:

- `PASS`: 次の slice へ進む
- `FAIL`: 同じ slice の実装に戻る
- `REPLAN_REQUIRED`: `technical-design` または `implementation-plan` に戻る。要求自体が曖昧なら `interview-with-docs` に戻る

次に該当する場合は、利用可能なら実装者とは別の動的subagentへ、slice contract、差分、RED/GREEN/acceptance evidenceだけを渡して独立評価を依頼します。

- GUIやinteractive runtimeの観測が必要
- trust boundary、migration、data loss、concurrency等の高risk変更
- 回帰範囲が広い
- 実装者の自己評価だけではevidenceが弱い
- ユーザーが独立評価を指定

独立評価者は修正せず、先に `PASS / FAIL / REPLAN_REQUIRED` と根拠を返します。並列実装は行わず、verdict確定後に単一writerが修正します。subagentが利用できない場合は、実装時の推論から離れてchecklistと差分を読み直します。

interactive evidenceが必要な場合だけ、対応するtemplateを読みます。

- web: [playwright.md](references/runtime-evidence/playwright.md)
- Windows desktop: [flaui.md](references/runtime-evidence/flaui.md)
- Python GUI / pygame: [python-gui.md](references/runtime-evidence/python-gui.md)

### ステップ 6 — completion handoff で閉じる

全 slice が `PASS` したら、実装フェーズを閉じます。

handoff に残すもの:

- 完了した slice
- 実行した command と結果
- 変更した主な file / artifact
- 確認に使った design / plan artifact path
- 残件、または明示的に対象外にしたもの
- 次に開く file または確認 command
- 戻り先 skill がある場合はその理由

`docs/plan/NNN_PLAN.md` が今回の実装 plan なら、完了時に `docs/plan/NNN_PLAN_DONE.md` へリネームします。未完了項目が残る場合は、次の plan または handoff に切り出します。

## 注意点

- 実装中に仕様の穴を埋めない。判断が必要なら前段へ戻す。
- phase / slice は自動停止点ではない。blocker、HITL 判断、`REPLAN_REQUIRED` がなければ次へ進む。
- 並列化する場合も、各 worker に slice contract と TDD loop を渡す。未確定の slice を並列化しない。
- PR、review、furikaeri はここで扱わない。必要になった時点で別 skill を起動する。

## 共通リソース

- `references/interactive-app-bootstrap-checklist.md` — interactive app の bootstrap 前提
- `references/interactive-app-comparable-harness-contract.md` — interactive app の比較前提
- `references/safe-refactoring.md` — 振る舞いを維持した小さい改善単位
- `references/eval-checklist.md` — slice gateの詳細観点
- `references/runtime-evidence/` — interactive appで必要時だけ使うevidence template
- `checkpoints/contract_verify.py` — 複数リポ環境での contract 検証
