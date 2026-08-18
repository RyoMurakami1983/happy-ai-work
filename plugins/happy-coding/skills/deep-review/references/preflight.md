# Review preflight

今回の変更に当てはまる項目だけを使う。

## 一次情報と正本

- Issue、要件、公式reference、repo instructionsを確認したか。
- 編集対象は正本か。mirror、template、generated fileを誤って直接直していないか。
- docs、comment、設定、実装の約束が一致しているか。

## 非破壊性

- update／replaceの境界は既存手書きdataを保持するか。
- empty、missing marker、legacy data、partial failureを扱うか。
- dry-run、warning、exit code、rollbackの説明と実装が一致するか。

## 配布と回帰

- 変更がどのplugin、template、runtime、利用者へ届くか説明できるか。
- 新しい分岐や失敗経路に検証手段があるか。
- focused testと必要な全体gateを実行したか。

## Reviewer先読み

- 今回の修正が次に壊しうる境界を1〜3個挙げたか。
- guardやinvariantは最小の所有境界にあり、重複していないか。
- 例外やエラーは利用者が次の行動を選べる情報を含むか。
