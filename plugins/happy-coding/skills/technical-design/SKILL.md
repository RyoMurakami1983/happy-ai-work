---
name: technical-design
description: 合意済みの要求から、module責務、public interface、data flow、security boundary、trade-offを決める。実装順序や進捗計画ではなく、変更を成立させる構造判断とtechnical designが必要なときに使う。
---

# Technical Design

要求の「何を実現するか」を、実装可能な「どの構造で実現するか」へ変換する。
このskillは構造判断を所有し、実装順序やvertical sliceの進捗計画は `implementation-plan` へ渡す。

## 入力ゲート

次を確認する。

- ゴール、成功条件、対象外
- 外部から観測できるacceptance criteria
- 関連するrepo instructions、既存コード、test、ADR、`CONTEXT.md`
- 会話で既に固定された技術制約

要求を左右する未知が残る場合は `interview-with-docs` へ戻す。PRDが必要な案件で利用者・scope・acceptance criteriaが未確定なら `to-prd` へ戻す。

## 設計ルート

通常は既存stackと単一repoを前提に、必要最小限の構造判断を行う。

次に該当する場合だけ[balanced-coupling.md](references/balanced-coupling.md)を読む。

- 複数repo、別team、別deployが関係する
- shared library、SDK、generated client、shared databaseを扱う
- service split、context分割、分散モノリス化が論点になる

大きな技術選定が必要な場合だけ[TECH_SELECTION_HARNESS.md](references/TECH_SELECTION_HARNESS.md)を読む。既存stackで自然に実装できる場合は省略する。

## ワークフロー

### 1. 現在の構造を接地する

- 実際のentry pointと主要な実行経路を追う。
- 現在の責務、public interface、state、I/O、所有境界を確認する。
- 新規抽象化より既存の境界を優先する。

### 2. 構造判断を固定する

- どのmodule / componentが責務を持つか
- 使用・変更・追加するpublic interface
- 状態とdata flow
- 触らない境界
- 認証、認可、外部入力、機密情報、file / network / command等のtrust boundary
- 移行、互換性、rollbackが必要か

追加する抽象化は、内部複雑性を隠し、変更を局所化できる場合だけ採用する。

### 3. 選択肢とtrade-offを記録する

重大な判断だけ、採用案、却下案、理由、既知riskを残す。長期的な判断であればrepoの規約に従ってADRを作る。

### 4. 実装可能性を確認する

- acceptance criteriaをpublic interfaceまたは観測可能な境界で検証できるか
- 対象技術で自然に実装できるか
- dependency、schema、contractの変更順に破綻がないか
- 未解決事項が実装をブロックしないか

順序の詳細やfirst testはここで作らず、`implementation-plan`へ渡す。

## 出力

会話だけで十分なら `artifacts: conversation-only` とする。設計判断を後で参照する価値がある場合、またはユーザーが保存を求めた場合は `docs/design/NNN_TECHNICAL_DESIGN.md` へ保存する。`NNN` は同案件のPRD / grill / planと共有し、既存番号がなければrepo内の最大番号+1を使う。

```markdown
# Technical Design NNN: [Name]

## Goal / Success Criteria / Out of Scope
## Current Structure
## Structure Decisions
## Public Interfaces
## State / Data Flow
## Security Boundaries
## Compatibility / Migration
## Alternatives and Trade-offs
## Risks / Unknowns
## ADRs
## Artifacts
```

handoffには、設計artifact、実装で守る構造判断、未決定事項、次の戻り先を含める。保存済み成果物がある場合は既知のpathをすべて列挙し、保存しない場合だけconversation-onlyとする。

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
