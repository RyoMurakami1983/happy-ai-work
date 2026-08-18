# happy-ai-work

> 仕事・学習・ライティング・コーディングを継続的に改善する Codex 用 skills／plugins／workspace template の母艦。

CodexデスクトップアプリとCodex CLIで再利用するワークフローを、2つのpluginとして管理します。

## Plugins

| plugin | 用途 |
| --- | --- |
| `happy-core` | home／workspace初期化、文章の構成・下書き・推敲 |
| `happy-coding` | インタビュー、PRD、設計、実装、言語／framework支援、デバッグ、評価、レビュー、CI対応 |

## 導入

このrepoをcloneし、repoルートをmarketplaceとして登録します。

```powershell
codex plugin marketplace add .
codex plugin add happy-core@happy-ai-work-marketplace
codex plugin add happy-coding@happy-ai-work-marketplace
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
- `furikaeri`: 作業の事実・学び・摩擦を次の小さな改善へ整理
- `skill-eval`: 既存skillのtriggerと振る舞いをrealistic scenarioで評価

### happy-coding

- 明示オーケストレーション: `$coding`（通常依頼には暗黙発火しない）
- 要求から実装: `interview-with-docs`、`domain-modeling`、`to-prd`、`technical-design`、`implementation-plan`、`implement`
- 言語／ecosystem: `dotnet`、`python`、`typescript`、`rust`、`dotnet-framework-bridge`、`nuget-local`
- framework: `wpf`、`tauri`
- 調査・修正: `repo-onboarding`、`debug-and-fix`
- 品質: `deep-review`、`ci-debug`

`coding`は必要な工程だけを選ぶrouterです。PRD、technical design、implementation planを常に全部作るのではなく、入力artifactとriskに応じて省略します。

旧repoのleaf skillをそのまま並べず、独立した利用目的がない詳細は各skillの`references/`へ統合しています。移植判断は[docs/SKILL-PORTFOLIO.md](docs/SKILL-PORTFOLIO.md)を参照してください。

## 作成途中のworkflow

未完成の案はplugin外の[incubator/](incubator/)で扱います。ここにある候補はインストールされません。旧`pptx`は移植せず、将来のwriting deliverablesを実利用から新規設計します。

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
