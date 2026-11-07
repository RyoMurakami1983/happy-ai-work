---
name: ci-debug
description: GitHub Actionsなどの失敗したCIチェックをログから切り分け、根本原因と最小修正を特定する。PRチェック失敗、workflow失敗、ローカルでは再現しないCI障害を調査するときに使う。
---

# CI Debug

PR・check・workflowのmetadataは利用可能なGitHubコネクタを優先し、Actions job logは`gh`またはGitHubのログ取得機能で読む。PR本文・check名だけで原因を推測しない。

1. repo、PR／branch、失敗check、最新runを特定する。
2. 最初に意味のある失敗を示すjob／stepと、直前の入力・command・環境を記録し、後続の連鎖失敗と分ける。
3. workflow・関連コードを読み、可能なら同じcommandでローカル再現する。証拠からflaky／環境差／依存関係／権限／テスト／設定へ分類する。
4. 根本原因・影響範囲・最小修正・再検証commandを提示する。
5. 修正も依頼範囲の場合だけ変更し、focused checkから必要な広域checkへ進む。

サービス障害・権限不足をコード変更で隠さない。再実行はflakyの証拠がある場合だけ、回数を限定する。
