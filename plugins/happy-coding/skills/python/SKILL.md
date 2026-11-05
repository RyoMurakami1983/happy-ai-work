---
name: python
description: Pythonリポジトリの環境・依存・lint・型検査・テスト契約を読み、既存ツールを尊重して安全に実装またはセットアップする。Pythonコード、pyproject、スクリプト、テストの変更で使う。
---

# Python

既存repoのpackage manager・lockfile・formatter・linter・type checker・test runnerを尊重し、greenfield既定で上書きしない。

1. `pyproject.toml`、lockfile、tool設定、README、CIからPython versionと実行入口を確定し、既存入口を使う。Windows sandboxでPython／uv起動やcache pathが失敗したら[windows-sandbox-and-uv.md](references/windows-sandbox-and-uv.md)で一度のpreflightから入口変更を判断する。新規構築の依頼時だけ[project-setup.md](references/project-setup.md)で最小構成を選ぶ。
2. [coding-practices.md](references/coding-practices.md)を読み、変更に関係する型境界・例外処理・I/O分離・path操作を確認する。
3. formatter、lint、type check、focused testはrepo所定の順序を優先して実行し、必要なら全体testへ広げる。CLI／scriptは終了コード・stdout／stderr・文字コード・Windows／WSLのpath差も確認する。

常用GUIの頻繁な入力確認・保存ごとに重いPython全体を起動・終了しない。EXE化・非同期化だけでは起動費用は消えない。設計時に頻度とprocess寿命を確認し、常駐再利用や軽い処理の分離を検討する。[coding-practices.md](references/coding-practices.md)のGUI項目に従い、実配布物の初回起動と継続操作を別々に測る。単発CLI・EXE・one-file自体は禁止しない。

永続的な規約追加の依頼時は[AGENTS.fragment.md](assets/AGENTS.fragment.md)をrepoに合わせ、最寄りの`AGENTS.md`へ統合する。

`uv`・Ruff・pytestはgreenfieldの候補であり、Poetry／pip-tools／PDM／mypy等を無断置換しない。型注釈・docstringは公開境界と変更箇所を優先し、全コードへ機械追加しない。formatterのstyleを本文へ大量複製しない。
