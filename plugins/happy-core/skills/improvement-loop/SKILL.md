---
name: improvement-loop
description: furikaeriなどで選択済みの改善候補を、批判的に検討できる改善実験と次のタスクへ変え、Notion、GitHub Issue、skill改善などへ委譲し、採用・継続・破棄まで結果を回収する。単なる振り返り、通常タスク管理、直ちに実装するだけの依頼には使わない。
---

# Improvement Loop

選択済みの改善候補を、反証可能な小さい実験として閉じる。目的は改善数を増やすことではなく、効果を確認できる一件を完了させること。

## 入力境界

- `furikaeri`などから、「その改善を進める」「登録する」「指定日に実行する」とユーザーが合意した改善候補を受け取る。候補提示だけを選択済みと見なさず、未選択候補をすべて登録しない。
- 通常の未完了作業はNotionの「次のタスク」へ戻し、このskillでは扱わない。
- 同時に進める改善実験は原則1件とする。

## ワークフロー

1. security、秘密情報、既知の失敗回数、必要権限、変更範囲をpreflightする。停止条件に該当する場合は、外部writeやdispatchより前にすべて停止する。
2. 既存の`scheduled`または`executing`改善実験を再開する場合は、Notionの実験ledgerを読み、元の仮説と反証条件を復元する。新しい候補として重複登録しない。
3. [次のタスク契約](references/task-contract.md)に沿って、観測事実、改善仮説、反対仮説、最小実験、反証条件、完了条件、実行日候補を整理する。
4. 何もしない選択肢、別の原因、機会費用を比較し、今進める価値がなければ保留または破棄する。
5. 一度だけの軽い摩擦は、原因確認の改善実験として具体化できるが、skill変更には進めない。
6. 日付指定がなければ「次のタスク」とし、次の作業日を候補として提示する。「明日」と勝手に確定しない。
7. Notionを実行タスクと実験ledgerの正本とする。GitHub Issueが必要なら、Issueを技術課題の正本にし、NotionにはIssueリンク、今回の一歩、改善仮説、反証条件、検証結果、判断を置く。Issue本文は複製しない。
8. 外部書き込み前に、タスク、実行日、完了条件、登録先、公開範囲、送信内容を一度にpreviewし、候補ごとにユーザーの確認を得る。
9. 利用可能な専門skillへ一段だけ委譲する。再帰的に`furikaeri`や`improvement-loop`を呼ばない。
10. 実行後は検証結果をledgerへ戻し、`adopted`、`continued`、`rejected`、`deferred`のいずれかで閉じる。登録済み、実行済み、効果確認済みを区別する。

## Dispatch

| 改善対象 | 委譲先 |
| --- | --- |
| 対象repoを問わず、対象とAcceptance Criteriaが明確な実装backlog | `github-issue` |
| Happy AI Work利用中の軽い違和感・未成熟なfeedback | `happy-add-issue` |
| skillの作成・更新 | 公式`skill-creator` |
| skillのtrigger・workflow・成果物のbehavior評価 | `skill-eval` |
| skill構造とfrontmatter | 公式skill validator |
| plugin新設、manifest、marketplaceなど配布境界 | 公式`plugin-creator` |
| repo全体の整合 | repo固有validatorとtest |

専門skill、Notion、GitHubが利用できなければ、実行可能なdraftと次の手順を返す。利用できない機能を実行済みと報告しない。

## skill変更ゲート

通常のskill変更は、同じ問題の再発が2回以上あり、再現scenario、期待動作、評価方法が書ける場合に始める。一度だけの軽い違和感は「次のタスク」またはfeedback候補に留める。

観測済みまたは再現済みの秘密漏洩、破壊操作、誤った外部公開、skillが利用不能になる重大障害は即時対応の例外とする。危険な依頼を一度受けただけでは、重大障害が発生したと推定しない。

tokenやcredentialが入力に含まれる場合は値を反復せず、外部送信を止める。実際に露出した可能性があれば、対象serviceでのrevoke／rotationと影響範囲確認をユーザーへ案内するが、自動実行しない。

skill変更では編集前にbaselineを固定し、同じscenarioでcurrentを比較する。重要な変更は[評価シナリオ](references/eval-scenarios.md)に沿って`skill-eval`へ委譲する。

## 停止条件

- 1回の実行で修正iterationは最大2回。
- 同じ失敗が2回続く、必要権限がない、評価不能、変更範囲が拡大する場合は停止する。
- 再開条件と次回確認時点が具体的なら`continued`、それらが決まらない、または今進める価値がないなら`deferred`とする。
- 停止時は、完了した状態、未確認の効果、残存risk、次のタスクを分けて返す。
