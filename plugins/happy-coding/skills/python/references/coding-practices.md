# Python coding practices

- 公開関数と重要な内部境界には型ヒントを付け、複雑な戻り値を曖昧にしない。
- 外部入力、I/O、時刻、環境変数と純粋ロジックを分離する。
- `except:`や握りつぶしを避け、回復できる境界で具体的な例外を扱う。
- 可変デフォルト引数を使わず、必要なら`None`から初期化する。
- path操作は特別な理由がなければ`pathlib`を検討する。
- 長寿命applicationでは`print`より既存logging方針を使う。短いCLIの標準出力契約は例外とする。
- `dataclass`、Enum、Protocol、TypedDict等は、データ境界を明確にするときに使い、型のための型を増やさない。
- import時副作用を避け、実行入口は必要に応じて`if __name__ == "__main__":`で分離する。
