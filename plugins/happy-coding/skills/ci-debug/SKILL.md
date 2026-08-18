---
name: ci-debug
description: GitHub Actionsなどの失敗したCIチェックをログから切り分け、根本原因と最小修正を特定する。PRチェック失敗、workflow失敗、ローカルでは再現しないCI障害を調査するときに使う。
---

# CI Debug

## 方針

- PR・check・workflow metadataは利用可能なGitHubコネクタを優先する。
- GitHub Actionsのjob logは `gh` またはGitHubのログ取得機能で確認する。PR本文やcheck名だけから原因を推測しない。
- 最初に失敗した意味のあるstepを特定し、後続の連鎖失敗と分ける。
- flaky、環境差、依存関係、権限、テスト失敗、設定不備を証拠に基づいて分類する。

## ワークフロー

1. 対象repo、PRまたはbranch、失敗check、最新runを特定する。
2. 失敗jobとstepのlogを読み、エラー直前の入力・command・環境を記録する。
3. workflowと関連コードを確認し、可能なら同じcommandをローカルで再現する。
4. 根本原因、影響範囲、最小修正、再検証commandを提示する。
5. 修正が依頼範囲に含まれる場合だけ変更し、focused checkを先に、必要なら広いcheckを後に実行する。

外部サービス障害や権限不足の場合はコード変更で隠さない。再実行はflakyの証拠がある場合に限り、無制限に繰り返さない。
