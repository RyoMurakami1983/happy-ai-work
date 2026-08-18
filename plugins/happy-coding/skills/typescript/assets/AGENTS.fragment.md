## TypeScript working agreement

- lockfile、`packageManager`、package scripts、`tsconfig`、既存lint／test設定を実行契約として尊重する。
- `any`を安易に使わず、外部入力は`unknown`から実行時検証して絞り込む。
- 公開APIとexportする関数には意図が分かる型境界を置く。
- 変更後は、このrepoのtype check、lint、test、buildを実行する。
