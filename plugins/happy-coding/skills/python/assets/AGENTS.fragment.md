## Python working agreement

- `pyproject.toml`、lockfile、既存の環境管理・lint・型検査・test runnerを正本として尊重する。
- 公開境界と重要な内部境界には型を付け、外部I/Oと純粋ロジックを分離する。
- 広すぎる例外処理や例外の握りつぶしを避ける。
- 変更後は、このrepoが定義するformat、lint、type check、testを実行する。
