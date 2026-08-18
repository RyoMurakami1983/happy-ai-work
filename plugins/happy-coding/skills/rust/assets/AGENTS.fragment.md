## Rust working agreement

- edition、MSRV、workspace、feature、target、`rust-toolchain`をbuild contractとして尊重する。
- 回復可能な失敗は`Result`で表し、panicと`unsafe`の範囲を局所化する。
- 不要な公開範囲、clone、allocationを増やさないが、推測で最適化しない。
- 変更後は、このrepoのformat、check、Clippy、test、target buildを実行する。
