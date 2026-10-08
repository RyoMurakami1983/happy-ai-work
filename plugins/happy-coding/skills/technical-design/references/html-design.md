# 図入りHTMLによる設計資料

新規開発や複数の境界の設計を、読者が構成・責務・処理順・失敗時の保証で判断できる資料にする。Markdown正本の設計契約を維持し、その入口としてHTMLを併用する。簡単な変更へこの形式を要求しない。

## 読み順と図の選択

推奨する読み順は、目的と今回の判断 → 全体構成 → 必要な詳細図 → 失敗時の扱い・未確認事項 → 詳細本文と根拠。白灰の面・青の強調、余白、目次、図の拡大、表の横スクロール、詳細の折畳みを持つ [design.html](../assets/design.html) を利用できる。色だけで状態を伝えない。

| 判断したい問い | 図の候補 | 誤解を防ぐ説明 |
| --- | --- | --- |
| 誰が何を担当し、何へ依存するか | 構成・コンポーネント図 | 静的依存と実行時I/O、内外の境界を区別 |
| 何を一体として管理し、誰が条件を守るか | クラス・ドメイン図 | 所有と参照、集約境界、多重度、不変条件の責任 |
| 外部I/O・保存・失敗はどの順に起きるか | シーケンス図 | 成功と部分失敗、取引が一体でない場合の保証差 |
| どの状態で何を許可するか | 状態遷移図 | 遷移条件、失敗時の状態、再試行と中断の範囲 |

必要な問いを解く図だけ選ぶ。アーキテクチャやDDDの採否を表示形式で決めない。各図に「判断したい問い」「読み方・保証範囲」「正本の参照見出し」を添える。設計案を実装済みの構成として描かない。未確認・提案・承認済みの違いを本文と同じ言葉で表示する。

## 保存・同期

```text
docs/design/NNN_design/
  NNN_TECHNICAL_DESIGN.md  # 規範となる設計正本
  NNN_DESIGN.html         # 読解用の派生資料
  presentation.json      # 要約・図の説明と正本見出しへの対応
  diagrams/              # 表示するSVG等
  uml/                   # 必要な場合の編集用UML
  validation.json        # 版・入力hash・確認結果
```

これはHTML併用の選択ルート。既存Markdownだけの案件は従来配置を保つ。既存案件の移動は利用者が依頼した場合にリンクと生成処理を一緒に更新する。PRD・domain model・ADRを同じ場所へ移す必要はない。持ち運び時にどこまで同梱すれば参照を開けるかも記録する。

図は可能なら一つの編集用ソースから描画する。編集可能なSVG自体を表示に使う方式もよい。PlantUMLとSVGを別に定義する場合は `reviewed-pair` とし、ソースの編集だけでは画像は更新されない旨と、ノード・依存方向・多重度・遷移・分岐の照合結果を残す。hashで意味の一致を保証したと書かない。

正本変更後は、要約と図の参照箇所を再確認して再生成する。新たな要求・自動復旧・実装承認などを要約で追加しない。HTMLだけの独立した要件正本は作らない。

## テンプレートの利用

スタイルのみ使う場合は `assets/design.html` の名前付きスロットを埋めてもよい。繰り返し生成には `scripts/render_design.py` を使える。Python 3の標準ライブラリのみで動き、外部図サービス・インストール・ブラウザ起動を行わない。既存SVGとその編集元を取り込み、UML描画そのものは行わない。

正本の記入用構成は [technical-design.md](../assets/technical-design.md)。規模に合わせて見出しを省略・統合し、記入例の文章を要求の正本として残さない。

```text
python <skill>/scripts/render_design.py <case>/presentation.json --output <case>/NNN_DESIGN.html
python <skill>/scripts/render_design.py <case>/presentation.json --output <case>/NNN_DESIGN.html --check
# 案件外のPRD/ADRへの相対参照を許可するときは --reference-root <docs> を指定
# 更新するときだけ --force を加える
```

動く架空例は [assets/example/presentation.json](../assets/example/presentation.json)。そのディレクトリを案件へコピーして内容と番号を置換する。実案件のアプリ名・ID・ユーザーのパス・固定の図数はテンプレートへ持ち込まない。

入力はUTF-8 JSON、`schema_version: 1`。`number`、`title`、`subtitle`、`date`、`revision`、`status`、`canonical_document` は必須。残りは必要な項目だけ指定する。未知のkeyや不正な型は拒否される。

| key | 内容 |
| --- | --- |
| `canonical_document` | 正本MDの相対path。見出しを `source_refs` で参照 |
| `summary_cards` | `title`, `body`, `source_refs` を持つ要点カードの配列 |
| `diagrams` | `id`, `title`, `question`, `description`, `svg`, `source`, `caption`, `source_refs`, `sync_mode`, `sync_note` の配列 |
| `sections` | `id`, `title`, `paragraphs`, `bullets`, `source_refs`、任意の `table`（`headers`, `rows`） |
| `references` | `label`, `path` の配列。存在するローカル資料へのリンク |

参照ファイルはpresentation.jsonの場所から解決する。正本・図・編集元と出力はそのディレクトリ配下。外部URL、出力による入力上書きは拒否する。`references` だけは `--reference-root <docs>` で指定したローカル範囲内の `../../prd/` 等も参照できる。既定は案件ディレクトリ内。入力SVGにscript・イベント処理・外部参照を含めない。図はinlineで埋め込み、ネットワークがなくても表示する。外部資料への相対リンクは同梱範囲によって開けなくなるため、配布前に再検証する。

正本本文も「詳細」に掲載する。簡易Markdown表示の対応範囲は生成器のhelp/docstringを参照する。対応しない構文を黙って省かず、原文表示に切り替えて告知する。要約の独立した執筆は許容するが、必ず `source_refs` を持ち、意味の照合を行う。

## 検証と評価

- 生成器の検証：入力schema、図XML・危険な参照、ファイル・見出し・HTML内リンクの存在、重複ID、入力hashと生成版。`--check` は書き込まず、古い生成物を検出する。
- 資料の照合：正本と要約・図の要件対応、決定状態、対象外、失敗時の保証とUnknowns。図の描画元が別ならその対応も確認。
- 表示の確認：図のラベル重なり、文字の大きさ、通常表示・拡大、狭い画面、折畳み、印刷。利用可能な表示手段で確かめ、未確認は未確認と書く。禁止された表示経路を迂回しない。
- 判断支援の評価：MDのみとHTML併用へ、責務・完了条件・部分失敗・未確認事項に関する同じ設問を使う。正答・根拠・時間・主観的な見やすさを分ける。同じ情報量と対象版を使い、HTMLの要約・構成・図それぞれの影響を分けて扱う。

レビュー要否は元スキルの基準に従う。利用者が見やすいと評価した事実、資料の独立レビュー、比較実験の結果は別の証拠である。静的検証だけでブラウザ動作・意味の整合・理解向上をPASSにしない。
