# Rust project setup

新規repoではbinary／library、workspaceの要否、support target、MSRV、feature方針を決めてから`cargo new`／`cargo init`を使う。

標準的な確認候補:

```powershell
cargo fmt --check
cargo check --all-targets
cargo clippy --all-targets --all-features -- -D warnings
cargo test --all-features
```

これは既定例であり、repoがfeature combination、cross target、no-std、platform固有commandを定義している場合はそちらを優先する。libraryでは`Cargo.lock`の運用方針をrepoに合わせる。

依存追加前にfeatureとdefault featureを確認し、不要なruntime、TLS backend、platform依存を引き込まない。
