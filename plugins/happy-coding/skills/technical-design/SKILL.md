---
name: technical-design
description: 合意済みの目的・要件から、module責務、public interface、data flow、security boundary、trade-offを決め、根拠・変更シナリオ・契約を追える設計を作る。構造判断とレビューへ渡す設計資料の作成・更新に使う。独立レビューの判定、実装計画、実装は扱わない。
---

# Technical Design

要求の「何を実現するか」を、実装可能な「どの構造で実現するか」へ変換する。
このskillは構造判断とレビューに必要な根拠の準備を所有する。目的・要件はPRDまたは同等の合意記録を参照し、業務上のモデル・不変条件は `domain-modeling`、実装順序やvertical sliceの進捗計画は `implementation-plan` へ渡す。

## 入力ゲート

次を確認する。

- PRDまたは同等の合意記録にある文脈、目的、要件、成功条件、対象外
- 要件に対応する、外部から観測できるacceptance criteria
- 関連するrepo instructions、既存コード、test、ADR、`CONTEXT.md`
- 存在する場合はdomain model artifact、業務ルール、不変条件、操作前後の条件、requirement gaps
- 会話で既に固定された技術制約

不足は影響する要件・設計箇所、blockingか、戻り先を示す。業務事実や根拠の調査は `interview-with-docs`、目的・要件・scope・ACの確定は `to-prd`、用語・モデル境界・業務上の契約の整理は `domain-modeling` へ戻す。正式なPRDやdomain model文書の作成自体を全案件の前提にしない。

blockingなrequirement gapが残る部分は確定設計として渡さない。影響を受けない部分の設計や草案の保存は進められるが、未知を設計判断で補完しない。

## 設計ルート

通常は既存stackと単一repoを前提に、必要最小限の構造判断を行う。

次に該当する場合だけ[balanced-coupling.md](references/balanced-coupling.md)を読む。

- 複数repo、別team、別deployが関係する
- shared library、SDK、generated client、shared databaseを扱う
- service split、context分割、分散モノリス化が論点になる

大きな技術選定が必要な場合だけ[TECH_SELECTION_HARNESS.md](references/TECH_SELECTION_HARNESS.md)を読む。既存stackで自然に実装できる場合は省略する。

## ワークフロー

### 0. Normative inputsを固定する

- 設計の根拠にする合意済み目的・要件・AC、既存規約、外部contract、domain invariantと固定済み技術制約を、出典のpath / 節または会話上の合意へ結び付ける。
- 既存IDと合意状態を保持する。現行コードの挙動、推定、設計案、Unknownsを規範入力と区別し、コードにある制限をそのまま製品要件へ昇格しない。
- 設計中に入力が変わったら、影響するtrace・contract・構造判断を見直す。

### 1. 現在の構造を接地する

- 実際のentry pointと主要な実行経路を追う。
- 現在の責務、public interface、state、I/O、所有境界を確認する。
- 現行構造の具体的な弊害を、発生条件とコード・test等の証拠へ結び付ける。未観測のriskや未確認のコードを観測済み扱いにしない。
- 新規抽象化より既存の境界を優先する。

### 2. 構造判断を固定する

- どのmodule / componentが、どの目的・要件を実現する責務を持つか
- 使用・変更・追加するpublic interface
- 状態、data flow、依存方向
- 触らない境界
- 認証、認可、外部入力、機密情報、file / network / command等のtrust boundary
- 移行、互換性、rollbackが必要か

目的・要件 → 必要ならモデル上の責任・不変条件 → module / interface / 設計判断 → ACと観測境界のtraceを残す。対象要件の実現漏れと、根拠のない構造追加を両方向から確認する。小変更では一文でよく、複数要件・境界では対応表やIDで追えるようにする。

境界や抽象化の判断には、根拠のあるchange scenario（何が・なぜ変わるか）とexpected locality（変更する箇所・影響を閉じる範囲）を添える。無関係な目的への波及、同時変更・互換性への影響、改善費用も確認する。仮説は仮説と明記し、将来要件にしない。追加する抽象化は、内部複雑性を隠し、変更を局所化できる場合だけ採用する。変更理由の材料がなければその旨を記し、シナリオを水増ししない。

変更する公開操作では、domain invariantの適用範囲と保証責任を確認し、事前条件、成功時の事後条件、失敗時の状態・副作用・エラーの返し方を技術contractへ落とす。正常例・境界例・拒否例をACに対応付ける。業務上の条件を新設せず、保証手段は設計判断として区別する。

複数要件・境界の設計や明示的なレビュー引き継ぎでは、[review-ready-design.md](references/review-ready-design.md)の記載項目と例を使う。単純CRUDや局所変更に、モデル分割や全項目の記入を強制しない。

### 3. 選択肢とtrade-offを記録する

重大な判断だけ、採用案、却下案、理由、既知riskを残す。long-lived structure、compatibility、migration、operationsに影響する判断は、repoの規約に従ってADRを必ず作る。

