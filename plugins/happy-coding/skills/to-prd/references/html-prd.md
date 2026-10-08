# オフラインHTMLによるPRD

目的・要件・受入条件の対応と、今回の範囲・未確定事項を読者が確認するための表示を作る。Markdown正本を要求のsource of truthとして保ち、HTMLを読む入口として併用する。

## 読み順と表現

文脈・問題・利用者 → 目的と対象範囲 → 目的→要件→ACの対応 → 合意状態・制約・依存・Unknowns → 根拠と正本の詳細の順を基本に、案件に合わせる。[prd.html](../assets/prd.html)は要点カード、目次、図拡大、表の横スクロール、詳細折畳みを持つ。状態は文字でも示す。

| 読者が判断したいこと | 表現 | 保つ内容 |
| --- | --- | --- |
| 誰のどの問題を、どこまで解決するか | 要点カード、In / Out of Scope | 観察と合意の根拠 |
| なぜこの要件が必要で、何を見て受け入れるか | P→R→AC対応表、必要なら対応図 | 既存ID、観測可能な期待結果 |
| 利用者が何をするか | 根拠がある利用者の流れの図 | 未合意の画面・操作を追加しない |
| 何が確定し、何が次工程を止めるか | 合意状態、Unknownsと影響の表 | blocking状態と確認先、推定・候補の表示 |

図は任意で、目的の階層や図数を固定しない。architecture、module、DB、API方式、実装順の新規設計は後工程へ渡す。図や要約が成立しても要求確定や実装許可の証拠にはならない。

## 保存と同期

```text
docs/prd/
  NNN_PRD.md                 # 正本。従来の保存先を維持
  NNN_presentation.json      # 要約・図説明・正本見出しへの対応
  NNN_prd/
    NNN_PRD.html             # 派生する読解用資料
    diagrams/                # 必要な図と編集元
    validation.json          # 入力版・hash・静的確認
    verification.md          # 内容・表示確認の結果（記録する場合）
```

NNNは同案件の設計・計画と共有する。既存正本をHTML化だけで移動しない。別配置の指定があれば従い、生成入力、リンク、handoffを実在pathへ合わせる。

要点・図・節に`source_refs`を持たせ、正本見出しへ辿れるようにする。正本を変更したらP→R→AC、In / Out of Scope、合意状態、Unknowns、根拠を要約・図と照合して再生成する。hash一致は鮮度の証拠で、意味の一致は別に確認する。

編集可能なSVG自体を表示する場合は`single-source`、別の編集元から描いたSVGなら`reviewed-pair`を使える。後者ではノード・矢印・説明を編集元と照合し、片方だけの更新を残さない。

## 生成器

正本の雛形は[NNN_PRD_TEMPLATE.md](../assets/NNN_PRD_TEMPLATE.md)。`scripts/render_prd.py`はPython 3標準ライブラリだけでHTMLと静的検証manifestを生成する。要求や依存の推論、ブラウザ操作、ネットワーク、UML描画は行わず、図は用意したSVGを取り込む。

```text
python <skill>/scripts/render_prd.py <repo>/docs/prd/NNN_presentation.json --output <repo>/docs/prd/NNN_prd/NNN_PRD.html
python <skill>/scripts/render_prd.py <repo>/docs/prd/NNN_presentation.json --output <repo>/docs/prd/NNN_prd/NNN_PRD.html --check
# 別のローカル資料への相対参照を許可するときは --reference-root <docs> を指定
# 更新するときだけ --force を加える
```

動く架空例は[005_presentation.json](../assets/example/005_presentation.json)。案件へコピーし、内容・番号・版・合意状態を正本へ合わせる。例の要求や閾値を実案件へ持ち込まない。

入力はUTF-8 JSON、`schema_version: 1`。`number`（3桁文字列）、`title`、`subtitle`、`date`（YYYY-MM-DD）、`revision`、`status`、`canonical_document`は必須で、残りは任意。未知のkeyと不正な型は拒否される。

| key | 内容 |
| --- | --- |
| `canonical_document` | 正本MDの相対path。見出しを`source_refs`で参照 |
| `summary_cards` | `title`, `body`, `source_refs`の配列 |
| `diagrams` | `id`, `title`, `question`, `description`, `svg`, `source`, `caption`, `source_refs`, `sync_mode`, `sync_note`の配列 |
| `sections` | `id`, `title`, `paragraphs`, `bullets`, `source_refs`、任意の`table`（`headers`, `rows`） |
| `references` | `label`, `path`の配列。存在するローカル資料へのリンク |

参照pathはJSONの場所から解決する。正本・図・編集元と出力はそのディレクトリ配下。`references`だけは`--reference-root`の明示範囲内へ相対参照できる。既定はJSONのディレクトリ内。外部URL、入力の上書き、SVGのscript・イベント・外部参照は拒否する。図はinline埋込みで表示できるが、関連資料へのリンクは同梱範囲に依存するため配布前に再検証する。

正本全文も詳細へ含める。簡易Markdown表示の対応範囲は生成器のhelp/docstringを参照する。対応外の構文は告知して全文原文表示へ切り替え、内容を省略しない。

## 確認

- `--check`で入力版・hash、ローカル参照、見出し、重複ID、SVGの静的内容を確認する。ファイルは書き換えない。
- 正本とHTMLの目的→要件→AC、対象外、合意状態、Unknowns、根拠を照合する。静的確認だけで意味の一致を検証済みにしない。
- 利用可能なブラウザで目次、閉じた詳細への参照、表・図の横スクロール、図拡大、狭い画面、印刷を確認し、未確認を記録する。

資料の検証成功は要求の成立やアプリの受入成功とは別である。読みやすさの効果を測る場合は、同じ情報・版・設問で正答、所要時間、主観的な見やすさを分けて比較する。
