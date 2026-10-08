---
name: implementation-plan
description: 合意済みの要求とtechnical designを、依存順、vertical slices、HITL/AFK、検証command、戻り条件を持つ実装計画へ変える。複数工程は図入りHTMLでも読みやすく示す。新しいarchitectureを決めず、安全な実装順序を作りたいときに使う。
---

# Implementation Plan

合意済みの要求と構造判断から、`implement`が迷わず実行できる順序とslice contractを作る。
このskillは実行順を所有し、新しいarchitecture判断は行わない。

## 入力ゲート

次を確認する。

- ゴール、成功条件、対象外
- acceptance criteriaまたはbehavior list
- 既存repoのbuild / test / launch command
- 構造判断が必要な変更では、`technical-design`のhandoffまたは同等の決定
- design handoffに`finalized_contract`がある場合は、採用済みのnormative source、exclusions、unknowns、主要target trace
- 保存済みartifactのpath

要求が不足していれば `interview-with-docs` または `to-prd`、構造判断が不足していれば `technical-design` へ戻す。[短縮条件](references/vertical-slice.md)を満たす単一の明確な変更なら、重いplanを作らず短いimplementation handoffだけでよい。省略理由と実装許可の確認・引き継ぎは省略しない。

## 資料の形式

局所変更は従来の短いMarkdown handoffでよい。複数sliceの依存、HITL境界、外部の開始条件を読者が判断する案件では、Markdown正本に図入りオフラインHTMLを併用する。利用者の形式指定とrepo規約を優先し、図は判断に役立つものを選ぶ。HTMLを使う場合は[html-plan.md](references/html-plan.md)を読む。形式を理由にslice数、architecture、日程、実装許可を増やさない。

## ワークフロー

### 1. Behaviorと依存を整理する

- acceptance criteriaを外部から観測可能なbehaviorへ対応付ける。
- `finalized_contract`がある場合は、各sliceと追加する主要な恒久targetを少なくとも一つのnormative sourceへ対応付ける。非採用案やNon-goalの詳細をplanへ再展開しない。
- schema、contract、migration、consumer / provider等の実依存だけを列挙する。
- 依存しない作業と、順序を守る必要がある作業を分ける。

### 2. Vertical sliceへ分ける

[垂直スライスの定義](references/vertical-slice.md)を読み、一つのまとまった観測可能な振る舞いを単位にする。正常・境界・失敗時など複数の受け入れ条件を同じsliceに含めてよい。最初のsliceは必要な層を薄く縦断するtracer bulletを優先する。

各sliceに含めるもの:

- done条件と対象外
- HITL / AFK
- interactive UIをHITLにする場合は、利用者が直接触れられるreviewable milestone、launch方法、代表操作、期待結果、再開条件
- 使用するpublic interface / test surface
- first testまたはdocs/config変更のverification
- RED command
- REDの期待失敗理由
- GREEN command
- acceptance command
- 検証の目的・規模、合成入力/実環境の区分、所要時間の見込みと根拠（不明なら不明）、timeout/試行budget。全件suite内の長い試験も識別し、[実行前通知](../implement/references/verification-communication.md)へ引き継ぐ。既存の実行許可と追加判断が必要な操作を区別する
- 前提と依存slice

HITLは、主観的な操作感、実端末、外部appとの互換性など、自動化だけではacceptanceを確定できない境界に置く。interactive UIだからという理由だけですべてのsliceを停止点にせず、自動runtime evidenceで十分なsliceはAFKのまま進める。

DBだけ、UIだけ、testだけを先に広げるhorizontal sliceは避ける。

### 3. 実行順と戻り条件を決める

- 価値を早く観測でき、riskを早く潰せる順にする。
- 未確定のsliceを並列化しない。
- `FAIL`は同じsliceの実装修正へ戻す。
- `REPLAN_REQUIRED`はこのplan、または構造問題なら `technical-design` へ戻す。
- 要求の問題なら `interview-with-docs` または `to-prd` へ戻す。

### 4. Handoffを作る

対象範囲と実装開始の許可を区別し、許可の状態・根拠となる利用者発言、省略工程と理由があれば引き継ぐ。計画の承認だけを実装開始の承認とみなさず、取得済みの同じ許可は聞き直さない。

```markdown
## Implementation Handoff

### Goal / Success Criteria / Out of Scope
### Design Artifacts
### Finalized Contract / Target Trace（design handoffにある場合だけ）
### Behavior List
### Dependencies
### Vertical Slices

| Slice | HITL/AFK | Depends on | Done | Test Surface | First Test | RED Command | RED Expectation | GREEN Command | Acceptance Command | Slice Out of Scope |
|---|---|---|---|---|---|---|---|---|---|---|

### HITL Review Contracts（必要なsliceのみ）

- Reviewable milestone: 利用者が何を直接操作できる状態か
- Launch: 利用者が同じbuildを起動する方法
- Review actions: 代表操作と確認する状態遷移
- Expected observations: 利用者の予測と一致すべき結果
- Resume condition: feedback、承認、または再計画のどれで再開するか

### Artifacts

artifacts:
  - docs/plan/NNN_PLAN.md

### Risks / Unknowns
### Return Conditions
```

上はplanだけを保存した例である。保存済みPRD / design等が実在する場合だけ、そのpathも追加する。

HTMLは正本を読む入口とし、要約・依存図・開始条件から根拠となる正本見出しへ辿れるようにする。実装許可、未確定事項、予定commandと検証実績を正本と同じ状態で示す。HTML併用時も正本の保存先を維持する。

成果物は保存を既定（saved-by-default）とし、[NNN_PLAN_TEMPLATE.md](assets/NNN_PLAN_TEMPLATE.md)を使って `docs/plan/NNN_PLAN.md` へ必ず保存する。保存済み成果物の実在するpathをすべて列挙する。finalized contractのnormative sourceまたは主要targetの根拠が不明なら、実行順で補わず`technical-design`へ戻す。

conversation-only は利用者が明示的に文書不要とした場合、またはsmall one-sliceで後続の判断記録が不要な場合だけ許容し、`exception reason:` を併記する。複数repo、複数slice、public contract、migration / operationsを伴う場合は選べない。成果物の番号とpathは[WORK_ARTIFACTS.md](references/WORK_ARTIFACTS.md)に従う。

## 注意点

- 設計案を作り直さない。構造判断が必要なら `technical-design` へ戻す。
- 実装を始めない。
- planを詳細な作業日記にしない。
- PR作成やreview実行そのものを実装sliceへ混ぜない。人間の判断が必要なruntime review contractはHITL境界として計画し、外部操作は上位workflowへ渡す。

## 関連リソース

- [WORK_ARTIFACTS.md](references/WORK_ARTIFACTS.md) — artifactのpath、番号、handoff規約
- [NNN_PLAN_TEMPLATE.md](assets/NNN_PLAN_TEMPLATE.md) — 保存するplanのテンプレート
- [html-plan.md](references/html-plan.md) — 図入りHTMLの読み順、保存・同期、生成と確認
