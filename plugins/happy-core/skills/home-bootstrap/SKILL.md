---
name: home-bootstrap
description: Codexホームの AGENTS.md を安全に導入・更新し、CodexのGit指示とHooksの初期設定を案内する。既存設定を残したdry-run、差分確認、バックアップ付き適用やホーム設定の見直しで使う。
---

# Home Bootstrap

`scripts/home_bootstrap.py` は、`CODEX_HOME` があればその配下、なければ `~/.codex/AGENTS.md` を対象にする。管理対象マーカー内だけを追加・更新し、既存の他セクションは変更しない。

1. まず `python scripts/home_bootstrap.py --dry-run` を実行して対象pathとdiffを示す。
2. ユーザーが適用を明示した場合だけ `--apply` を実行する。
3. 既存ファイルを変更するときは、同じディレクトリへtimestamp付きbackupを作る。
4. 適用後に管理対象セクションと既存内容が保持されていることを確認する。

home指示には普遍的な作業方針だけを置く。言語・framework・test commandなどrepo固有の規則は各repoの `AGENTS.md` に置く。

## Git設定

AGENTS.mdへGit固有の指示を追加しない。AGENTS.mdのdry-run結果を示した後、またはユーザーがGit設定を求めたときは、[Git設定ガイド](references/git-settings.md)を読み、3つの入力欄へ貼り付ける文面と「準備完了時に自動マージ」をONにする手順を必ず表示する。

Codexアプリ自身の設定画面を確実に自動操作できない場合、設定済みと推測せず手動入力が必要だと明記する。

## Hooks

Hooksの確認または設定を求められたときは、[Hooks初期設定ガイド](references/codex-hooks.md)を読む。未設定は異常ではない。既定ではhookを書き込まず、既存設定のinventoryと候補の説明まで行う。設定変更は候補ごとに影響を示し、dry-run、差分確認、ユーザーの明示承認、backup付き適用、Trust確認の順に進める。
