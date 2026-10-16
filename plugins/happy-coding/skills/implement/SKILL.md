---
name: implement
description: >
  合意済みの要求・設計・issueから実装順とvertical slicesを計画し、許可された範囲をTDDと検証で完了する。
  実装計画だけの依頼にも使い、その場合は計画で停止する。PR作成やふりかえりは別skill。
---

# implement — TDD で実装して閉じる

実装に必要な計画と実行を一つのloopで扱います。必要な粒度で順序・slice・検証を決め、承認済みの範囲を実装します。構造判断は`technical-design`が所有します。
計画だけの依頼（plan-only）では、調査と計画成果物の作成までで停止し、実装コード・test・設定の変更や実行へ進みません。実装の明示依頼がある場合は、計画への別の承認を機械的に挟みません。計画への賛意だけは実装許可にしません。
PR 作成、PR review 対応、pre-PR review、furikaeri は別 skill に任せます。

## こんなときに使う

- 実装計画だけを作りたいとき、または計画からローカル実装まで任せたいとき
- 受け入れ条件を vertical slice に分けたいとき
- TDD の RED/GREEN/REFACTOR を崩さず進めたいとき
- slice ごとに evidence gate を通したいとき
- 実装完了後に handoff だけ残して閉じたいとき

## Core Loop

