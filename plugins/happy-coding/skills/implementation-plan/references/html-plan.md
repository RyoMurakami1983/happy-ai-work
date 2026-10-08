# 図入りHTMLによる実装計画

複数sliceの依存、開始条件、人の確認が必要な境界を読みやすく示す。Markdown正本の実行契約を維持し、HTMLを読む入口として併用する。局所変更は主スキルの短縮条件を使う。

## 読み順と表現

目的・対象範囲・実装許可 → 実装の依存 → 各sliceの観測結果 → 開始条件と人の確認 → 未確定事項・検証・戻り先 → 正本の詳細の順に置く。[plan.html](../assets/plan.html)は目次、要点カード、図拡大、表の横スクロール、詳細折畳みを持つオフラインテンプレートである。状態は色だけでなく文字でも示す。

| 読者が判断したいこと | 表現 | 保つ説明 |
| --- | --- | --- |
| 何から動かし、何を済ませて次に進むか | 依存図、slice一覧 | 矢印は実依存。日程や工数の根拠にはならない |
| 一工程で何が動けば完了か | 観測結果、Done、AC対応表 | 正本の受入条件と同じ範囲 |
| どの条件を誰が確認するか | 開始条件、影響slice、担当、再開の証拠 | 実装許可、外部前提、HITL受入を区別 |
| 利用者が何を操作して確認するか | HITL review contract | milestone、launch、代表操作、期待結果、再開条件 |
| 何が検証済みで、何が未確認か | 検証予定・実績、未確定事項、戻り先 | 予定commandの記載を実行成功と扱わない |

図数、slice数、技術構成を固定しない。既決設計を参照し、未確定の構造を計画側で確定しない。外部条件待ちは影響sliceへ示し、取得済みの実装許可の範囲で進められる作業を判断する。図の独立した枝を新しい実装許可と扱わない。

## 保存と同期

```text
docs/plan/
  NNN_PLAN.md                 # 正本。従来の保存先を維持
  NNN_presentation.json       # 要約・図説明・正本見出しへの対応
  NNN_plan/
    NNN_PLAN.html             # 派生する読解用資料
    diagrams/                 # 必要な図と編集元
    validation.json           # 入力版・hash・静的確認
    verification.md           # 内容・表示確認の結果（記録する場合）
```

NNNはPRD・設計と共有する。既存正本の移動や`PLAN_DONE`への改名をHTML化だけで行わない。別配置を指定された場合はその指示に従い、生成入力、リンク、後工程handoffの実在pathを揃える。

要約・図・節の`source_refs`から正本見出しへ辿れるようにする。正本変更後は依存方向、開始条件、Done/AC、HITL再開、実装許可、未確定事項、予定/実績を照合して再生成する。hash一致は鮮度の証拠であり、意味の一致は別に確認する。

編集可能なSVG自体を表示する場合は`single-source`、UML等の編集元とSVGを別管理する場合は`reviewed-pair`を使える。後者では編集元と画像のノード・矢印・条件・状態を照合し、未更新を残さない。

## 生成器

正本には[NNN_PLAN_TEMPLATE.md](../assets/NNN_PLAN_TEMPLATE.md)を使う。`scripts/render_plan.py`はPython 3標準ライブラリだけでHTMLと静的検証manifestを生成する。ネットワーク、ブラウザ、UML描画、依存の推論は行わない。図は用意したSVGを取り込む。

```text
python <skill>/scripts/render_plan.py <repo>/docs/plan/NNN_presentation.json --output <repo>/docs/plan/NNN_plan/NNN_PLAN.html --reference-root <repo>/docs
python <skill>/scripts/render_plan.py <repo>/docs/plan/NNN_presentation.json --output <repo>/docs/plan/NNN_plan/NNN_PLAN.html --reference-root <repo>/docs --check
# 再生成には --force。--check は書き込まない。
```

入力specから相対pathを解決する。正本、SVG、編集元、出力はspecディレクトリ配下。関連資料の`references`と正本内リンクは、明示した`--reference-root`内の兄弟資料へ参照できる。既定はspecディレクトリ内。入力上書き、外部URL、アクティブなSVGは拒否する。

入力はUTF-8 JSON、`schema_version: 1`。`number`（3桁）、`title`、`subtitle`、`date`（YYYY-MM-DD）、`revision`、`status`、`canonical_document`は必須。未知のkeyや不正な型は拒否する。

| key | 内容 |
| --- | --- |
| `canonical_document` | 正本MDの相対path |
| `summary_cards` | `title`, `body`, `source_refs`の配列 |
| `diagrams` | `id`, `title`, `question`, `description`, `svg`, `source`, `caption`, `source_refs`, `sync_mode`, `sync_note`の配列 |
| `sections` | `id`, `title`, `paragraphs`, `bullets`, `source_refs`、任意の`table`（`headers`, `rows`） |
| `references` | 実在するローカル資料の`label`, `path`の配列 |

架空例は[003_presentation.json](../assets/example/003_presentation.json)。example全体をコピーして内容・番号・参照を置き換える。例のcommandは未実装であり、slice数、HITL数、検証budgetは案件の既定値にしない。

正本全文を詳細へ埋め込む。簡易Markdownの対応範囲は生成器のdocstringを参照する。task listは「未完了」「完了」の静的表示にし、HTMLから進捗を書き換えない。対応外の構文は全文の原文表示へ切り替え、欠落を防ぐ。

## 確認

- 生成器の`--check`で入力版、hash、ローカル参照、見出し、重複ID、SVGの静的内容を確認する。
- 正本とHTMLの依存方向、開始条件、Done/AC、HITL再開、実装許可、未確定事項、予定/実績を照合する。
- 利用可能なブラウザで目次、折畳み参照、通常/拡大、狭い画面、印刷を確認する。静的確認と実表示の確認を分け、未確認を記録する。

資料の検証成功はアプリや実APIの受入成功とは別である。読みやすさの効果を測る場合は同じ情報・対象版・設問で比較し、正答、時間、主観的な見やすさを分ける。
