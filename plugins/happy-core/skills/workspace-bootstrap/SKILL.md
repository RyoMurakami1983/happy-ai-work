---
name: workspace-bootstrap
description: 既存または新規repoへ Codex向け AGENTS.md と最小の品質・文書構成を安全に導入する。workspace初期化、既存repoへのCodex導入、repo template作成時に使う。
---

# Workspace Bootstrap

1. repo root、既存 `AGENTS.md`、技術stack、build/test command、CI、文書構成を確認する。
2. `assets/AGENTS.md` を土台に、実在するcommandと境界だけを反映した案を作る。
3. 既存ファイルを上書きせず、差分を提示する。無関係な設定や依存関係を追加しない。
4. ユーザーの承認後、必要なファイルだけを適用する。
5. 指示の読み込み、最小test、リンクを確認してhandoffする。

新規repoでは `.editorconfig`、`.gitignore`、docs、PR／Issue template、CIも候補にできるが、選択したstackに必要なものだけを作る。
