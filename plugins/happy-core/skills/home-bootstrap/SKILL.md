---
name: home-bootstrap
description: Codexホームの AGENTS.md に Happy AI Work の共通作業方針を安全に導入・更新する。既存設定を残したままdry-run、差分確認、バックアップ付き適用を行いたいときに使う。
---

# Home Bootstrap

`scripts/home_bootstrap.py` は、`CODEX_HOME` があればその配下、なければ `~/.codex/AGENTS.md` を対象にする。管理対象マーカー内だけを追加・更新し、既存の他セクションは変更しない。

1. まず `python scripts/home_bootstrap.py --dry-run` を実行して対象pathとdiffを示す。
2. ユーザーが適用を明示した場合だけ `--apply` を実行する。
3. 既存ファイルを変更するときは、同じディレクトリへtimestamp付きbackupを作る。
4. 適用後に管理対象セクションと既存内容が保持されていることを確認する。

home指示には普遍的な作業方針だけを置く。言語・framework・test commandなどrepo固有の規則は各repoの `AGENTS.md` に置く。
