---
name: wpf
description: WPFアプリのXAML、binding、resource、MVVM、UI thread、設定保護を既存構成に合わせて実装・診断する。WPF画面、ViewModel、command、validation、デスクトップ設定を扱うときに使う。一般的な.NET変更だけならdotnetを使う。
---

# WPF

XAMLを独立言語として一般化せず、WPFのproperty system、binding、resource、threading、lifetimeの文脈で扱う。

## ワークフロー

1. target framework、WPF SDK、既存MVVM framework、DI、navigation、resource構成、UI test基盤を確認する。
2. ViewとViewModelの責務、binding contract、command、validation、dispatcher境界を固定する。詳細は[xaml-and-mvvm.md](references/xaml-and-mvvm.md)を読む。
3. 画面状態をコードビハインド、ViewModel、service、domainのどこが所有するか決め、同じ状態を重複保持しない。
4. secretや個人情報を含む設定では、保存先・脅威モデル・復旧方法を決めてから[secure-config.md](references/secure-config.md)を読む。
5. build／unit testに加え、変更したbinding、validation、keyboard操作、DPI／theme等の該当UIシナリオを確認する。

## 境界

- WinUI、MAUI、AvaloniaへWPF固有手順をそのまま適用しない。
- 単純なView専用イベントまで機械的にViewModelへ移さない。
- binding errorを無視せず、実行時traceまたはUI testで観測する。
- credentialを独自暗号、source、通常の設定JSONへ保存しない。
