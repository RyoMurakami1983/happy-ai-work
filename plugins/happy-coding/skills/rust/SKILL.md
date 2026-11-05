---
name: rust
description: Rust／Cargoリポジトリのworkspace、toolchain、feature、format、Clippy、test契約を読み、所有権・エラー・unsafe境界を保って実装またはセットアップする。RustコードやCargo設定の変更で使う。
---

# Rust

既存edition・MSRV・workspace・feature・target・lint方針を読み、最新既定で上書きしない。

1. `Cargo.toml`・`Cargo.lock`・workspace・`rust-toolchain*`・`.cargo/config.toml`・CIからbuild contractを読む。
2. library／binary・公開API・feature・target・MSRVの影響を整理し、新規時は[project-setup.md](references/project-setup.md)を読む。
3. [coding-practices.md](references/coding-practices.md)で変更に関係する所有権・error type・panic・unsafe・公開範囲を確認する。
4. focused test後、format、check、Clippy、test、必要なtarget buildをrepo所定の順序・契約に従って実行する。platform依存・FFI・async runtime・featureの影響する組合せを明示・検証する。

永続規約の追加依頼時は[AGENTS.fragment.md](assets/AGENTS.fragment.md)をrepoに合わせ、最寄りの`AGENTS.md`へ統合する。

Tauriのfrontend連携・capability・bundle・sidecarは`tauri`へ渡す。cloneは機械削除せず所有権・可読性・実測コストで判断する。`unsafe`は安全前提・検証範囲を隠さず局所化する。
