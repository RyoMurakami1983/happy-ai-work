# Python project setup

新規repoでは、対象runtime、配布形態、library／applicationの別を先に決める。特別な制約がなければ、単一の`pyproject.toml`、lockfile、local virtual environment、formatter／linter、test runnerを揃える。

候補例:

```powershell
uv init .
uv add --dev ruff pytest
uv sync
uv run ruff check .
uv run pytest
```

型検査は対象Python version、framework plugin、チーム経験に合わせて選ぶ。ツール名より、ローカルとCIが同じ設定・lockfile・commandを使うことを優先する。

既存repoではREADME、task runner、CIのcommandを正本とし、`python`直実行と環境管理ツール経由を混在させない。
