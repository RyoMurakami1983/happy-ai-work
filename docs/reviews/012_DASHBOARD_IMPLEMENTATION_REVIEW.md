# 012 — dashboard実装の独立レビュー

## Review v1 — 2026-10-03

### 結論と適用範囲

**PASS: sanitize済みJSONの取込み・決定的集計・表示コードの限定レビュー。重大な未解消指摘なし。**
初回に確認した数値型のPython/JS不一致、配布schemaの部分一致、UTF-8の置換読込み、
real分類の実測表現は修正され、下記の最終版で再確認した。

**実ブラウザ表示・操作・CSP適用・通信観測・desktop/mobile screenshotは未確認。**
ブラウザはHTML実行前に環境制約で停止した。Nodeでの検証とDOM stubによるevent検証を、
実ブラウザでの成功へ読み替えない。actual model trial、独立採点の真正性、改善効果、
candidate採用、公開push/PR/mergeについてのPASSではない。

Reviewer: `dashboard-reviewer-01`。対象implementation/schema/fixture/testの作成・修正を
担当せず、指摘は実装担当へ返した。reviewerがrepoへ追加した成果物はこのreview recordだけ。
役割分離は実装レビューの独立性であり、共有filesystem上の作業をblind trialの隔離証明にしない。

### 対象版

基準commit: `ab32391c9612ad7983a4805040a6331ad5f576db`。
対象は未commitのため、実装担当の最終版確定後に内容のSHA-256を採取した。

| Path | SHA-256 |
| --- | --- |
| `docs/evaluation-dashboard.html` | `71f0e355aeb000edf7f30cfc49bc99fad63f5b451ce9880e875104cd1067dc8e` |
| `scripts/evaluation_dashboard.py` | `65d625e28d5a3ef40d620c0f4ef6781111ffd826c96708e7903475dd40a5a201` |
| `tests/test_evaluation_dashboard.py` | `1d2a08ab8d1a53274c816435b26b264da2a25f222d5cda76cd3a609babd1165b` |
| `evals/schema/dashboard-export.v1.schema.json` | `89b69863d97cc8fdb4920cd0b5872f39491e96e1ebbbff05474237cf62157a18` |
| `tests/fixtures/dashboard/synthetic.v1.json` | `7b6ecb26630b598402f0a69e1ce7cfea54afdf314889ef7d46bae5c7ca72c722` |
| `docs/design/012_DASHBOARD_DATA_CONTRACT.md` | `214e0bc43932be5e1d1b335135004f19cf4fe2c3035779868511ddcb2c461719` |

規範入力は`AGENTS.md`、`CONSTITUTION.md`、`docs/EVALUATION_ASSETS.md`、
`docs/reviews/012_TECHNICAL_DESIGN_REVIEW.md`のreview v2で承認されたdashboard契約。
`deep-review`のpreflightを適用した。最終契約の`File.text()`からfatal UTF-8 decodeへの変更は、
不正入力拒否とPython/JS整合性を実装するための局所修正として確認した。

### 指摘の修正確認

1. **解消: mathematical integerの不一致。** 初回は`schema_version: 1.0`と
   `iteration: 1.0`をJSだけが受理した。Python側の新契約adapterで有限の整数値を
   検査できるようにした。共有validatorは変更していない。両経路の受理を再確認し、
   小数反復番号・boolean数値は拒否される。
2. **解消: 配布JSON Schemaのpatternが部分一致。** 初回のpatternは標準的なsearch意味では
   `!!abc!!`や129文字のID、余分な文字付きhashを許した。schemaに開始・真の末尾境界を追加し、
   embedded schemaとの一致を確認した。adapterも全体一致を確認する。
   LF/CR/U+2028/U+2029末尾付きIDはPython/JS両方で拒否された。
3. **解消: malformed UTF-8の黙示置換。** `File.text()`は不正byteを置換し得るため、
   `arrayBuffer()`とfatal `TextDecoder`へ変更した。BOMは保持して厳格JSON parserへ渡し、
   Pythonと同じく拒否する。実際のimport event handlerをDOM stubで実行し、
   不正byteとBOMで表示中のdata/filter/detailが変わらないことを確認した。
4. **解消: real分類を実測値と同一視する表現。** rootのrealを「実台帳」とし、
   実際の台帳記録という分類と、B・各内訳のmeasured/estimatedを区別した。
   sourceの真正性・独立性・隔離・事前固定を未検証とする常時注意書きを維持する。

### 実行した決定的検証

- Python 3.14.7で`python -m unittest discover -s tests -p test_evaluation_dashboard.py -v`:
  **10 tests PASS**。HTML/schema/fixture一致、CLI出力、未知field、重複、bounds、
  gate矛盾、事前登録、cohort、S適格性、Python/Node parity、欠測・反復gapを含む。
- 独立した合成probe **2,329件**でPython/Nodeの受理結果と契約上の期待が一致。
  うち2,304件は3 mode × 3 completion × 4値の4 gateの全組合せ。
  not_runの未評価gate制約を先に適用し、その後のhard fail、incomplete、B/C、
  quality fail、pass、indeterminateの優先順位を確認した。
  残るprobeは型、負数・上限、割当欠落・重複、証拠、日付、登録、secret pattern、
  Unicode surrogateと長さ境界等を含む。
