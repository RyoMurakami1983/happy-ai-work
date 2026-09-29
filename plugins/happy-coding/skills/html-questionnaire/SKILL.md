---
name: html-questionnaire
description: 回答をJSONで受け取れるオフラインHTML質問票を作る。質問内容が決まり、フォームでまとめて渡したいときに使う。
---

# HTML質問票

回答者へ渡す質問内容が決まったら、案件のPython定義から単一のHTMLファイルを生成する。質問の発見や要件の合意はこのskillの仕事ではない。1〜2件の追加確認を会話で行う場合はフォームを作らない。

1. 質問文、選択肢、必須条件、補足欄を案件側の定義へ記す。[定義形式](references/definition.md)を使い、同じ質問のIDと選択肢コードを後続版でも保つ。変更された質問には新しいIDを使う。
2. 利用先repoのPython実行入口を使い、`<python> <skill>/scripts/render_questionnaire.py path/to/questions.py path/to/questions.html`の形で実行する。入力・出力は案件repoのパスを使う。生成器はPythonリテラルのみ受け付け、定義ファイルのコードを実行しない。
3. 出力HTMLをローカルで開き、必須・条件付き補足、回答プレビュー、コピーまたは手動コピー、JSONダウンロードを確認する。回答JSONの`form_id`と質問IDが定義に対応することを確かめる。

共通の`assets/`と`scripts/`には案件名、業務データ、回答を入れない。出力HTMLと回答JSONの保存場所は案件repoの規則に従う。生成HTMLは外部送信しないが、回答者によるコピー・添付とファイル保管の扱いは案件ごとに説明する。
