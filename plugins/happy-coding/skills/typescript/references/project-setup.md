# TypeScript project setup

greenfieldではruntime、package manager、module方式、bundler、test環境を先に決める。最小契約は次の通り。

- package managerとversionを宣言する
- lockfileをcommitする
- `tsconfig`は可能なら`strict`から始める
- `typecheck`、`lint`、`test`、`build`をpackage scriptsへ寄せる
- CIではfrozen／immutable相当のinstallを使う

frameworkの公式scaffoldがある場合は、その生成物を起点にする。複数のformatter、test runner、bundlerを理由なく重ねない。

既存repoでは`npm install`等を推測で実行する前にlockfileを読み、対応するpackage managerを選ぶ。依存追加はproduction／developmentの別とbundle影響を確認する。
