# 質問定義

案件repoに`.py`ファイルを置き、`QUESTIONNAIRE`へPythonの辞書・リスト・文字列・真偽値だけを代入する。import、関数呼び出し、変数参照は使えない。生成器はファイルを実行せず、リテラルとして読む。

```python
QUESTIONNAIRE = {
    "id": "sample-001",
    "title": "作業手順の確認",
    "intro": "回答をまとめたら、内容を確認して担当者へ渡してください。",
    "sections": [
        {
            "id": "current-work",
            "title": "現在の作業",
            "questions": [
                {
                    "id": "work-example",
                    "type": "long_text",
                    "prompt": "最近の作業を1件、順に教えてください。",
                    "required": True,
                    "hint": "機密情報は書かず、作業の流れを記入してください。",
                },
                {
                    "id": "review-step",
                    "type": "single_choice",
                    "prompt": "結果を誰が確認しますか？",
                    "required": True,
                    "choices": [
                        {"id": "worker", "label": "作業者本人"},
                        {"id": "manager", "label": "管理者"},
                        {"id": "other", "label": "その他"},
                        {"id": "unknown", "label": "分からない"},
                    ],
                    "note": {
                        "label": "その他の場合の担当者",
                        "type": "short_text",
                        "required_if": ["other"],
                    },
                },
            ],
        },
    ],
}
```

`id`は小文字英数字とハイフンを使い、英小文字で始める。フォームIDは回答JSONの`form_id`、質問IDは`answers`のキーになる。同一フォーム内で質問IDを重複させない。表示順の番号をIDにしない。追加質問票には別のフォームIDを付け、同じ意味の質問を再利用するときだけ同じ質問IDを使う。

質問の`type`は`single_choice`、`short_text`、`long_text`。`required`は必ず真偽値で指定する。`single_choice`には2件以上の`choices`を付け、必要なら`note`を付ける。`note.required_if`には、選んだとき補足を必須にする選択肢IDを指定する。推奨案を選択肢に記す場合も、初期選択にはしない。「不明」や「該当なし」が必要かは質問の目的に合わせて決める。

回答JSONは`{"schema_version":1,"form_id":"sample-001","answers":{"work-example":{"value":"..."},"review-step":{"value":"other","note":"..."}}}`の形になる。任意項目も空文字列で出力する。回答を処理するときは、表示順や表示文言ではなくIDと選択肢コードを使う。
