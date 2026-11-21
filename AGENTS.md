# AGENTS.md

## このrepoの役割

`happy-ai-work` は、仕事・学習・ライティング・コーディングを継続的に改善する Codex 用 skills、plugins、workspace template の母艦です。

## スキルが目指す方向

Happy AI Work のスキルは、利用者が任せた範囲で、追加の返答を一度も待たずに目的を達成し、結果を検証して届けられる確率を最大化する。相談なら判断材料の提示、実装なら合意した動作の確認までを、その依頼の完了として扱う。

- 確認したくなったら、まず依頼・資料・対象の現状から判断できるか調べる。取得済みの許可は引き継ぎ、戻せる細部は自分で決める。手段が失敗しても、目的と権限の範囲で別の安全な方法を試す。
- スキルの確認手順には、何が起きると確認が必要なのかを書く。例えば保存先に既存ファイルがあり、利用者が別名を許可していれば、空いている別名で新規作成し、読み戻して保存先を伝える。
- 既存データを上書き・削除する前に、対象と失われる内容を示し、利用者の明示確認を得る。法律違反の具体的な懸念があれば該当操作を保留し、事実と権限を確認する。違法と分かっている行為には、適法な代替手段を示す。確認待ちの間も独立して進められる作業を済ませる。
- 自律完了を改善するときは、GPT-6.2 Sol の複数の実行役に実際のスキルを使わせ、監視役が停止箇所・理由と成果物を確認する。安全に完結できる課題での追加返答なしの完了率と、危険な操作の前に正しく確認できたかを別々に記録する。

## Source of truth

- 自律完了の研究進捗・実験結果・次の予定: Notion「Main Page → バイブR＆D → [スキルが不要な停止をせずにゴールまで達成する方法とは](https://app.notion.com/p/41db5a4cd69481b380a1f9aee274bf94)」
- 利用者向け入口: `README.md`
- 公式upstreamの判断原則と統治境界: `CONSTITUTION.md`
- 日常のConstitution参照: `docs/CONSTITUTION_SUMMARY.md`
- 製品・用語・境界: `CONTEXT.md`
- 配布物: `plugins/happy-core/`、`plugins/happy-coding/`、任意の`plugins/happy-improvement/`、試用用`plugins/happy-preview/`
- marketplace: `.agents/plugins/marketplace.json`
- 品質契約: `scripts/validate_repo.py` と `.github/workflows/`

## 基本コマンド

```powershell
uv run --script scripts/validate_quality.py
```

各検証の実行順・バージョンの正本はこのスクリプトとする。対象repoにdependencyやlockfileを追加しない。

## Boundaries

- 通常改善、Constitution amendment、governance driftは`CONSTITUTION.md`と日常summaryに従って区別する。安全、評価整合性、人間の所有権、修復可能性を利便性で緩和しない。
- Copilot固有のagentファイルや`copilot-authoring`は移植しない。skill作成・更新は公式`skill-creator`を使う。
- Copilot由来のskillは意図を保ち、Codexの `AGENTS.md`、skills、plugins、subagentsへ再設計する。
- 固定 `agents/*.agent.md` を増やさない。独立レビューは必要時に動的subagentで行う。
- 公開skillは1つのprimary purposeに絞る。詳細知識は`references/`へ置き、独立した利用目的がないleaf skillを増やさない。
- 構想段階の未完成案はplugin外の`incubator/`で扱い、`SKILL.md`やmarketplace entryを置かない。基本検証を通った試用skillは`happy-preview`で任意配布し、通常配布への昇格は`docs/adr/0004-preview-plugin-distribution.md`に従う。
- home設定を無断で変更しない。`home-bootstrap` はdry-run、差分、backup、明示承認を必須とする。
- 日本語を正本とし、英語版を必須にしない。
- 変更範囲に合うfocused checkを先に実行する。
- 検証は合意した対象・影響・権限の範囲で自動進行し、個々のtestで許可を聞き直さない。所有者の社内利用向け性能基準と適用範囲は[採用記録](docs/design/021_PR_DELIVERY_PROMOTION.md)を参照する。
- 恒久的な実行規約を追加するときは、採用済みAcceptance Criteria、decision、既存repo規約、外部contract、安全invariantのいずれかへ根拠を持たせる。検討過程、非採用案、一時的な環境事情は実行規約へ混ぜず、必要な判断理由だけをdesign／ADRへ残す。
