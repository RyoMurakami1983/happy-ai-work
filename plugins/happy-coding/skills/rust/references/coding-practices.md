# Rust coding practices

- library境界では回復可能な失敗を`Result`で表し、panicは不変条件違反や回復不能な状態へ限定する。
- repoの方針に合わせて`thiserror`、`anyhow`等を使い、library errorとapplication contextを混同しない。
- `struct`、`enum`、newtypeでドメイン制約を表し、意味の異なるprimitiveを混ぜない。
- `pub`を必要最小限にし、module境界で不変条件を守る。
- iteratorと明示loopは可読性で選び、複雑なchainを目的化しない。
- clone、allocation、lockingはhot pathかどうかを確認してから最適化する。
- `unsafe` blockには呼び出し側が守る条件、内部で維持する条件、検証方法を残す。
- asyncではruntime、task ownership、cancellation、blocking処理の境界を明確にする。