```text
implementation contract
  -> lightweight plan or saved plan
  -> plan-only handoff OR authorized implementation
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

まず依頼が計画のみか実装までかを確認します。以下を契約として整理し、順序やslice分割はこのskill内で決めます。要求の不足は `interview-with-docs` / `to-prd`、新しい構造判断は `technical-design` へ戻します。計画作成には実装許可を要求せず、実装に入る直前にその許可を確認します。

- 目的、対象、非対象
- その範囲の実装開始について利用者の明示的な依頼・承認と、その根拠となる発言。handoffの自己申告だけでなく、利用可能な会話と最新の制約を照合する。Issue選択、PRDや計画への賛意、設計レビューのPASSを代替にしない
- 工程を省略した場合は、その工程と理由、同じ範囲・省略内容への許可。根拠不足や範囲変更があれば影響部分を開始せず確認へ戻す。取得済みの同じ許可は聞き直さない
- 受け入れ条件
- 主要な user-visible behavior または外から観測できる contract
- handoffに`finalized_contract`がある場合は、採用済みnormative source、exclusions、unknowns、主要target trace
- handoff に `artifacts:` フィールドがある場合は、その意味（保存済み path か、例外理由付きの `conversation-only` か）
- 実行する test / build / launch command
- 失敗時の戻り先: `FAIL` は実装修正、計画調整はこのskill内、真の契約変更は `REPLAN_REQUIRED` として所有者へ戻す

実装に不要な設計議論をここで広げません。必要十分な契約に圧縮してから進みます。

### 実行前の計画 — 必要な粒度で作る

[垂直スライスと短縮条件](references/vertical-slice.md)に従い、観測可能な振る舞い、AC、実依存、順序、検証、戻り条件を短く整理します。複数sliceという理由だけで別skillや確認待ちへ戻しません。明確な低risk変更は会話内の短い計画でよく、後続判断・互換性・移行・運用・複数repoが関わる場合は[計画の詳細](references/planning.md)を読みます。

保存はsaved-by-defaultです。必要な計画を`docs/plan/NNN_PLAN.md`へ保存し、[成果物規約](references/WORK_ARTIFACTS.md)に従って実在pathまたはconversation-onlyの例外理由を残します。既存の保存済みplan、`finalized_contract`、HITL契約は読み込み、今回の許可・現状と照合して再利用します。旧skillで作ったplanの再作成や移動を要求しません。

plan-onlyなら、計画、未確定事項、許可の状態、次に必要な判断を返してここで停止します。計画済み・レビューPASSを実装済みと報告せず、PLAN_DONEへの改名も行いません。

### ステップ 2 — bootstrap を軽く確認する

検証commandの実行前に[検証の通知と報告](references/verification-communication.md)を読む。全件suiteに含まれる長い試験の目的・合成/実環境・所要時間の見込みを事前通知し、終了時は結果・未確認・必要な判断を伝える。通知で承認済み作業を再確認せず、短い通常testに待ちを増やさない。

対象 repo で次を確認します。

- repo instructions、local hooks、workflow の有無
- git 管理状態
- build / test / launch command
- interactive app なら `references/interactive-app-bootstrap-checklist.md`
- 複数リポで `plan.md` の `dependencies.contracts.requires` がある場合だけ、`checkpoints/contract_verify.py` で required artifact を検証する
- handoff に `artifacts:` フィールドがあり path が列挙されている場合は、その file が repo に存在することを確認する。存在しない場合は、誤記か欠落かを調べ、根拠が揃う計画はこの計画段階で修復する。未確認の契約を推測して実装しない
- `artifacts: conversation-only` の場合は `exception reason:` があり、成果物規約の例外条件を満たすことを確認する。保存が必要なら実装前に計画を保存する。利用者が保存禁止を指定し、安全な引継ぎと両立しない場合は競合だけ確認する

bootstrap の不足が今の slice を壊すなら修正します。関係ない整備は実装 scope に混ぜません。

### ステップ 3 — slice contract を固定する

planの有無を問わず、直前にslice contractを確認します。新しい事実により分割・統合・順序を変えるときは、目的・AC・公開契約・採用済み構造・許可範囲・実依存・HITL条件・回復可能性を維持できるか確認します。維持できる調整は理由と影響する検証を計画に更新し、このskill内で継続します。slice境界や順序の変更だけを`REPLAN_REQUIRED`にしません。
これらの契約を変更する、根拠が不明、または追加権限が必要なら影響部分を止めて該当所有者へ戻します。外部前提待ちは影響sliceだけを保留し、独立して許可済みの作業は進められます。最初のsliceは必要な層を薄く縦断するtracer bulletを優先します。

各 slice で必ず短く固定すること:

- 対象振る舞い
- 非対象
- public interface 経由の確認観点
- 最初に追加または更新する test
- `RED` を確認する command と期待する失敗理由
- `GREEN` を確認する command
- acceptance command

planでHITL review contractが指定されたinteractive sliceでは、reviewable milestone、launch方法、代表操作、期待結果、再開条件も固定する。人間の主観判断や実端末・外部app確認がacceptanceに含まれる場合、その判断を自動testの成功で代替しない。

`finalized_contract`がある場合は、そのsliceと追加する主要な恒久targetがどのnormative sourceに対応するかも確認します。exclusion由来の新しい責務が必要になった、sourceが不明、または採用decisionが変わった場合は実装で補完せず`REPLAN_REQUIRED`とします。

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
- `REPLAN_REQUIRED`: 要求・ACなら `to-prd` / `interview-with-docs`、構造・公開契約なら `technical-design`、権限なら利用者へ戻す。順序・分割だけの安全な調整は計画を更新して継続する

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

### HITL review gate（必要なsliceのみ）

自動gateを通過して利用者が直接触れられる状態になったら、HITL review contractがあるsliceだけを明示的なreview milestoneとして渡す。

- 同じbuildを起動するcommandまたは手順
- 利用者が行う1〜5個の代表操作
- 各操作で期待する表示、状態遷移、操作感
- 自動確認済みの範囲と、人間の判断が残る範囲
- feedback受領、承認、または`REPLAN_REQUIRED`となる再開条件

状態は`code complete`、`runtime verified`、`user validated`を区別する。build/testと自動runtime evidenceだけで`user validated`と報告しない。feedbackで不具合が見つかった場合は再現loopを作れるなら`debug-and-fix`、contractの誤りなら前段へ戻る。

HITLの結果がsliceのacceptanceに含まれる場合は、自動gateが通っても`HITL pending`として保持し、feedbackまたは承認を得るまでsliceを`PASS`やcompletion handoffに進めない。HITLが完成後の探索的な製品評価でありacceptanceをブロックしない場合だけ、`user validated`が未完了であることを残してローカル実装フェーズを閉じられる。

HITL review contractがなく、自動runtime evidenceでacceptanceを確定できるsliceは、利用者入力を待つためだけに停止しない。

### ステップ 6 — completion handoff で閉じる

全 slice が `PASS` したら、実装フェーズを閉じます。

handoff に残すもの:

- 完了した slice
- 実行した command と結果
- 変更した主な file / artifact
- 確認に使った design / plan artifact path
- 残件、または明示的に対象外にしたもの
- `finalized_contract`がある場合は、追加した主要な恒久targetとnormative sourceの対応、およびexclusion由来の残骸がない確認結果
- 次に開く file または確認 command
- 戻り先 skill がある場合はその理由
- interactive UIでは`code complete`、`runtime verified`、`user validated`の到達状況と、残っているHITL review gate

`docs/plan/NNN_PLAN.md` が今回の実装 plan なら、完了時に `docs/plan/NNN_PLAN_DONE.md` へリネームします。未完了項目が残る場合は、次の plan または handoff に切り出します。

## 注意点

- 実装中に仕様の穴を埋めない。判断が必要なら前段へ戻す。
- phase / slice は自動停止点ではない。blocker、HITL 判断、`REPLAN_REQUIRED` がなければ次へ進む。
- 並列化する場合も、各 worker に slice contract と TDD loop を渡す。未確定の slice を並列化しない。
- PR、review、furikaeri はここで扱わない。必要になった時点で別 skill を起動する。

## 共通リソース

- [planning.md](references/planning.md) — 依存・移行・HITL・保存計画が必要な場合
- [html-plan.md](references/html-plan.md) — 任意の図入り計画HTML
- `references/interactive-app-bootstrap-checklist.md` — interactive app の bootstrap 前提
- `references/interactive-app-comparable-harness-contract.md` — interactive app の比較前提
- `references/safe-refactoring.md` — 振る舞いを維持した小さい改善単位
- `references/eval-checklist.md` — slice gateの詳細観点
- `references/runtime-evidence/` — interactive appで必要時だけ使うevidence template
- `checkpoints/contract_verify.py` — 複数リポ環境での contract 検証
