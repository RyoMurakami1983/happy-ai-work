# implement比較の準備基盤

**実モデル比較は未実行、候補未採用、配布pluginは変更しない。**
2026-10-22にPR #54を整理し、旧比較案と、計画統合・#61・#62を含む現行版の入力を分離した。
現行の状態・残件は [整理記録](../../docs/reviews/012_REFRESH_STATUS.md) を参照する。

## 使えるものと、まだ決めていないもの

- 入力準備script、公開・合成の4群×3 case、JSON検証とダッシュボードは再利用する。
- `current-v2` は main `1854315e78454f1f3b98ad9f9ea9ce2217cbf013` のimplement全25 filesと必要なPRD/設計HTML参照依存を固定したbaselineのみ。
  新candidateは未作成。旧candidateを代わりに混ぜず、candidate指定は出力前にエラーにする。
- `legacy-v1` は `ab32391c9612ad7983a4805040a6331ad5f576db` と旧lean候補の未実行案。
  計画統合前の条件・廃止済みimplementation-planへの指示を含むため、現在の採用判断に使わない。
- `baseline/`、`candidate/`、`cases.v1.json`、`tasks/`、`fixtures/`、`preparation.v1.json` はbyte保持。
  旧候補の文言を現行に直して過去の設計レビューと混同しない。旧入力のhash inventoryも保存した。
- `snapshots/current-v2/` と `snapshots/legacy-v1.inventory.json` は既存append-only規約の対象。
  入力を変えるときは新versionを追加する。実行方法・条件の事前登録まで完了した意味ではない。

## 現行baselineの入力を準備する

repo外の存在しない出力先を使う。Windowsでは自身の一時directory下の絶対pathを指定する。

```sh
python scripts/comparison_bundle.py baseline small-fix-normal /tmp/actor-current
```

既定は`--suite current-v2`。一条件のskill tree、依頼、fixture、source hashのみを出力する。
現在の12 caseは旧案と同じ公開開発課題で、計画統合や#61/#62の全受入を覆うhold-outではない。
新candidateを作る際は、対象仮説に必要なcaseを新versionで追加し、比較する両条件で固定する。

旧案の再現を明示的に必要とする場合だけ:

```sh
python scripts/comparison_bundle.py candidate small-fix-normal /tmp/actor-legacy --suite legacy-v1
```

`SOURCE.json`は`suite_id`、`baseline_revision`、hashと、`comparison_ready: false`、
`isolation_verified: false`、`trial_authorized: false`を保持する。
**別directoryはアクセス隔離ではない。scriptはrunnerではなくmodelを起動しない。**
古いコマンドのcandidate指定は今後既定では失敗する。旧案なら明示的なsuite選択が必要。

actor開始directory・instruction発見方法は実行前にharnessで固定する。
`.agents/skills`はbundle root、作業対象は`workspace/`、依頼は`task.md`。
採点資料や他条件は同梱しない。`fixtures/docs/README.md.fixture`は作業対象の壊れたリンクを含む合成入力で、
出力時に`.fixture`を外す。repo文書の不具合とは区別する。

## 実比較開始前の条件

新candidateの仮説・変更範囲、対応する両条件の入力hashとcase範囲、正式model/snapshot、effort、
tools/権限、context/token/time/cost上限と規模を確定する。
private尺度の事前登録、独立grading、実行側から秘密採点資産へのread拒否を実証する。
shared filesystemのnative subagentsでコードレビューしたことをblind trialの証拠にしない。

72 runsは旧設計の規模案で、今回の実行・費用承認ではない。生trace、private rubric、非公開業務dataは公開repoに置かない。
入力準備・合成testの成功を性能改善、比較完了、候補採用の証拠にしない。

設計: [旧pilot詳細設計](../../docs/design/012_COMPARATIVE_PILOT.md)、
[ダッシュボード契約](../../docs/design/012_DASHBOARD_DATA_CONTRACT.md)。
sanitize済みJSONは [ダッシュボード](../../docs/evaluation-dashboard.html) へlocal importできる。
描画/CSP/networkの実ブラウザ確認は引き続き未確認。
