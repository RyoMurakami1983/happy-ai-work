# Compatibility options

| 選択肢 | 向く状況 | 主なrisk |
| --- | --- | --- |
| `netstandard2.0` contract | 両側が対応し、共有APIを小さく保てる | 利用API制約、依存packageの非対応 |
| multi-target | 同じsourceをtarget別にcompileできる | conditional codeとtest matrixの増加 |
| adapter／facade | legacy SDKを同一processで隔離できる | runtime load、binding、bitness |
| IPC／別process | runtime、bitness、crash、security境界を分けたい | protocol、deployment、versioning、運用コスト |

共有候補はinterface、DTO、enum、純粋な変換／validationに限定する。WPF／WinForms型、`System.Configuration`の読み取り、vendor SDK呼び出し、DI container、host logging実装は境界の外へ置く。

確認項目:

- 各targetで共有projectがcompileする。
- modern側がlegacy実装を直接参照しない。
- exception、null、serialization、version skewの契約がある。
- runtimeで必要なassembly／native DLL／設定が出力先に揃う。
- x86／x64、STA、COM、driver等のlegacy制約を実環境で確認する。
