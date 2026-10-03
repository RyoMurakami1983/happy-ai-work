# 012 — 実装検証と実測の境界

Status: ローカル検証完了 / 2026-10-03。実比較は未実行、実測成績なし。

## 実装済み・個別確認

- 4群×3のpublic合成case、現行snapshot、限定implement候補、一条件の入力bundle
- 準備script: 7 tests PASS。12case×2条件すべての準備、改変hash、上書き、path逸脱、Windows名、衝突を検証
- 候補: 12 tests PASS。元の全Python helper保持、参照の可搬性、固定baselineとのbyte一致を確認
- 独立設計review: PASS（実装範囲）。実行予算の比較区間分離と負担内訳不足を修正後に再確認
- 独立static candidate/preparation review: PASS。行動評価の代替ではない

REDは準備API欠落、path/collision拒否不足、候補helper inventory不足で実際に観測し、
修正後のGREENを確認した。docs配置だけの検証をmodel/TDD効果の実測に読み替えない。

## ダッシュボードと全件gate

- JSON契約・Python/JavaScript parity・全割当分母・cohort・欠測・入力失敗保持を実装
- dashboard focused: 15 tests PASS。CLI出力はexclusive-createとし、元台帳/既存summaryの上書きを拒否
- 独立検証: 2,329 semantic probes、28 cohort変更、5 S非適格条件、DOM event/race/XSSの合成試験PASS
- 実ブラウザはChromium起動時のsocket権限制限、接続済みbrowserのlocal file URL制限で未実行
- 実レンダリング・実CSP/network動作・screenshotsは未確認。DOM合成試験で代替済みとはしない
- `uv run --script scripts/validate_quality.py`: Python3.14で全157 tests、repo validator、Ruff、ty、diff checkを確認
- 配布plugin/marketplace/versionは無変更。既存eval record/schema/historyは改変していない

## 実行環境の限定probe

新規model呼出し、課金API、credential作成・移送は行っていない。
既存Linux sandbox toolでuser/PID namespace内の無害なcommand起動は成功。
続く全namespace分離の無害なshell probeはnetwork namespace初期化で
`NETLINK_ROUTE socket: Operation not permitted`により失敗した。
制限の回避は行わない。この結果はmodel context、tools、logs、network、private採点資産の
end-to-end隔離が成立した証拠ではない。actorとしてnative shared-filesystem agentを使っていない。

## 未確認・開始前の条件

- 正式model/取得可能なsnapshot、effort、実行環境、token/time/cost上限、実行規模の確定
- private評価尺度/係数/anchorと依存作業遅延の事前登録、独立grader、hold-out管理
- actorから秘密資産へのread拒否、context/log/tool経由の漏洩防止の実証
- 実際の入力を既存immutable snapshots方式に固定
- public push/draft PRは公開承認まで保留、両OS CIも未実行
- 実利用の2件確認、約5件での方法見直しは未実施。件数稼ぎの課題は作らない

candidate採用・有効性・一般優位を主張しない。現行pluginとversionは変更していない。
