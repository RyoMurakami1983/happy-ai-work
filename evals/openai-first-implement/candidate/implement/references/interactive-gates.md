# Runtime evidenceとHITL review gate

interactive sliceだけで使う。bootstrapで実行入口を見つけることと、実際のruntime検証は別。

## Runtime evidence

受入に必要なlive runtimeの表示・操作・状態を、同じbuildのlaunch commandで実際に確認する。対応templateだけを読む。

- web: [Playwright](runtime-evidence/playwright.md)
- Windows desktop: [FlaUI](runtime-evidence/flaui.md)
- Python GUI / pygame: [Python GUI](runtime-evidence/python-gui.md)

環境・権限で起動や観測ができなければ、具体的blockerと未確認範囲をgateへevidence gapとして渡す。build/test成功だけで`runtime verified`や`PASS`にしない。

比較用interactive pilotのときだけ[comparable harness contract](interactive-app-comparable-harness-contract.md)を読む。通常の製品開発に比較用seed・state dump・commandを一律追加しない。

## HITL contractとreview milestone

planでHITL review contractが指定されたsliceでは、実装前のslice contractにreviewable milestone、launch方法、代表操作、期待結果、再開条件を固定する。人間の主観判断・実端末・外部app確認を自動testで代替しない。

自動gateを通過し利用者が直接触れられる状態になったら、そのsliceをreview milestoneとして渡す。

- 同じbuildを起動するcommandまたは手順
- 利用者が行う1〜5個の代表操作と、それぞれの期待表示・状態遷移・操作感
- 自動確認済みの範囲と人間の判断が残る範囲
- feedback受領、承認、または`REPLAN_REQUIRED`となる再開条件

`code complete`、`runtime verified`、`user validated`を区別する。自動runtime evidenceだけでは`user validated`としない。

- HITLがacceptanceに含まれる: 自動gate通過後も`HITL pending`。feedbackまたは承認までsliceの`PASS`・completion handoffを保留する。
- HITLがacceptanceをブロックしない完成後の探索的製品評価: `user validated`未完了と残件を明記してローカル実装を閉じられる。
- HITL review contractがなく、自動runtime evidenceで受入が確定する: 利用者入力を待つためだけに止めない。

feedbackが不具合なら再現loopを作れる場合は`debug-and-fix`、contractの誤りなら前段へ戻す。戻り先が未導入なら、再現条件または必要な判断と再開条件を返す。
