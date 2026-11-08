---
name: home-bootstrap
description: Codexホームの AGENTS.md を安全に導入・更新し、CodexのGit指示とHooksの初期設定を案内する。既存設定を残したdry-run、差分確認、バックアップ付き適用やホーム設定の見直しで使う。
---

# Home Bootstrap

`scripts/home_bootstrap.py`は`CODEX_HOME`配下、未設定なら`~/.codex/AGENTS.md`の管理マーカー内のみ追加・更新し、管理外を保つ。

skill／template改善はrepo成果物を更新し、実home適用も依頼された場合だけ実homeへ進む。template検証には一時ファイルを`--target`指定できる。

AGENTS.mdのtemplate更新・実home適用前に、対象pathと変更後の全文（実homeは管理外も含む）を利用者へ提示し、その版への明示確認を得る。差分や作業全体の承認で代替せず、本文を変えたら全文を再提示する。同一変更の再試行では、対象・全文が同じなら承認を聞き直さない。

## 実homeへの適用

1. 管理領域と周辺の個人設定を読む。
2. `python scripts/home_bootstrap.py --dry-run`で差分を確認し、対象pathと管理外を含む変更後の全文を利用者へ示す。
3. その対象・全文への明示適用承認がある場合のみ、確認した差分と同じ引数で`--apply`する。
4. 既存変更時は同じdirectoryへtimestamp付きbackupを作る。
5. 適用後、管理対象と管理外内容の保持を確認する。

適用完了と会話への自動読込は別に確認する。`CODEX_HOME`とoverrideを確認する。[Codexの読込仕様](https://learn.chatgpt.com/docs/agent-configuration/agents-md)では空でない`AGENTS.override.md`が優先されるため、`AGENTS.md`の更新だけで有効になるとは扱わず、overrideを無断変更しない。Workでも同じhomeが読まれるとは推測しない。明示的なファイル読取だけでは自動読込の証拠にしない。

homeには普遍的な作業方針のみ置き、言語・framework・test command等repo固有規則は各repoの`AGENTS.md`へ置く。

## 共通方針

正本は[assets/AGENTS.md](assets/AGENTS.md)。編集前に[短歌と俳句](../tanka-to-haiku/SKILL.md)を読み、意味・判断条件を保って既存の構成と調子へ統合する。「目的を把握する」は会話・repoからの判断、「必要な情報から報告する」は伝達の段階とする。指定の詳しさ・書式・判断条件を短さのために削らない。

実homeでは管理領域と周辺設定、templateのみの改善ではrepo管理領域の意味重複・競合を確認する。管理外個人設定を自動削除せず、競合箇所・影響・融合案を示してから適用する。

## Git設定・Hooks

AGENTS.mdにGit固有指示を追加しない。home初回導入またはGit設定依頼時は[Git設定ガイド](references/git-settings.md)を読み、3入力欄用文面と「準備完了時に自動マージ」ONの手順を示す。共通方針のみの更新では、全文確認後の完了報告を変更結果に絞る。設定画面を確実に自動操作できなければ設定済みと推測せず、手動入力が必要と示す。

Hooks確認・設定依頼時のみ[Hooks初期設定ガイド](references/codex-hooks.md)を読む。未設定は異常でなく、既定は既存inventoryと候補説明まで。候補ごとの影響提示→dry-run→差分確認→明示承認→backup付き適用→Trust確認の順を守る。
