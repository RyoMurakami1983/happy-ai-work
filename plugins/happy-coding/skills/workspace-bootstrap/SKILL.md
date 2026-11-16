---
name: workspace-bootstrap
description: 既存または新規repoへ Codex向け AGENTS.md と最小の品質・文書構成を安全に導入する。workspace初期化、既存repoへのCodex導入、repo template作成時に使う。
---

# Workspace Bootstrap

1. root・適用directoryのinstruction chainを`AGENTS.override.md`→`AGENTS.md`→設定済み`project_doc_fallback_filenames`で解決する。`.github/copilot-instructions.md`、対象pathへ`applyTo`が適用される`.github/instructions/*.instructions.md`、近接docs、stack、build/test、CI、他の適用skillの`AGENTS.fragment.md`も確認し、不在sourceを推測で補わない。
2. `assets/AGENTS.md`を土台に、実在command・責務・優先順位・境界のみの差分案を作る。有効な既存指示の構造・管理内容を保ち、全文置換しない。同directoryでoverrideが有効なら隠れるAGENTSを新設提案しない。fallbackが有効なら新AGENTSのshadow影響とfallback制約を保つ統合差分を示す。override廃止／通常AGENTS移行／fallback移行は別変更として明示承認を得る。
3. `## Code Review Rules`は、採用済みAcceptance Criteria・decision・repo規約・外部contract・安全invariantを根拠に、重大誤動作・data損失・権限／security破れ・誤正常終了を防ぐrepo固有制約だけ少数追加する。実装・CI・事故記録は必要性とscopeの証拠とし、一時workaround・検討過程・非採用挙動を恒久化しない。一般lint／style／test推奨は入れない。
4. Copilot指示は全文複製せず、Codexの変更／review判断を変える高重要度ルールのみ抽出する。`applyTo`の範囲をrootへ一般化せず、最寄りAGENTSまたはscope明示指示で保つ。同義を重複させず、矛盾は優先順位・scopeを確認して解消する。
5. 既存を上書きせず、根拠sourceと差分を提示し、無関係な設定・依存を追加しない。
6. 承認後に必要fileだけ適用する。
7. 指示読込・最小test・リンクを確認してhandoffする。

新規repoでは`.editorconfig`・`.gitignore`・docs・PR／Issue template・CIも候補にできるが、選択stackに必要なものだけ作る。
