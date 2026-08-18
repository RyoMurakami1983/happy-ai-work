# TypeScript coding practices

- exportする関数、型、公開APIは境界が読める型シグネチャにする。
- 外部JSON、環境変数、network、storage、URL parameterはruntimeで検証し、型assertionだけで安全とみなさない。
- `any`より`unknown`とnarrowingを使い、`@ts-ignore`／`@ts-expect-error`には局所的な理由を持たせる。
- 状態はbooleanの組合せより判別可能union等で不正状態を表現しにくくする。
- `const`／`readonly`を使いつつ、既存frameworkのstate modelに反する全面immutable化はしない。
- promise rejectionとcancel／timeoutを観測可能にし、fire-and-forgetを無所有にしない。
- ESM／CJS、server／client、build-time／runtimeの境界を明示する。
- テストは内部関数の形より利用者が観測する振る舞いを主語にする。
