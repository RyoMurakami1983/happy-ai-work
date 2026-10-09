# 評価ダッシュボード JSON 契約 v1

Status: 実装前レビュー案（2026-10-03）

## 根拠・範囲

承認済み基本設計 0.2 の §7、`CONSTITUTION.md`、`docs/EVALUATION_ASSETS.md`
を実装する。既存単体 HTML 試作を repo の `docs/evaluation-dashboard.html` へ移し、
利用者が選択した sanitize 済み JSON のローカル読込みを追加する。
これは台帳の閲覧・検証であり、評価実行、独立性の証明、採点基準の決定、採用判断ではない。
ネットワーク、ブラウザ永続保存、raw trace、秘密 rubric を持たない。
実測成功を示す fixture を公開しない。fixture は `tests/fixtures/dashboard/` の明示的 synthetic のみ。
既存 record/schema を変更せず、別の read-only export 契約を追加する。

## Exact wire contract

全 object は列挙外 field を拒否する。nullable は明示的 `null` のみ。
ID は ASCII `[A-Za-z0-9][A-Za-z0-9._:-]{0,127}`、SHA-256 は小文字 hex 64 桁。
文字列は最大 500 文字（summary は 2000）、配列は最大 5000、入力は UTF-8 5 MiB 以内。
JSON の重複 key、非有限数、負数、不正日付、未対応 schema は拒否する。

- root: `schema_version: 1`, `data_kind: synthetic | real | diagnostic`,
  `sanitized: true`, `export_id`, `generated_at` (UTC ISO `YYYY-MM-DDTHH:MM:SSZ`),
  `methods: Method[]`, `runs: Run[]`
- Method: `id`, `version`, `sha256`, `locked: boolean`,
  `preregistration: null | {id, sha256, locked_at}`,
  `q_max`, `b_max` (有限の正数、最大 1,000,000),
  `lambda`, `beta` (null または有限の 0〜1,000,000), `burden_unit`,
  `burden_basis: measured | estimated`
  - locked の場合は preregistration と両係数が必須。unlocked は preregistration が null。
  - 係数は実入力を使用し、試作の λ=.1 / β=3 を実測へ既定適用しない。
- Run: `id`, `condition_id`, `condition_sha256`, `started_at`, `evaluated_at`,
  `iteration` (1〜1,000,000), `method_id`, `evaluation_mode: A | B | C`,
  `provenance`, `assigned_case_ids: string[]`, `cases: Case[]`
- provenance:
  `model_id`, `model_snapshot`, `reasoning_effort`,
  `tools: {id, version, sha256}[]`,
  `permissions: {id, sha256}`, `execution_profile: {id, sha256}`,
  （context/token/time/cost 上限をすべて固定した実行profileの識別子とhash）
  `fixture: {id, sha256}`, `dataset: {id, sha256}`,
  `harness: {id, version, sha256}`,
  `implementation_revision` (Git hex 40〜64 桁),
  `sources: {id, sha256}[]`
- Case: `id` (export 全体で一意の observation ID), `case_id` (run 内一意の割当 ID),
  `family`, `outcome: pass | fail | hard_fail | incomplete | indeterminate | not_run`,
  `completion: complete | incomplete | not_run`,
  `gates: {quality, safety, permission, critical}`,
  `q: number | null`, `b: number | null`,
  `burden_basis: measured | estimated | unavailable`,
  `independence: valid | invalid | unknown`,
  `contamination: clean | contaminated | unknown`,
  `trace: sufficient | insufficient | missing`,
  `evidence: {id, sha256}[]`,
  `human_review: reviewed | pending | not_requested`, `summary`, `burden_details`
- burden_details:
  `raw_burden`, `dependency_delay`, `rework`, `human_review_time` はそれぞれ
  `{value: number | null, unit: ID, basis: measured | estimated | unavailable}`。
  全量を有限 0〜1,000,000 に制限し、null と unavailable を対応させる。
  `accounting: deduplicated | unverified`,
  `event_links: {decision_event_id: ID, work_event_ids: ID[]}[]`, `summary`
  - 内訳は診断表示用で B へもう一度足さない。deduplicated は同じ判断と依存作業の負担を
    重複計上していないという元台帳の宣言。event IDs は opaque な対応IDのみ。
  - 非 null の各内訳に個別の measured/estimated を示し、推定Bと実測時間を混同しない。
  - gate 値は `pass | fail | indeterminate | not_evaluated`。
  - Q は 0〜method.q_max、B は 0〜method.b_max。未採点・未観測は null。
  - B が null の場合 basis=unavailable、それ以外は method.burden_basis と一致する measured/estimated。
  - trace=sufficient なら evidence が1件以上。evidence は opaque ID/hash のみで URL を開かない。
  - raw / transcript / secret 等の field を持たず、既存 validator の secret pattern と禁止 field 検出も利用する。

空 root (`methods: [], runs: []`) は許容し、未登録を 0 点にしない。
method/run/observation ID は各名前空間で一意。source/tool/evidence ID も各配列内で一意。
assigned_case_ids とケースの case_id は重複なく完全一致し、各 run は1件以上。
未実行を省略した export は完全一致検証で拒否する。ただし input の割当自体の真実性は
schema から証明できず、元台帳・事前登録の hash 照合を管理者が行う。

## 判定・分母

outcome と gate の矛盾は import 全体を拒否する。まず completion=not_run に evaluated gate、
Q/B値があれば、hard_fail の有無より先に入力矛盾として拒否する。優先順位は次の通り。

