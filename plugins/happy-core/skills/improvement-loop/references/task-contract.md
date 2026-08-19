# 次のタスク契約

## Critical thinking

- 観測事実: 実際に何が起きたか
- 改善仮説: 何を変えると何が改善するか
- 反対仮説: 本当の原因は別にないか
- 最小実験: 最小の変更でどう確かめるか
- 反証条件: どんな結果なら改善案を棄却するか
- 機会費用: 今これを行う価値が他のタスクより高いか

## Notionの最小項目

### Properties

- タスク名
- 状態: 次／作業中／完了／保留／破棄
- 実行日: 未定／日付
- 種別: 通常／改善実験／GitHub Issue
- 今日または次回の完了条件
- 発生元と関連リンク

### 改善実験ledger

改善実験では、別sessionでも同じ基準で結果を回収できるよう、page本文または対応するpropertyへ次を保存する。

- 観測事実
- 改善仮説と反対仮説
- 最小実験と反証条件
- 検証方法
- 結果
- 採用／継続／破棄／保留の判断と理由

「今日」は保存場所ではなく、実行日が今日のタスクを表示するviewとして扱う。「明日のタスク」は、実行日が翌日に確定した「次のタスク」の一部である。

GitHub Issueがある場合、Issue本文をNotionへ複製しない。NotionにはIssueリンク、その実行日に行う一歩、改善実験ledgerだけを置く。

## Lifecycle

```text
candidate -> scheduled -> executing -> evaluated
                                      |-> adopted
                                      |-> continued
                                      |-> rejected
                                      `-> deferred
```

- `scheduled`: NotionやIssueへ登録した状態。改善完了ではない。
- `executing`: 実験または変更を実行中。
- `evaluated`: 完了条件と反証条件で効果を確認した状態。
- `adopted`: 効果を確認して採用。
- `continued`: 追加の観測が必要だが継続価値がある。
- `rejected`: 仮説が反証された、または利益がない。
- `deferred`: 今は実行しない。
