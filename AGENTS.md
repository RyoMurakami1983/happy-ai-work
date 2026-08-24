# AGENTS.md

## このrepoの役割

`happy-ai-work` は、仕事・学習・ライティング・コーディングを継続的に改善する Codex 用 skills、plugins、workspace template の母艦です。

## Source of truth

- 利用者向け入口: `README.md`
- 公式upstreamの判断原則と統治境界: `CONSTITUTION.md`
- 日常のConstitution参照: `docs/CONSTITUTION_SUMMARY.md`
- 製品・用語・境界: `CONTEXT.md`
- 配布物: `plugins/happy-core/`、`plugins/happy-coding/`
- marketplace: `.agents/plugins/marketplace.json`
- 品質契約: `scripts/validate_repo.py` と `.github/workflows/`

## 基本コマンド

```powershell
uv run --script scripts/validate_quality.py
```

この入口をPython version、tool version、実行順の正本とし、一時uv環境からrepo validator、unit test、lint、type check、`git diff --check`を実行します。対象repoへdependencyやlockfileを追加しません。

## Boundaries

- 通常改善、Constitution amendment、governance driftは`CONSTITUTION.md`と日常summaryに従って区別する。安全、評価整合性、人間の所有権、修復可能性を利便性で緩和しない。
- Copilot固有のagentファイルや`copilot-authoring`は移植しない。skill作成・更新は公式`skill-creator`を使う。
- Copilot由来のskillは意図を保ち、Codexの `AGENTS.md`、skills、plugins、subagentsへ再設計する。
- 固定 `agents/*.agent.md` を増やさない。独立レビューは必要時に動的subagentで行う。
- 公開skillは1つのprimary purposeに絞る。詳細知識は`references/`へ置き、独立した利用目的がないleaf skillを増やさない。
- 未完成案はplugin外の`incubator/`で扱い、`SKILL.md`やmarketplace entryを置かない。
- home設定を無断で変更しない。`home-bootstrap` はdry-run、差分、backup、明示承認を必須とする。
- 日本語を正本とし、英語版を必須にしない。
- 変更範囲に合うfocused checkを先に実行する。
- 恒久的な実行規約を追加するときは、採用済みAcceptance Criteria、decision、既存repo規約、外部contract、安全invariantのいずれかへ根拠を持たせる。検討過程、非採用案、一時的な環境事情は実行規約へ混ぜず、必要な判断理由だけをdesign／ADRへ残す。
