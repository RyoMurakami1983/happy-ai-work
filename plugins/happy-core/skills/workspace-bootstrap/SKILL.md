---
name: workspace-bootstrap
description: 既存または新規repoへ Codex向け AGENTS.md と最小の品質・文書構成を安全に導入する。workspace初期化、既存repoへのCodex導入、repo template作成時に使う。
---

# Workspace Bootstrap

1. repo rootと適用範囲の`AGENTS.md` chain、`.github/copilot-instructions.md`、対象pathに`applyTo`で適用される`.github/instructions/*.instructions.md`、近接docs、技術stack、build/test command、CI、および適用対象の他skillが提供する`AGENTS.fragment.md`を確認する。存在しないsourceは推測で補わない。
2. `assets/AGENTS.md` を土台に、実在するcommand、責務、優先順位、境界だけを反映した案を作る。既存`AGENTS.md`がある場合は全文置換せず、その構造と管理中の内容を保った差分案にする。
3. Codex review用の`## Code Review Rules`は、repoの実装、CI、事故記録、または既存指示で確認でき、見逃すと重大な誤動作、データ損失、権限／security境界の破れ、または誤った正常終了につながるrepo固有の制約だけを少数追加する。一般的なlint／style／テスト推奨は入れない。
4. Copilot指示がある場合は全文を複製せず、Codexの変更やreviewの判断を実質的に変える高重要度のルールだけを抽出する。`applyTo`付きのルールは対象範囲を根AGENTS.mdへ一般化せず、対応する最寄りの`AGENTS.md`または適用範囲が分かる指示として保つ。既存指示と同義の内容は重複させず、矛盾は優先順位と適用範囲を確認して解消する。
5. 既存ファイルを上書きせず、根拠sourceと差分を提示する。無関係な設定や依存関係を追加しない。
6. ユーザーの承認後、必要なファイルだけを適用する。
7. 指示の読み込み、最小test、リンクを確認してhandoffする。

新規repoでは `.editorconfig`、`.gitignore`、docs、PR／Issue template、CIも候補にできるが、選択したstackに必要なものだけを作る。
