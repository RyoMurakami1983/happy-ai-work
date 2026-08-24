# Repo quality validation

## 目的

repoの品質検証を、ローカル環境へdependencyやlockfileを追加せず、WindowsとUbuntuで同じ入口から再現可能に実行する。

## 実行

```powershell
uv run --script scripts/validate_quality.py
```

Python version、一時dependency、tool version、実行順の正本は`scripts/validate_quality.py`とする。この入口は次を実行する。

- repo validator
- unit test
- Ruff
- ty
- `git diff --check`

既存のuv cacheだけを使用する場合は`--offline`を付ける。検証が失敗した場合やworktreeを変更した場合は成功として扱わない。
