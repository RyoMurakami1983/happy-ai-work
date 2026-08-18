---
name: dotnet-framework-bridge
description: .NET Framework 4.xのlegacy実装を残しながらモダン.NETへ段階移行する境界を設計・検証する。共有contract、netstandard、multi-target、adapter、別processのどれで橋渡しするか判断するときに使う。
---

# .NET Framework bridge

`netstandard2.0`を常に正解とせず、legacy依存、consumer target、runtime load、配布単位を調べて最小の移行境界を選ぶ。

## ワークフロー

1. Framework固有API、vendor SDK、UI型、configuration、native dependency、process bitnessを棚卸しする。
2. 双方が共有すべきものをcontract、DTO、enum、純粋なvalidationへ限定する。
3. [compatibility-options.md](references/compatibility-options.md)を使い、`netstandard2.0`、multi-target、adapter、IPCの候補を比較する。
4. 参照方向を一方通行にし、legacy実装型をmodern UI／application層へ漏らさない。
5. configurationとI/Oはhost側で読み、共有境界には値または明示的なinterfaceを渡す。
6. 両targetのcompile／testに加え、実行時load、設定、native DLL、bitness、installerを代表環境で確認する。

## 境界

- 完全書き換えや大規模process分割は`design-and-plan`へ渡す。
- WPFの画面構造は`wpf`、一般的なSDK／project診断は`dotnet`を使う。
- 共有層を便利な共通libraryへ肥大化させない。
- direct DLL referenceを恒久的なarchitectureとして曖昧に残さない。
