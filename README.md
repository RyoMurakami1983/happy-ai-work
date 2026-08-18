# happy-ai-work

> 仕事・学習・ライティング・コーディングを継続的に改善する Codex 用 skills／plugins／workspace template の母艦。

CodexデスクトップアプリとCodex CLIで再利用するワークフローを、2つのpluginとして管理します。

## Plugins

| plugin | 用途 |
| --- | --- |
| `happy-core` | home／workspace初期化、文章の構成・下書き・推敲 |
| `happy-coding` | インタビュー、PRD、設計、実装、評価、レビュー、CIデバッグ |

## 導入

このrepoをcloneし、repoルートをmarketplaceとして登録します。

```powershell
codex plugin marketplace add .
codex plugin install happy-core@happy-ai-work-marketplace
codex plugin install happy-coding@happy-ai-work-marketplace
```

Codexアプリではplugin画面から `Happy AI Work` を開き、必要なpluginを導入します。

## 主要skills

### happy-core

- `interview-me`: 重要な意思決定を具体例・反例まで質問で深掘り
- `home-bootstrap`: `~/.codex/AGENTS.md` の管理対象部分を安全に導入・更新
- `workspace-bootstrap`: repo用 `AGENTS.md` と最小基盤を対話的に準備
- `writing-plan`: 読者と目的から文章構成を設計
- `draft-writing`: 合意済み構成から日本語初稿を作成
- `deep-edit`: 主張・構成・論理・読みやすさ・正確性の順に推敲

### happy-coding

- `interview-with-docs`
- `domain-modeling`
- `to-prd`
- `design-and-plan`
- `implement`
- `implementation-eval-gate`
- `deep-review`
- `ci-debug`

## home用AGENTS.md

Codex全体へ適用する指示は、通常 `~/.codex/AGENTS.md` に置きます。Windowsでは `%USERPROFILE%\.codex\AGENTS.md` です。

`home-bootstrap` は既存内容を全置換せず、管理対象マーカー内だけを更新します。最初に必ずdry-runします。

```powershell
python plugins/happy-core/skills/home-bootstrap/scripts/home_bootstrap.py --dry-run
```

## 開発

```powershell
python scripts/validate_repo.py
python -m unittest discover -s tests -v
ruff check .
```

WSL2の確認範囲は [docs/WSL2.md](docs/WSL2.md) を参照してください。

## ライセンス

MIT License
