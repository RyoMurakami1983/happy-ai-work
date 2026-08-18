# AGENTS.md

## このrepoの役割

`happy-ai-work` は、仕事・学習・ライティング・コーディングを継続的に改善する Codex 用 skills、plugins、workspace template の母艦です。

## Source of truth

- 利用者向け入口: `README.md`
- 製品・用語・境界: `CONTEXT.md`
- 配布物: `plugins/happy-core/`、`plugins/happy-coding/`
- marketplace: `.agents/plugins/marketplace.json`
- 品質契約: `scripts/validate_repo.py` と `.github/workflows/`

## 基本コマンド

```powershell
python scripts/validate_repo.py
python -m unittest discover -s tests -v
ruff check .
```

PythonがPATHにないWindows環境では、repo内の開発手順に従って `uv run` を使います。

## Boundaries

- Copilot固有のagentファイルや`copilot-authoring`は移植しない。skill作成・更新は公式`skill-creator`を使う。
- Copilot由来のskillは意図を保ち、Codexの `AGENTS.md`、skills、plugins、subagentsへ再設計する。
- 固定 `agents/*.agent.md` を増やさない。独立レビューは必要時に動的subagentで行う。
- 公開skillは1つのprimary purposeに絞る。詳細知識は`references/`へ置き、独立した利用目的がないleaf skillを増やさない。
- 未完成案はplugin外の`incubator/`で扱い、`SKILL.md`やmarketplace entryを置かない。
- home設定を無断で変更しない。`home-bootstrap` はdry-run、差分、backup、明示承認を必須とする。
- 日本語を正本とし、英語版を必須にしない。
- 変更範囲に合うfocused checkを先に実行する。
