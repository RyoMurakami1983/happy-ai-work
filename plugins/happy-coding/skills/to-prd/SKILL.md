---
name: to-prd
description: 現在の会話と確認済み資料から、利用者、問題、成果、scope、acceptance criteria、制約、未確定事項をPRDへ整理する。追加の技術設計や実装計画を行わず、何をなぜ作るかを合意・保存したいときに使う。
---

# To PRD

会話と確認済み資料に根拠がある内容だけを、要求のsource of truthへ整理する。
PRDは「なぜ・誰の・何を・どこまで」を所有し、「どの構造で・どの順に」は後工程へ渡す。

## 入力ゲート

PRDを書く前に、次が会話または資料に存在するか確認する。

- 誰の、どんな問題を解決するか
- 解決後に得られる成果
- 何ができたら成功か
- 今回扱わない範囲の素材

認証・認可を変更する場合は、actor × action × resource scopeのpolicy matrix、許可・拒否、tenant / organization境界、未定義roleの扱いも確認する。決まっていない項目はblocking Unknownsとして `interview-with-docs` へ戻す。

不足がある場合は、未確定のままPRD化するか、先に `interview-with-docs` で深めるかをユーザーに選んでもらう。追加インタビューをこのskill自身で始めず、勝手に補完しない。

## 根拠の扱い

- 会話や確認済み資料にない機能、user story、判断を発明しない。
- 推論は「推定」と明示する。
- 決まっていないことは本文の決定事項に混ぜず、Unknownsへ置く。
- repoがある場合は、用語、既存機能、制約、ADRに接地する。アクセスできなければ「コードベース未確認」と記す。
- 会話で既に決まった技術事項は「Fixed Constraints」として記録できるが、新しいmodule、interface、schema、API方式をここで設計しない。

## ワークフロー

1. 問題、利用者、期待するoutcomeを短く固定する。
2. In Scope / Out of Scopeを分ける。
3. 会話に出たuser storyまたはjobを、利用者価値に接続して整理する。
4. Acceptance Criteriaを外部から観測可能で、合格/不合格を判断できる形にする。
5. 既決のbusiness / product / compliance / technical constraintsを記録する。
6. Unknowns、前提、依存、コードベース確認状況を列挙する。
7. 根拠とscopeを再確認し、次工程へhandoffする。

## 生成テンプレート

```markdown
# PRD: [Name]

## Problem
## Users
## Desired Outcomes
## In Scope
## Out of Scope
## User Stories / Jobs
## Acceptance Criteria
## Fixed Constraints
## Dependencies
## Unknowns
## Source Notes
```

保存する場合は同じ案件の `NNN` を使って `docs/prd/NNN_PRD.md` とする。`NNN` は同案件のgrill / design / planと共有し、既存番号がなければrepo内の最大番号+1を使う。

次工程へのhandoffには必ず次のいずれかを含める。保存済み成果物が1つでもある場合は、会話で補った内容だけであっても既知のpathをすべて列挙する。

```yaml
artifacts:
  - docs/prd/NNN_PRD.md
```

保存しない場合だけ `artifacts: conversation-only` とする。

## 出荷ゲート

- すべての要求が会話または資料に接地している。
- Acceptance Criteriaが内部実装ではなく観測可能な振る舞いになっている。
- Out of Scopeが空ではない。
- 未確定事項がUnknownsに隔離されている。
- 新しいarchitecture、test seam、vertical slice、file pathをPRDで決めていない。

## 次工程

- 構造判断が必要なら `technical-design`。
- 構造が既に固定され、複数sliceの順序だけ必要なら `implementation-plan`。
- 単一の明確な変更なら `implement` へ直接渡してよい。
- Unknownsが実装をブロックする間は自動着手させない。

## 注意点

- セクションを埋めるための水増しをしない。
- 追加のインタビューをしない。
- PRDをtechnical designやtask checklistの代わりにしない。
