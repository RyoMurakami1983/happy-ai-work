---
name: interview-with-docs

description: 文書や既存repoを根拠に要件をインタビューし、用語と境界を整理する。資料を基に仕様を固めたいときに使う。

---

この skill は、利用可能なら `happy-core` の `interview-me` を使い、`happy-coding` の `domain-modeling` へつなぐ薄いオーケストレーションです。会話、指定された文書、既存repoを根拠に、実装や執筆へ渡せる合意を作ります。

## 実行ルール

1. 指定された文書とrepo内の関連資料を先に読む。外部ページが指定された場合は、利用可能なコネクタまたはブラウザで原文を確認する。
2. `interview-me` が利用可能ならその手順を使う。利用できなければこの場で、既に決まっている事項、矛盾、実装を左右する未知を分け、判断に必要な質問だけを行う。skillの導入を前提や待ち条件にしない。
3. `domain-modeling` の用語整理（Vocabulary pass）で、合意した用語・定義・意味の境界を整理する。repoの `CONTEXT.md` は必ず作成または更新する。業務ルールや例外の候補・未決事項は合意記録に残し、モデル境界、不変条件、状態遷移が設計を左右するときだけモデル化（Formal modeling）へ渡す。未合意の目的・要件は確定入力にせず、`to-prd`で整理する。
4. 回答のたびに決定ログを更新し、同じ質問を繰り返さない。
5. 実装を左右する未知がなくなったら、合意事項、用語、未確定事項、次工程へのhandoffを返す。

3件以上の質問をまとめて尋ねる場合は、質問内容をこのskillで決めてから `html-questionnaire` へ渡す。利用者が会話での回答を指定した場合は、その希望に従う。1〜2件の追加確認は会話で続けられる。HTML生成を要件合意の完了とみなさない。

## 成果物（saved-by-default）

結果を後続PRDへ根拠・未決事項・重要判断として引き継げる場合、grill結果の単独保存は不要です。それ以外は `docs/grill_results/NNN_GRILL_WITH_DOCS_RESULT.md` へ保存します。`NNN` は同案件のPRD / design / planと共有します。

conversation-only の可否と保存必須条件は、[共通成果物契約](../implement/references/WORK_ARTIFACTS.md#conversation-only-exceptions)に従う。例外を選ぶ場合は `artifacts: conversation-only` と具体的な `exception reason:` をhandoffに記載する。

文書にない内容を事実として補わない。推定は推定と明示する。質問が不要なほど要求が明確なら、grillを長引かせずhandoffを作る。

## 迷ったときの判断

- ゴールや判断軸が曖昧なら、上記のインタビューへ戻る。
- 用語や境界が曖昧なら `domain-modeling` に戻る。
- 実装判断に影響しない好みは、推奨を示して保留可能にする。
- 要求をPRDとして合意・保存するなら `to-prd`、構造判断が必要なら `technical-design` へ渡す。
