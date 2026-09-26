# ADR 0006：過去評価の対象実体をsnapshotで保持する

2026-09-27 / 採用 / Issue #35

## 背景

既存recordの `artifact_hashes` は評価時のskill pathを参照している。validatorが常に現行treeへ照合するため、skillを改善すると旧recordが不一致になる。一方、旧recordのhashを更新することは過去評価の改変となる。

## 決定

`evals/history/<record-id>.json` に、変更しない旧recordのSHA-256と、元artifact pathから `evals/` 内の `snapshots/` 保存実体への対応を追加する。旧recordをまずhashで固定し、その元の期待hashでsnapshotを照合する。対応のないartifact・新recordは現行実体の照合を維持する。

履歴対応表とsnapshotはrecordと同様append-onlyとする。未知record、未知artifact、対応表の形式不正、record／snapshotの改変、repo外のsnapshotは検証を失敗させる。旧manifestとrecord間の整合検証も維持する。

対応表を作るときは、そのrecordが参照する変更可能な実装・指示をまとめて保存する。今回変更するものだけを保存すると、残った指示を後日変更する際に、immutableな対応表へ追加できなくなるためである。既に固定されているcase・schema・manifest等は元の実体を保持する。

## 理由と代替案

過去recordを書き換える方法は評価整合性に反する。Git履歴に期待hashが存在するだけで現行recordを通す方法は、現行評価の古いhashを見逃す。明示的な対応表なら、どのrecordだけが過去実体を参照するかをレビューでき、Git履歴を取得できない環境でも検証できる。

これは評価基準の緩和ではなく、当時の対象をそのまま検証する保存方式の補完である。過去の成功を現行版の成功へ転用しない。保存量と対応表が増える費用は、実際に旧証拠の保存が必要なartifactだけへ限定する。

## 検証

`tests/test_eval_history.py` で、現行skill変更後の旧証拠の照合、snapshot／record改変拒否、path境界、未知artifact、現行recordの不一致拒否、append-onlyを確認する。