- independence、contamination、trace、Q欠測、B欠測の独立した5変更で、
  gate上の合格完了率100%と割当分母1を保ちつつ、Sをnull・S対象数0にした。
  gate合格率とS適格性が別物であることを確認した。
- 15種のrun/provenance/composition変更、12種のmethod/registration変更、data_kind変更の
  **計28変更**でcohortが分かれた。implementation revision、欠測、family filterでは
  元のcohort identityを保持した。混在headlineは台帳件数だけで、合算した性能値を持たない。
- HTML中の実event handlerを最小DOM stubとともにNodeで実行し、成功取込み、
  family/cohort/axis変更、detail生成、不正入力時の表示保持、置換、後からのfile選択優先、
  clear/sampleによるpending read無効化、後から選んだ不正fileに対する古い成功readの無効化、
  empty export、XSS文字列のescape済みHTML生成を確認した。
- tooltipの`textContent`、動的HTML/属性のescape、opaque evidence ID/hashをURL/codeとして
  使用しないこと、`connect-src 'none'`と永続保存・通信APIの不使用を静的に確認した。
  CSPが実ブラウザで適用されたことやnetwork requestが0件だったことは未確認。
- Q/B/Sはrunごとで、全割当と観測・適格分母を表示する。推定Bと実測の人の確認時間は
  個別のbasisを保持し、負担内訳をBへ再加算しない。非適格Sと未観測を0に置換しない。
- `git diff --check`: PASS。全repo canonical quality・両OS CIはこのreviewの実行結果に含めない。

以上は全て公開のsynthetic fixtureまたはその一時mutationによる検証であり、
private dataへのアクセス、新規model呼出し、実比較、公開操作は行っていない。

### 実ブラウザ検証の未充足と次の確認

既存のPlaywrightとChromiumでlocal HTMLのheadless検証を試みたが、Chromiumの起動が
`socket() failed: Operation not permitted`で停止した。承認されたsandbox escalationによる
1回の再試行も同じ起動段階で停止した。利用可能なcloud browserでは`file://`がURL policyで
拒否された。制限回避、追加hosting、公開uploadは行っていない。

このため、browserでの実操作、file picker、描画崩れ、mobile幅、keyboard操作、
download、reload後の消去、CSP enforcement、外部通信0件、screenshotは未検証。
DOM stubはbrowser DOM・layout・security modelを再現しないので、これらの代替証拠にはしない。
既に許可された実行環境でHTMLを開ける段階に、success/error preservation、out-of-order read、
clear/filter、XSS、no-networkとdesktop/mobile表示を確認する。

台帳の`valid`、`clean`、`sufficient`、`deduplicated`、hash、preregistrationは元資料の宣言である。
必要なhuman acceptanceが未完了なら元台帳のgateをpassにしない責任、独立grader、
非公開原本のhash照合、実trial開始前gateは引き続き元の評価手順が所有する。

## Review v2 — 2026-10-03（CLI出力先保護の限定再レビュー）

**PASS: CLI集計出力の既存file保護。追加点検で見つかった上書き問題は解消。**
v1はCLIの既存出力先保護まで確認できていなかった。追加点検で、`--summary INPUT.json`が
入力台帳を集計結果へ上書きし、成功exit codeを返すことが判明した。reviewerも一時的な
synthetic入力で同じ破壊を再現した。v1の本文・対象hashは変更せず、この追記で補正する。

### 修正と最終版

`Path.open("x", encoding="utf-8")`による排他的な新規作成へ変更した。
存在確認後にwriteする方式ではないため、入力alias・既存出力・並行作成を同じ境界で拒否する。
`OSError`は明確な出力エラーと非zero exit codeになり、成功表示を返さない。
集計規則・schema・fixture・HTMLはこの修正で変更していない。

| Path | SHA-256 |
| --- | --- |
| `scripts/evaluation_dashboard.py` | `08f8ff5c6add0967cf7e8c8fc7433e46c9853324b7d099b25affaf430cb03398` |
| `tests/test_evaluation_dashboard.py` | `ecdf97a18a365bfe427fb71850c80ff82ede5a41232c37f099cbfe77659b3bed` |
| `docs/evaluation-dashboard.html`（変更なし） | `71f0e355aeb000edf7f30cfc49bc99fad63f5b451ce9880e875104cd1067dc8e` |

### 限定検証

- Python 3.14.7のdashboard focused suite: **15 tests PASS**。入力同一path、既存summary、
  symlink/hardlink、書込み先親directory不在に関する5 testsが追加された。
- reviewerの独立した一時directory検証で、入力同一path、既存summary、directory指定、
  親directory不在、入力へのsymlink/hardlinkの6条件を拒否。入力と既存fileのbyteが
  不変で、成功表示もtracebackも出ないことを確認した。
- fresh出力は正常なJSONを新規作成し、入力を変更しなかった。
- 異なる合成入力を持つ2 processが同じ新規出力へ同時に書く検証では、一方だけ成功、
  他方は拒否された。出力は成功した側の完全なJSONと一致し、上書き・混在はなかった。
- HTMLのhash一致を確認した。v1の2,329件の無関係な全probeはこの局所修正では再実行していない。

このPASSは既存fileの保存境界と通常の新規出力の確認であり、disk故障時のdurabilityや
新規fileへの書込み途中の障害復旧を保証するものではない。v1の実ブラウザ未確認、
actual trial未実施、真正性・採点・採用判断の範囲外という制限は全て維持する。
