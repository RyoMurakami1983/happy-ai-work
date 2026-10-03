# 012 — 比較pilot 技術設計レビュー

## Review v1 — 2026-10-03

### 結論と対象範囲

- **PASS: preparation / packaging の限定インフラ。** 固定した現行版と候補、publicな開発caseを準備し、allowlistからfresh directoryへ一条件だけを出力する範囲は実装できる。runner、private hold-out、採点、配布変更は含めない。
- **REVISE: dashboard の提示契約。** 実行budgetが比較区間を分けられず、合意した負担の内訳を保持・表示できない。下記M1/M2を修正して再レビューする。
- **BLOCKED: 実際の比較試験・採用判断。** model/環境/費用上限の確定と承認、事前校正、アクセス分離の実証、独立評価者、private hold-outが未準備。この状態はインフラ実装の禁止ではなく、実比較の開始条件が満たされていないことを意味する。72 runsや有料実行を許可する判定ではない。

既に許可された限定実装とdraft PRの範囲で、parentはpreparationを先に進め、dashboard担当は契約を修正する。新たな利用者判断を必要とする修正ではない。実行費用・方式等の所有者判断は実trialの前に別途必要。

### 対象版と独立性

基準commit: `ab32391c9612ad7983a4805040a6331ad5f576db`。設計は未commitのため、commitだけで対象版を特定せず、読んだ内容のSHA-256を以下に固定する。

Reviewer: `design-reviewer-01`。提示設計・candidate・実装の作成を担当していない動的reviewer。評価対象文書の自己申告を承認・合格の根拠にしていない。この設計レビューの役割分離は、将来のblind trialの隔離や完全なblindnessの証明ではない。共有filesystemのため、試験generatorの役には流用できない。

| 入力 | SHA-256 |
| --- | --- |
| `AGENTS.md` | `a3078fec1a59bdbe012e342111423ca8e8ab37f0dd5a4dcb48b633198c26b931` |
| `CONSTITUTION.md` | `61a9f2e813f78cc240e21c15800c85bd04e36e56f64edaed4e1680a97253129a` |
| `docs/EVALUATION_ASSETS.md` | `a71997a671d31fd60a591af6c158ec6b8bfd19bb3104e75dc43c1bef1940fe55` |
| `plugins/happy-preview/skills/technical-design-review/SKILL.md` | `3818ff4bbf898b142c7b7ce2e62157e0f95571ee7763cfe3b224404ec4755e2f` |
| 同skillの `references/purpose-driven-design-review.md` | `33367c107b7e0a6e8ce35a3a8f5825519b4a64a277fcbc32f22da1967fb43b01` |
| `docs/design/012_COMPARATIVE_PILOT.md` (0.1) | `afb8bf8b6acd2ee842e2e582ce550dc33fc65e7034c55f3f3bb7d4cef9152ca9` |
| `docs/design/012_DASHBOARD_DATA_CONTRACT.md` (初回提示) | `d7405a95929ab907f713ae383a0c5cdb8cb0d37c41557617af24e77a2be6b7f1` |
| 承認済み `happy-ai-work-basic-design.html` (基本設計0.2 / 評価方法v0.1) | `d227f7251e390b44ff89272ac2329487dfff77a8d4a4686de3518b3afbb09b29` |

基本設計は利用者提供の作業入力として検査し、公開repoへ複製していない。承認範囲の情報はparentのhandoffによる。レビューは実装前の構造と契約に限り、テスト実行、UI runtime、候補の行動効果の検証を含まない。

### 目的から観測までの確認

| 合意・不変条件 | 提示設計の保証と確認範囲 |
| --- | --- |
| implementだけの限定試験、配布物維持 | eval領域のsnapshot/candidate、no runner、現行plugin非変更。撤回は未採用候補を採用しないこと |
| 小修正・docs-only・UI・未承認の4群 | 各3caseの明示と全群維持。公開開発caseは未見hold-outに昇格しない |
| 第一応答だけではなく仕事の完了を観測 | artifact diff、toolと結果、test/runtime、質問・停止時点を外部observerが記録。未実施runtimeをPASSにしない |
| 必要な人の判断を抑制しない | 適切な停止・新事実による質問は0。必要質問の基本負担を除き、合理的に早く気付けた依存作業だけ遅延対象。無許可続行はhard fail |
| gateを高得点で相殺しない | hard failで採用停止。A/B/C、S適格性、合格完了率を分離。失敗・未完了・未実行を割当分母に保持 |
| generatorと採点資産を隔離 | fresh directoryやforkなしだけでは不十分と明記。mount、検索、connector、network、ログ、親contextを実際に試験するgate |
| 独立評価とblindness | 独立grader、匿名化による意味喪失はblind不可。役名変更・共有contextを独立証明にしない |
| 因果効果・一般化を誇張しない | 正式model/設定等を固定しない結果はinstructionの因果効果にしない。反復は独立task数でなく、小規模は診断。実利用2件未観測は効果未確認 |
| 私的資産を公開しない、過去記録を保つ | raw/private判定はrepo外、publicはsanitize済み。既存schema/records/historyを変更しない。事後変更は別method/run |

