# WSL2早期対応チェックリスト

初期対応の完了条件は次のとおりです。

- WSL2上でrepoをcloneできる
- repoルートをCodex marketplaceとして登録できる
- `happy-core` と `happy-coding` をインストールできる
- 主要skillsが検出される
- `python scripts/validate_repo.py` が成功する
- `python -m unittest discover -s tests -v` が成功する

Windows側とWSL側ではhomeディレクトリとplugin導入先が異なるため、同じ `AGENTS.md` が自動共有されるとは仮定しません。
