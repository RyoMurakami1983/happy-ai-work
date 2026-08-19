---
name: github-issue
description: 現在作業しているGitHub repoの追跡価値がある具体的な実装backlogを、重複を避け、観測可能なAcceptance Criteriaを持つIssueとして作成または具体化する。軽い利用feedback、PR対応、一般的なGitHub調査には使わない。
---

# GitHub Issue

現在のrepoで継続追跡すべき作業を、次の担当者が実行できるIssueにする。単なるTODOやその場限りの感想をすべてIssue化しない。

## ワークフロー

1. 投稿先repoと、現在の作業scope外または継続追跡が必要な理由を確認する。
2. 既存Issueを読み取り専用で検索し、重複なら新規作成ではなく既存Issueへの接続案を示す。
3. 公開repoなら、private repo名、顧客名、内部URL、秘密情報、特定可能な業務dataを除外または匿名化する。
4. タイトル、背景、問題、提案または期待結果、Acceptance Criteria、必要な証拠、Non-goalsを必要な範囲だけ整える。
5. repoに実在するlabelだけを候補にする。labelやassigneeを推測で新設しない。
6. 作成前に、正確なrepo、公開範囲、title、body、labelをpreviewし、ユーザーの確認を得る。
7. 利用可能なGitHub connectorを優先し、必要なら`gh`を使う。どちらも使えなければ投稿可能なdraftを返す。
8. 作成後はIssue URLと、Notionの次のタスクへ置く一歩を返す。

## 境界

- Happy AI Work repo内でも、対象とAcceptance Criteriaが明確な実装backlogはこのskillを使う。
- Happy AI Workの利用中に生じた軽い違和感や未成熟なfeedbackは、作業repoにかかわらず`happy-add-issue`へ渡す。
- PR review comment、CI失敗、PR作成はそれぞれの専門workflowへ渡す。
- Issue作成は技術課題の記録であり、Notionの今日／次の実行タスクを置き換えない。
