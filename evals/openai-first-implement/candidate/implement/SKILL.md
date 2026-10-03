---
name: implement
description: >
  実装契約を受け取り、bootstrap 確認、vertical slice 分割、TDD loop、slice gate、completion handoff まで進める。
  technical-design / implementation-plan / issue から実装可能な契約を受け取り、PR やふりかえりではなくローカル実装を完了したいとき。
---

# implement — 許可された実装を検証して閉じる

成果は、許可範囲のローカル変更、RED/GREENまたは正当な代替検証、受入結果、未確認点とhandoff。PR作成・PR review対応・pre-PR review・furikaeriは対象外。

## 開始と停止の契約

- 目的・対象・非対象、受け入れ条件、外から観測できる振る舞い、test / build / launch commandを確認する。実装中に未決の仕様を補完しない。
- その範囲の実装開始について、利用者の明示的な依頼・承認と根拠発言を、利用可能な会話・最新制約と照合する。handoffの自己申告、Issue選択、PRDや計画への賛意、設計レビューのPASSは実装許可の代わりにならない。
- 工程を省略したなら、工程・理由と同じ範囲・省略内容への許可を確認する。根拠不足や範囲変更があれば影響部分を開始せず確認へ戻す。取得済みの同じ許可は聞き直さない。
- `artifacts:` または `finalized_contract` がある場合は、開始前に[条件付き実装契約](references/task-contract.md)の該当節を読む。
- 要求不足は`interview-with-docs`、構造判断は`technical-design`、順序・分割は`implementation-plan`へ戻す。戻り先skillが未導入なら、不足・必要な判断・再開条件をhandoffし、判断を代行しない。

秘密・個人情報・利用者dataを必要なく公開・複製しない。破壊操作、外部公開、権限拡大は対象と影響・許可を確認し、最小権限と修復可能性を守る。実装許可を追加の外部操作の許可に広げない。評価基準は実行前に固定し、結果を見た緩和・過去recordの上書き・実装者だけによる採用判定をしない。利用先のinstructions・人間の所有権を尊重する。停止は違反する作業を止めることであり、許可済みの調査・修復・safe rollbackを妨げない。

## 実装ループ

### bootstrap

repo instructions、local hooks / workflow、Git状態、build / test / launch入口を確認し、今のsliceを壊す不足だけを依頼範囲内で補う。無関係な整備を混ぜない。

検証commandの前に[検証の通知と報告](references/verification-communication.md)を読む。長い試験を含む全件suite・負荷試験・実環境検証は目的、合成／実環境、所要時間の見込みを事前通知する。通知で承認済み作業を再確認せず、短い通常testに待ちを増やさない。

- interactive app: [bootstrap checklist](references/interactive-app-bootstrap-checklist.md)の該当stackと、[runtime / HITL gate](references/interactive-gates.md)を読む。
- 複数repoで`plan.md`の`dependencies.contracts.requires`がある場合だけ、[条件付き実装契約](references/task-contract.md)のrequired artifact検証を使う。

### slice contract → RED → GREEN → REFACTOR

planがあればslice境界を維持して直前にcontractを確認する。planを省略したなら[垂直スライスと短縮条件](references/vertical-slice.md)を読み、単一の明確な変更を一つの観測可能な振る舞いとして切る。正常・境界・失敗時の複数ACを同じsliceに含めてよい。境界変更や新たな構造判断は`REPLAN_REQUIRED`。最初は必要な層を薄く縦断するtracer bulletとし、局所文言修正に不要な層を足さない。

各sliceで、対象振る舞い、非対象、public interface経由の確認観点、最初のtest、RED commandと期待失敗理由、GREEN command、acceptance commandを短く固定する。

1. **RED**: 失敗するtestを一つ追加／更新し、実行した失敗理由が対象振る舞いと一致することを確認する。
2. **GREEN**: そのtestを通す最小実装だけを加える。
3. **REFACTOR**: 振る舞いを変えず整理し、再検証する。次のtestが必要なら同じslice内で繰り返す。

testはpublic interfaceの振る舞いを主語にし、private methodや内部collaboratorの呼出回数を固定しない。mockは外部API・時刻・乱数・ファイルI/O・コマンド実行等のsystem boundaryに限る。speculative codeや不要な抽象化、all tests first、DBだけ／UIだけ／testだけを横に広げるhorizontal slicingを避ける。

docs-only / config-onlyなどREDが成立しないsliceではTDDを装わず、verification commandと期待結果をcontractに明記して実行する。保守性改善が主目的なら、先に[振る舞い比較](references/safe-refactoring.md)を読む。

### slice gate → 次のslice

実際のREDとその理由、GREEN、refactor後の再検証、acceptance、public interfaceの観測、scopeと差分を証拠で確認する。RED不成立のsliceには代替verificationを使う。詳細が必要なら[eval checklist](references/eval-checklist.md)の関係項目だけを読む。

- `PASS`: contractと受入を満たしblockerがない。次のsliceへ進む。
- `FAIL`: contractは明確だが実装・証拠が不足。同じsliceを修正する。
- `REPLAN_REQUIRED`: 要求・構造・順序・slice境界・採用decisionの判断へ戻す。未決を実装で補わない。

GUI / interactive runtime観測、高risk（trust boundary、migration、data loss、concurrency等）、広い回帰範囲、弱い自己評価evidence、利用者指定のいずれかなら、利用可能な別の動的subagentにslice contract・差分・RED/GREEN/acceptance evidenceだけを渡して独立評価を依頼する。評価者は修正せずverdictと根拠を先に返す。評価中は並列実装せず、verdict確定後に単一writerが修正する。subagentが使えなければ実装時の推論から離れ、checklistと差分を読み直す。

interactive appは実際に起動・操作してruntime evidenceを残す。build/test成功をruntime検証や人間の主観・実端末・外部app確認の代替にしない。acceptanceにHITLが必要なら`HITL pending`のまま保持し、feedback／承認まで`PASS`やcompletion handoffに進めない。詳細は[runtime / HITL gate](references/interactive-gates.md)。

未確定sliceを並列化せず、各sliceのgate verdictを確定してから次へ進む。workerに分ける場合もslice contractとTDD loopを渡す。phase / sliceの区切り自体は停止点にせず、blocker・HITL判断・`REPLAN_REQUIRED`がなければ承認済み範囲を続ける。

## completion handoff

全sliceが`PASS`したら、完了slice、実行commandと結果、主な変更file / artifact、確認したdesign / planのpath、残件・非対象、次に開くfile／command、戻り先と理由を返す。`finalized_contract`があれば[source対応と残骸確認](references/task-contract.md)も残す。

interactive UIでは`code complete`、`runtime verified`、`user validated`を区別し、残るHITL gateを明記する。acceptanceをブロックしない完成後の探索的評価だけは、`user validated`未完了を残して閉じられる。HITL contractがなく自動runtime evidenceで受入を確定できるなら、入力待ちだけの停止を作らない。

今回のplanが`docs/plan/NNN_PLAN.md`なら完了時に`docs/plan/NNN_PLAN_DONE.md`へリネームする。未完了項目は次のplanかhandoffへ切り出し、今回の受入が未達なら完了扱いにしない。