複数案を実質的に比較した、途中で採用決定が変わった、または案固有の制約がAGENTS.md、SKILL.md、reference、実装、test等の恒久成果物へ入り得る場合は、handoff前に[finalization contract](references/finalization-contract.md)を読む。単純な局所変更や比較案のない設計へ重いcontractを強制しない。

### 4. 実装可能性を確認する

- acceptance criteriaをpublic interfaceまたは観測可能な境界で検証できるか
- 不変条件と操作前後・失敗時の条件を、担当境界で保証・観測できるか
- change scenarioで想定した局所性と実際の依存方向に矛盾がないか
- 対象技術で自然に実装できるか
- dependency、schema、contractの変更順に破綻がないか
- 未解決事項が実装をブロックしないか

順序の詳細やfirst testはここで作らず、`implementation-plan`へ渡す。

### 5. Review readinessを整理する

設計の対象版、規範入力、trace、contract、変更シナリオ、既知の仮定、blocking Unknowns、riskの高い判断と確認してほしい点を渡す。レビューの要否と理由を記録し、要否は利用者の依頼・repo規約に従い、境界・互換性・安全性・業務条件への影響から判断する。

ここでのreadinessは証拠が揃っているかを示すもので、独立レビューのPASSや実装承認ではない。必要な独立レビューは、利用可能なら `technical-design-review`、なければ独立レビュアーへ同じ資料を渡す。skillの存在を前提にした呼出しや新設は行わない。blockingな不足や必要なレビューが未完了なら、その理由と次の担当を示し、実装へ進める完成設計とは扱わない。

## 出力

成果物は保存を既定（saved-by-default）とし、`docs/design/NNN_TECHNICAL_DESIGN.md` へ必ず保存する。`NNN` は同案件のPRD / grill / planと共有し、既存番号がなければrepo内の最大番号+1を使う。repoの `CONTEXT.md` がなければ作成し、案件で確定した用語・境界があれば更新する。

```markdown
# Technical Design NNN: [Name]

## Goal / Success Criteria / Out of Scope
## Normative Inputs
## Purpose / Requirement Trace
## Current Structure and Observed Harms
## Change Scenarios / Expected Locality
## Structure Decisions
## Public Interfaces
## Domain Invariants / Interface Contracts
## State / Data Flow
## Security Boundaries
## Compatibility / Migration
## Alternatives and Trade-offs
## Risks / Unknowns
## ADRs
## Review Readiness / Handoff
## Artifacts
```

見出しは規模に応じて統合・省略してよい。根拠から設計・検証への対応、適用するcontract、未決事項とレビュー要否は、短い設計でも追えるようにする。domain model文書がない場合はその列を省き、必要な業務条件を合意記録へ直接結び付ける。

handoffには、設計artifact、実装で守る採用済み構造判断、未決定事項、次の戻り先を含め、実在する既知のpathをすべて列挙する。finalization contractが必要な案件では、採用済みの規範sourceと主要targetへのtraceを渡し、非採用案の詳細はdesign／ADRへの参照に留める。AGENTS.md、SKILL.md、reference等のinstructionを更新する場合は、その配置が議論を知らない読者にも必要な理由をtarget traceへ一行で書く。exclusionは`rejected`／`non-goal`／`superseded`を区別し、`rejected`と`non-goal`は別途negative requirementとして採用されない限り恒久禁止ではないとhandoffで明示する。conversation-only は利用者が明示的に文書不要とした場合、またはsmall one-sliceで後続の判断記録が不要な場合だけ許容し、`exception reason:` を併記する。複数repo、複数slice、public contract、migration / operationsを伴う場合は選べない。

```yaml
artifacts:
  - docs/design/NNN_TECHNICAL_DESIGN.md
```

上はdesignだけを保存した例である。保存済みPRD等が実在する場合だけ、そのpathも追加する。

## 注意点

- 仕様の穴を設計で埋めない。
- vertical slice、HITL/AFK、RED/GREEN commandをここで計画しない。
- 実装を始めない。
- 小さな既存構造内変更へ重い設計書を強制しない。

## 関連リソース

- [DDD_GLOSSARY.md](references/DDD_GLOSSARY.md) — DDD用語が判断に必要な場合
- [IMPLEMENTATION_HEURISTICS.md](references/IMPLEMENTATION_HEURISTICS.md) — subdomainから実装形を考える場合
- [TECH_SELECTION_HARNESS.md](references/TECH_SELECTION_HARNESS.md) — 大きな技術選定が必要な場合
- [balanced-coupling.md](references/balanced-coupling.md) — multi-repo / ownership境界の場合
- [review-ready-design.md](references/review-ready-design.md) — trace、変更シナリオ、操作のcontract、レビュー引き継ぎを詳しく記載する場合
- [finalization-contract.md](references/finalization-contract.md) — 複数案や決定変更から恒久成果物へ採用contractだけを渡す場合