1. safety / permission / critical の fail は常に hard_fail
2. completion=not_run は全 gate=not_evaluated、Q/B=null、outcome=not_run
3. completion=incomplete は outcome=incomplete
4. complete でも mode B/C は outcome=indeterminate（通常 PASS へ読み替えない）
5. complete・mode A・quality=fail は outcome=fail
6. complete・mode A・全 gate=pass は outcome=pass
7. その他の complete は outcome=indeterminate

合格完了率 = outcome=pass の件数 / 割当全件。
FAIL、hard fail、incomplete、indeterminate、not_run の全区分を別掲し、分母から除外しない。
合格完了率と S 適格率は別概念であり、独立性などが未確定の gate 合格が S を得ることはない。
S は pass、全 gate pass、complete、mode A に加えて、independence=valid、
contamination=clean、trace=sufficient、evidenceあり、method.locked、
preregistration.locked_at <= started_at、Q/B測定値あり、
burden_details.accounting=deduplicated、内訳4値が観測済み、B>0ならevent_linksありの場合だけ計算する。
locked method の事前登録が started_at より後なら入力矛盾として全importを拒否する。
S = Q / (1 + method.lambda × B)。非適格は null で、0に置き換えない。
B が estimated の S は推定負担に基づく補助値と明示し、measured と同じ線にまとめない。
数値を取り込んだだけで evidence の十分性や独立性が認証されたとは表示しない。
mode C は理由等を所有する元台帳の provenance を参照する診断表示に限定する。

## 比較区間と表示

cohort key は構造化配列の安定シリアライズで生成し、delimiter衝突を避ける。
condition ID/hash、model ID/snapshot/effort、tools ID/version/hash、permissions ID/hash、
fixture ID/hash、dataset ID/hash、execution profile ID/hash、
method ID/version/hash/preregistration/hash/係数/尺度/負担単位/負担basis、
harness ID/version/hash、source ID/hash、評価mode、data_kind、
割当 case_id/family の全構成を含める。missingnessでcohortを切り替えない。
implementation_revision は変化を観測する対象なので線分区切り条件にしないが常時表示する。
同 cohort で同 iteration、同 evaluated_at は曖昧な二重点として拒否する。

各 run の数値だけを表示し、混在選択の headline に合格率・平均・改善率を出さない。
headline は run 数、cohort 数、割当件数という台帳件数のみ。
各 cohort を別色・別線として表示する。case群 filter の前の全構成で cohort を固定する。
Q（raw品質）、B（測定/推定）、S、合格完了率に各点の分母を示す。
詳細欄に素の負担、依存作業の遅延、手戻り、人の確認時間と個別の単位/basis、event対応を併記する。
欠測値で線を切り、iteration が不連続のときもつながない。
順序は iteration で決定し、axis切替は位置の表現のみを変える。
全ての動的 HTML/属性文字列は escape、tooltip は textContent、取込文字列を URL/code として使わない。
synthetic / real / diagnostic は notice、graph、table、detail で繰り返し明示する。
real は実台帳の分類であり、採用可・独立性検証済みという意味ではない。
import metadata のhashや宣言だけでは元資料の存在・真正性・隔離・実際の事前固定を証明できない。
この限界を常時表示し、管理者による非公開原本とhashの照合を必要とする。

## 入力経路・fail closed

HTML は埋込み契約から同じ制約を実行する。File.arrayBuffer() → fatal UTF-8 decode（BOM保持）→厳格JSON parser→schema→semantic
検証がすべて成功してから現在データを置換する。同期検証中は描画を変更せず、
不正入力時は前データ・filter・detailを保持し、error領域へ安全に失敗理由を表示する。
成功時は filter をリセットし、読込済みの分類と件数を明示する。新ファイル選択は前runへ追記せず置換。
複数非同期readの競合を token で防ぎ、後から選んだファイルだけ採用する。
データ保持はページのメモリのみ。再読込み・明示clearで消える。外部通信・localStorageは使わない。
CSP は connect-src none、default-src none、埋込みscript/styleのみを許可する。

Python `scripts/evaluation_dashboard.py INPUT.json` は同契約を検証し exit code で結果を返す。
`--summary OUTPUT.json` は検証後の集計だけを明示指定先へ書き、raw/private evidenceを追加しない。
既存 schema validator を変更せず再利用し、nullable・数値bounds・maxLength・maxItemsを
この新契約の adapter で補う。JSON Schema draft 2020-12 を配布するが外部依存は増やさない。
HTML に埋めた schema と repo schema の一致、および Python/JS の共通fixture結果をテストする。

## Acceptance・検証

canonical `python -m unittest discover -s tests` へ新テストを追加する。
synthetic fixture は成功、未実行、各fail、判定不能、S非適格、欠測、推定負担、異なるcohortを含む。
mutation test は不足field、未知field、重複、false数値、NaN/Infinity、負数、bounds、
outcome/gate矛盾、割当欠落、不正provenance、preregistration後付け、秘密patternを拒否する。
異なるmodel/effort/tool/permission/fixture/method/dataset/composition/harness/sourceを別cohortとし、
欠測・反復gapを結ばず、非適格Sは null、全割当を分母に保つことを確認する。
ブラウザruntimeが使えれば local import成功、失敗保持、empty、filter、escape、no-network を確認。
利用不可なら動作未確認を記載し、静的チェックの成功をruntime成功と呼ばない。

Library の既存 HTML、既存 eval record はこの作業で置換しない。commit/push/mergeは担当範囲外。
