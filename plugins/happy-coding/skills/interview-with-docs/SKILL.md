---
name: interview-with-docs

description: >
  interview-me と domain-modeling を組み合わせ、文書や既存repoを根拠に目的・制約・例外・成功条件を掘り下げ、用語と境界を整理する。
  要件を明確化したい、grill me形式で質問してほしい、または文書を基に仕様を固めたいときに使う。

---

この skill は `happy-core` の `interview-me` と `happy-coding` の `domain-modeling` を順に使う薄いオーケストレーションです。会話、指定された文書、既存repoを根拠に、実装や執筆へ渡せる合意を作ります。

## 実行ルール

1. 指定された文書とrepo内の関連資料を先に読む。外部ページが指定された場合は、利用可能なコネクタまたはブラウザで原文を確認する。
2. `interview-me` の手順で、既に決まっている事項、矛盾、実装を左右する未知を分け、重要な意思決定を深掘りする。
3. `domain-modeling` の手順で、合意した用語、定義、境界、例外を整理する。repoの `CONTEXT.md` は必ず作成または更新する。
4. 回答のたびに決定ログを更新し、同じ質問を繰り返さない。
5. 実装を左右する未知がなくなったら、合意事項、用語、未確定事項、次工程へのhandoffを返す。

## 成果物（saved-by-default）

結果を後続PRDへ根拠・未決事項・重要判断として引き継げる場合、grill結果の単独保存は不要です。それ以外は `docs/grill_results/NNN_GRILL_WITH_DOCS_RESULT.md` へ保存します。`NNN` は同案件のPRD / design / planと共有します。

conversation-only は利用者が明示的に文書不要とした場合、またはsmall one-sliceで後続の判断記録が不要な場合だけ許容し、handoffに `exception reason:` を記載します。複数repo、複数slice、public contract、migration / operationsを伴う場合は選べません。

文書にない内容を事実として補わない。推定は推定と明示する。質問が不要なほど要求が明確なら、grillを長引かせずhandoffを作る。

## 迷ったときの判断

- ゴールや判断軸が曖昧なら `interview-me` に戻る。
- 用語や境界が曖昧なら `domain-modeling` に戻る。
- 実装判断に影響しない好みは、推奨を示して保留可能にする。
- 要求をPRDとして合意・保存するなら `to-prd`、構造判断が必要なら `technical-design` へ渡す。
