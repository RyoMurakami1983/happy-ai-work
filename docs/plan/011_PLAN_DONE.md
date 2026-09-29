# Plan 011：技術実現性調査スキルの初版

2026-09-30 / [PRD](../prd/011_PRD.md) / [設計](../design/011_TECHNICAL_DESIGN.md)

「OKです。作成進めてください。GPT6用として」に基づき、合意した提案を実装・ローカル検証する。新たな業務判断はないため、途中の形式的な承認待ちは設けない。コミット・公開・home導入は対象外。

- [x] Slice 1：調査票を安全に新規作成する。最初のCLI試験でスクリプト未存在のREDを確認し、作成成功と上書き拒否を実装する。空欄・改行・I/Oエラーも公開CLIで確認する。
- [x] Slice 2：本文・判断例とtechnical-designへの任意連携を作る。文章のTDDは装わず、quick_validateとrepo validatorで形式・リンクを確認する。
- [x] Slice 3：固定した架空ケースをGPT-6 Astraの独立生成と別の採点担当で評価する。失敗時は現recordを保存し、修正後は別runへ進む。
- [x] Slice 4：基本検証後にプレビュー一覧・説明を更新する。全体品質チェックと独立差分レビューを通し、実利用未検証の範囲を報告する。

focused command：`uv run --no-project --python 3.14 python -m unittest discover -s tests -p test_technical_feasibility_research.py -v`

形式検証：公式skill-creatorの`quick_validate.py`。全体検証：`uv run --script scripts/validate_quality.py`。

スクリプト不具合・不整合は局所修正。必須条件や役割を変える必要があればPRD・設計へ戻す。実利用の効果確認は試用段階で継続する。

## 完了記録

2026-09-30、上記のローカル作成・検証を完了。

- CLI：最初の実行でスクリプト未存在のRED、その後は新規作成・既存データ保護・不正入力・ディレクトリ出力の3テストがPASS。
- 形式：公式skill-creatorの`quick_validate.py`とrepo validatorがPASS。
- 振る舞い：GPT-6 Astra（high）、5件を各1回実行し、別担当が固定基準で採点。Critical 20/20、通常5/5、禁止行為・重大な誤適用0。[公開評価記録](../../evals/records/technical-feasibility-research-preview-001.json)に条件・hash・限界を保存。
- 独立実装レビュー：`/root/research_implementation_review`が本文・補助CLI・テスト・設計を確認し、高信頼の不具合指摘なし。評価基準・模擬回答を渡さず実施。
- 全体：`uv run --script scripts/validate_quality.py`がPASS（repo validator、93 tests、Ruff、ty、`git diff --check`）。初回に既存の評価suite一覧テストが新suiteの未登録で失敗したため、一覧へ追加して再実行した。

模擬評価は共通home Yohaku指示も含み、ケースは2つの生成contextへ分けて実行した。Yohakuのソースは実行後に保存したため、実行前のbyte同一性は別途確認していない。スキル単体の優位性、未見hold-out、実際の自動起動、実案件の調査・配布成功、全GPT-6モデルでの再現性は確認していない。

利用者の次の判断に必要な成果物は、スキル本文・判断例・調査票・CLIと、technical-designへの任意連携。home導入・公開は今回の完了条件に含まれない。

## PR検証での補修

PR #43のCIで、Gitへの初回登録時の改行変換による評価hash不一致と、英語Windows環境で日本語の出力先を表示する際のUnicodeEncodeErrorを検出した。前者は評価時のbytesを保持する属性と再登録で復元し、index内の全artifact hash一致を確認。後者はCLIの標準出力・標準エラーをUTF-8へ統一し、cp1252の入出力環境を固定したCLIテストで失敗を再現して修正した。

凍結したv1評価資源とrecordは保持する。模擬評価は修正前CLIを含むsnapshotを対象としており、今回のCLI修正の根拠は回帰テストとCI。スキル本文・判断例・雛形は同一で、模擬回答の再生成は行わない。
