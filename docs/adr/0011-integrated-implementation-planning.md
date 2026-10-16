# ADR 0011: implement内の計画と旧plan skillのアーカイブ

## 決定

利用者の2026-10-16の依頼に基づき、`implementation-plan`を通常配布から外し、実装に必要な順序・slice・検証の計画を`implement`へ統合する。構造判断は`technical-design`に維持する。別skillへの往復と実行中の計画調整を分けるための責務変更であり、速度・token・品質の改善は未測定である。

計画だけの依頼では実装を開始しない。実装まで許可された場合は、目的・AC・公開契約・採用済み構造・許可範囲・実依存・HITL・回復条件を維持した順序や分割の変更を同じskillで進める。真の契約変更・追加権限は該当所有者へ戻す。

短い低risk計画は会話内で足りる場合がある。複数sliceという数だけで保存や停止を強制しない。互換性・移行・運用・複数repo・後続判断が関わる計画は引き続き保存し、HTMLは任意の読解用表示とする。

## 移行と互換性

- 旧skill一式を[archive](../../archive/implementation-plan/)へ保存する。entrypointは`SKILL.md.txt`へ変更し、pluginやskillとして探索・配布しない。snapshot manifestで元の内容を検証できる
- 現行の計画reference・template・HTML generatorと例はimplementへ移管する。生成器の形式・保存先・既存planの意味は変えない
- 既存の`docs/plan/NNN_PLAN.md`、`finalized_contract`、HITL、別形式のfleet `plan.md`とcontract verifierを引き続き受け取る
- 過去のdesign、ADR、評価snapshot/historyは当時の判断の証拠として残す。過去のskill名を現行invocationとはみなさない。ADR 0003の計画段階のfinalized contract consumer責務はimplementが継承する
- plugin更新はrepo配布定義だけ。既存PCのhome設定、cacheや手動copyを無断更新・削除しない。利用先更新は別途行う

## 検証範囲

配布対象、移管後generator、archive hash、現行リンクの自動検証に加え、計画のみ、承認済み複数slice、順序変更、真の契約変更、移行回復、外部依存、旧planの独立scenario reviewを行う。文言検査だけを実モデルの実装成功率や速度の証拠と扱わない。
