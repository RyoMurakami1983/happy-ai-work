---
name: python
description: Pythonリポジトリの環境・依存・lint・型検査・テスト契約を読み、既存ツールを尊重して安全に実装またはセットアップする。Pythonコード、pyproject、スクリプト、テストの変更で使う。
---

# Python

既存repoのpackage manager、lockfile、formatter、linter、type checker、test runnerを先に確認し、greenfield向け既定で上書きしない。

## ワークフロー

1. `pyproject.toml`、lockfile、tool設定、README、CIからPython versionと実行入口を確定する。
2. 既存環境がある場合はその入口を使う。新規構築を依頼された場合だけ[project-setup.md](references/project-setup.md)から最小構成を選ぶ。
3. 型境界、例外処理、I/O分離、path操作を変更内容に合わせて確認する。詳細は[coding-practices.md](references/coding-practices.md)を読む。
4. formatter、lint、type check、focused testをrepoの順序で実行し、必要なら全体testへ広げる。
5. CLIやscriptでは終了コード、標準出力／標準エラー、文字コード、Windows／WSLのpath差を確認する。

repoへ永続的なPython規約を追加する依頼では、[AGENTS.fragment.md](assets/AGENTS.fragment.md)を対象repoに合わせて最寄りの`AGENTS.md`へ統合する。

## 境界

- `uv`、Ruff、pytest等はgreenfieldの有力候補であり、既存Poetry／pip-tools／PDM／mypy等を無断置換しない。
- 型注釈やdocstringを機械的に全コードへ追加せず、公開境界と変更箇所を優先する。
- formatterが扱うstyleをskill本文へ大量に複製しない。
