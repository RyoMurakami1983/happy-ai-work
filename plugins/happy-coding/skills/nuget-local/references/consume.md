# Consume local package

1. repo-local feedまたは一時的なuser feedを選び、共有configへ個人absolute pathを残さない。
2. package source mappingや明示sourceを使い、同名packageがpublic feedから選ばれないようにする。
3. SDK-styleでは`dotnet add ... package ... --version ...`、legacyでは既存のPackage Manager／`packages.config`手順を優先する。
4. restoreとbuildを別々に実行し、選択されたsource、version、transitive dependencyを確認する。
5. Debug／Releaseや必要なtarget frameworkでtestまたは代表起動を行う。

失敗時は次を分離する。

- source登録／mapping
- version mismatch／cache
- target framework compatibility
- missing transitive dependency
- legacy `HintPath`、props／targets import
- runtime load／native dependency

必要なら一意なversionへ上げる。cache削除だけでversioning問題を隠さない。
