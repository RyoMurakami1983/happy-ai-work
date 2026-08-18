# C# implementation practices

- Nullable reference typesを前提にし、`!`は不変条件を説明できる場合だけ使う。
- 公開契約と失敗可能性を型で表し、処理できない例外を握りつぶさない。
- 非同期I/Oでは`async`／`await`を使い、同期ブロックを混ぜない。既存規約に従い`Async`接尾辞を付ける。
- `IDisposable`／`IAsyncDisposable`の所有者を明確にし、`using`／`await using`で寿命を閉じる。
- `var`、LINQ、record、struct、classは可読性と意味で選び、流行だけで既存コードを置換しない。
- DI、Options、Configuration、Loggingはrepoのcomposition rootと既存パターンに合わせる。
- テストは内部実装ではなく公開境界の振る舞いを検証し、既存のxUnit／NUnit／MSTest等を尊重する。
