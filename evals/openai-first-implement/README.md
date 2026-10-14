# implement比較pilot — 未実行の開発用入力

現行revision `ab32391c9612ad7983a4805040a6331ad5f576db` と限定lean候補を比較する準備。
**実測結果なし・候補未採用・現行pluginは無変更**。公開caseは合成の開発課題でhold-outではない。

## ファイル

- `baseline/`: 固定revisionからbyte単位で保存したimplementと参照依存
- `candidate/`: 評価用の限定candidate。配布pluginには含めない
- `cases.v1.json`: 既存case schemaに従う4群×3のpublic開発case、公開の判定観点
- `tasks/`, `fixtures/`: actorに渡す依頼と初期状態
- `preparation.v1.json`: actor入力のallowlistとSHA-256。開始前に固定し、変更は新version

`fixtures/docs/README.md.fixture` は意図的な壊れたリンクを持つ作業入力。
準備時に `.fixture` を外して `workspace/README.md` へ配置する。
repo自身の文書不具合と、修正対象の初期症状を混ぜない。

## 入力を準備する

repo外に、まだ存在しない出力先を選ぶ。例えば:

```sh
python scripts/comparison_bundle.py baseline small-fix-normal /tmp/actor-A-small-fix
python scripts/comparison_bundle.py candidate small-fix-normal /tmp/actor-B-small-fix
```

Windowsでは自身の一時directory下の絶対pathを指定する。
生成物は依頼・fixture・一方のskill treeとsource hashのみ。採点集合・重み・他条件は入れない。
`SOURCE.json` は `isolation_verified: false`、`trial_authorized: false` を明記する。
**別directoryへの出力だけではアクセス隔離にならない**。本scriptはrunnerではなく、modelも起動しない。

actor開始directory・instruction発見方法をharnessで固定する。
`.agents/skills`はbundle root、作業対象は`workspace/`、依頼は`task.md`。
observerは依頼から完了/正当な停止までのtool・変更・test/runtime・質問時点を記録し、
最初の応答だけを成果として評価しない。記録先は非公開でrepo外。

## 実比較前に残る条件

正式model/取得可能なsnapshot、effort、tools/権限、fixture、context/token/time/cost上限と実行規模、
private方法の事前登録、独立評者、実行側から採点資産を読めないことの拒否試験。
これらが揃わない入力準備や合成testは性能改善の証拠ではない。
72 runsは基本設計の規模案で、ここで起動・承認したことにはならない。

詳細: `docs/design/012_COMPARATIVE_PILOT.md` と
`docs/design/012_DASHBOARD_DATA_CONTRACT.md`（repo rootからのpath）。
実データ表示は `docs/evaluation-dashboard.html` にsanitize済みJSONをlocal importする。
公開repoにはraw trace、private rubric、非公開業務dataを保存しない。

## 実行開始時の履歴固定

現在のbaseline/task/fixture/preparationは未実行の開発資産で、`snapshots/`外にあるため
既存append-only validatorの保護対象ではない。実比較前には実際に発行するmanifestと全入力を
既存のimmutable snapshots方式へ保存し、source/hashと登録条件を照合する。
開発中のhash照合成功を、試験開始後の履歴保護済みという意味にしない。