### 指摘

#### M1 — 実行budgetが変わった結果を同じ条件の推移として表示できる（MAJOR / REVISE）

根拠: 基本設計§7「同じ…時間/token上限」、pilot「実行前gate」のcontext予算・token/time/cost上限、dashboard「Exact wire contract」「比較区間と表示」。

現行provenance/cohortにはmodel、tools、permissions等がある一方、context/token/time/cost budgetを識別する項目がない。同じmodel・case・methodでも、実行上限を増やしたrunが同じ線へ入る。完了率や負担の変化をinstruction変更と混同しやすく、比較条件を固定する契約をviewerが保持できない。

最小修正: context/token/time/cost上限を含む固定execution-profileのID/hashをprovenanceの必須項目にし、cohort keyへ含める。完全な内容を公開に含める必要はなく、hashの参照先を元台帳で検査する責任を明示する。実際の消費量と上限を区別する。上限の変化を別cohortにするmutation testを追加する。

戻り先: dashboard設計担当（technical-design）。修正後、contractとcohortへのtraceを再確認する。

#### M2 — 必要な判断の抑制や負担の二重計上を見抜く内訳を取り込めない（MAJOR / REVISE）

根拠: 基本設計§7「Q、各gate、素の負担、遅延、手戻り、人の確認時間、Sを併記」、pilot「方法の事前登録」のB内訳と重複event統合。dashboardのCaseはq/bだけで、unknown fieldを拒否する。

現在のwire contractでは同じBに集約される理由を表示できず、適切な必要質問に基本負担を付けたrunや重複した手戻りを、集計だけから点検できない。private raw traceを公開する必要はないが、合意した診断の内訳を表示できる契約は必要。

最小修正: sanitize済み・nullableな素の回避可能負担、遅延、手戻り、人の確認時間と、それぞれの単位・測定/推定/欠測の区別を追加する。Bへ加算する排他的な内訳と、二重加算しない補助観測を区別する。必要質問そのものは0、回避可能な先送りのみを遅延とする既定を残す。未測定を0とせず、UI/detailで内訳・欠測・basisを表示する。詳細なevent対応と判定根拠の正本はprivate台帳に残してよい。

戻り先: dashboard設計担当（technical-design）。内訳の定義・欠測・二重計上防止を再確認する。

#### C1 — 後付け登録の扱いと未実行の矛盾を一意にする（限定的契約明確化）

S適格条件は`locked_at <= started_at`だが、Acceptanceは後付け登録を拒否する。import拒否なのか、台帳として受理してSをnullにするのかを一つに固定する。どちらも事後登録を通常の有効評価へ昇格させてはならない。

また、outcomeの優先順位だけをそのまま実装すると、completion=not_runかつsafety=failをhard_failとして受理し得る。not_runなら全gateがnot_evaluatedであることを先行整合性制約として強制する。

### 未解決gateと受容していないリスク

実trialの開始前に、所有者/評価担当が以下を確定・実証する。

1. 正式model variant/snapshot取得可能性、effort、harness、tools、permissions、fixture/contextと実行上限。72 runsは提案規模であり費用・時間の承認は未充足
2. Qのanchor/threshold、Bの単位・重複除去、依存eventと最初に知り得た時点、係数の独立校正とbaseline前登録。必要質問への萎縮・巨大質問へのまとめ・欠測除外をgaming例として確認
3. generatorからprivate重み・case集合・正解・ログ等へのreadが拒否されるアクセス試験、外部observerの証拠、graderの独立性と実際のblind化
4. public開発caseと独立管理hold-outの区別、完全な割当台帳。schemaだけでは割当自体の真実性、宣言されたclean/valid/sufficient、hash参照元の真正性は証明できない
5. 実行traceと成果物による品質・安全・承認・TDD・HITLの確認。UI runtime未観測やHITL未完了を、build/test成功で代用しない

同一model等の統制は因果解釈の必要条件であり十分条件ではない。実trial計画では実行順・model drift・順序効果も事前固定して確認する。現pilotは一般優位を主張しない診断のため、この未確定を準備scriptの実装blockerへ拡大しない。

### 再レビューと次の一歩

preparation担当はPASS範囲だけを実装し、allowlist、hash、可搬性、既存先拒否、4群保存を検証する。dashboard担当はM1/M2/C1の契約を修正してhash付きで再提示する。reviewerはこのv1を保持し、本fileへ新しい対象hashと修正確認を別review versionとして追加する。

独立差分review、canonical quality、両OS CI、ブラウザruntime検証は後工程。設計PASSをそれらの実施・成功と記録しない。

## Review v2 — 2026-10-03（契約修正の限定再レビュー）

### 結論

**PASS: preparation / packaging とdashboardの限定インフラ設計。** v1のM1/M2/C1は修正版で解消した。review v1を変更せず、以下の新版だけにdashboardのPASSを適用する。actual blind trial、係数の妥当性、行動改善、採用判断は引き続き**BLOCKED**であり、前節の未充足gateを維持する。

| 再確認した対象 | SHA-256 |
| --- | --- |
| `docs/design/012_DASHBOARD_DATA_CONTRACT.md` (修正提示版) | `5d5d44f3bd762b54797ecd66cf1f9b35ab77931e3b7570577bdd291255a527e8` |
| `docs/design/012_COMPARATIVE_PILOT.md` (0.1、変更なし) | `afb8bf8b6acd2ee842e2e582ce550dc33fc65e7034c55f3f3bb7d4cef9152ca9` |

他の規範入力・reviewer・独立性・評価範囲はv1のとおり。修正設計の全文を読み、変更の影響するwire contract、cohort、S適格性、UI表示、入力整合性の対応を再確認した。実装はレビュー範囲に含めていない。

### 解消確認

- **M1 解消:** context/token/time/cost上限をすべて含む`execution_profile`のID/hashをprovenanceへ追加し、cohort keyにも含めた。実際のprofile内容の検証は元台帳管理者の責任であり、宣言されたhashだけで同一性を認証しないことを常時表示する。
- **M2 解消:** `burden_details`に素の負担、依存作業の遅延、手戻り、人の確認時間をnullable・個別unit/basis付きで追加した。opaque event IDの対応とaccounting宣言を保持し、内訳をBへ再加算しない。detailへ内訳・欠測・basisを示す。Sは内訳未観測や未確認accountingではnullになり、割当分母は減らさない。
- **C1 解消:** locked methodの事後登録はimport全体の矛盾として拒否する。not_runのgate/Q/B制約をhard_failの優先順位より先に適用する。
- **関連する変更:** Methodにburden basisを固定し、非nullのCase Bは一致させる。欠測でcohortを分断せず、measuredとestimatedを別cohortにする。内訳の測定/推定は個別表示なので、推定Bと実測review時間の共存を偽装しない。

### 実装へ渡す確認点と残る限界

以下は未受容の重大問題を条件付きで通すものではなく、今回PASSした契約を実装・検証するための確認点である。

1. preparationのallowlist/hash/no-overwrite、全4群、独立したpackage内参照をfocused testで確認する。bundle準備をOS/context/toolアクセスの隔離と表示しない
2. execution_profile変更を明示的なcohort mutation testへ含める。全割当の分母、欠測・estimated、後付け登録、not_run矛盾、旧表示保持、unknown field/duplicate/nonfinite、XSS/no-networkをPython/JSと利用可能なbrowser runtimeで確認する
3. `raw_burden`はpilotと基本設計で定義した回避可能な負担を意味する。人の確認時間を観測しても、必要な判断・適切な停止の時間を自動的にBへ加算しない。推定値を実測と表示しない
4. eventリンク・deduplicated・valid・clean・sufficient・sanitizedは入力元の宣言であり、schema PASSがその真実性の証明になることはない。必要なhuman acceptanceが未完了なら、元台帳のcritical/quality gateをpassにしてはいけない
5. publicなtestsにはsyntheticだけを保存する。private係数・rubric・raw evidence・実際の利用者情報をfixtureやreviewへ転記しない。既存case/schema/record/historyを不変に保つ

数値の内訳はgamingの観測可能性を上げるが、それだけで適切な採点を保証しない。独立校正と実traceの照合、必要な判断を萎縮させない方法の実利用確認は別工程である。real/diagnosticのラベル、単一のS、インフラtestsのPASSを採用根拠へ昇格しない。

次は実装担当が承認済み範囲のTDD実装を行い、差分・実行evidenceを別の独立実装reviewへ渡す。actual trialの実行条件が確定するまでは、合成fixtureと決定的検証の到達点だけを報告する。
