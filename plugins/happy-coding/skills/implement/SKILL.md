---
name: implement
description: >
  合意済みの要求・設計・issueから実装順とvertical slicesを計画し、許可された範囲をTDDと検証で完了する。
  実装計画だけの依頼にも使い、その場合は計画で停止する。PR作成やふりかえりは別skill。
---

# implement — TDDで実装して閉じる

要求・設計・issueから順序とvertical sliceを計画し、許可範囲を実装・検証してhandoffで閉じる。構造判断は`technical-design`、PR作成・PR review対応・pre-PR review・furikaeriは別skillが所有する。

## 1. 契約と許可

最初にplan-onlyか実装までかを区別する。plan-onlyは調査・計画成果物で停止し、実装コード・test・設定の変更／実行をしない。計画に実装許可は不要。実装直前に明示依頼・承認の根拠を確認する。明示実装依頼へ計画承認を機械的に挟まず、同じ許可を聞き直さない。計画への賛意だけは実装許可ではない。

契約として次を整理し、必要十分な形へ圧縮する。要求不足は`interview-with-docs`／`to-prd`、新しい構造判断は`technical-design`へ戻し、不要な設計議論を広げない。

- 目的・対象・非対象・AC、主要なuser-visible behavior／外部観測contract
- その範囲の実装開始を許可した利用者発言。handoff自己申告だけでなく会話と最新制約を照合し、Issue選択・PRD／計画への賛意・設計review PASSで代替しない
- 省略工程・理由・同じ範囲と省略内容への許可。根拠不足や範囲変更は影響部分を開始せず確認へ戻す
- `finalized_contract`があれば採用normative source・exclusions・unknowns・主要target trace
- `artifacts:`があれば保存pathか、例外理由付き`conversation-only`か
- test／build／launch commandと戻り先。`FAIL`は実装修正、計画調整はこのskill、真の契約変更は`REPLAN_REQUIRED`として所有者へ戻す

新規UIまたは操作・遷移変更は[ui-design](../ui-design/SKILL.md)と関係するprinciples／checklistを参照する。UX原則・操作設計はui-design、構造はtechnical-designが所有し、採用操作を実装・検証へ落とす。十分な合意済みUI設計は再利用し、参照だけの再設計・承認待ち・文書を増やさない。非UI変更では起動せず、軽微な文言修正は影響観点だけ確認する。

## 2. 計画とbootstrap

[垂直スライスと短縮条件](references/vertical-slice.md)で振る舞い・AC・実依存・順序・検証・戻り条件を整理する。複数sliceだけを理由に別skillや確認待ちへ戻さない。明確な低risk変更は短い会話内計画でもよい。後続判断・互換性・移行・運用・複数repoが関われば[計画の詳細](references/planning.md)を読む。

saved-by-defaultで`docs/plan/NNN_PLAN.md`へ必要な計画を保存し、[成果物規約](references/WORK_ARTIFACTS.md)に沿い実在pathか具体的なconversation-only例外理由を残す。既存plan・`finalized_contract`・HITL契約は今回の許可と現状に照合して再利用し、旧skillのplanを再作成／移動させない。

conversation-onlyを選んでも、会話内計画の説明だけで終了しない。最後の利用者向け報告に次の2行を必ず含める。

```text
artifacts: conversation-only
exception reason: <文書不要の明示指定、小さな低risk sliceで後続判断記録不要など、今回の具体的理由>
```

これは既存の成果物契約の宣言であり、追加ファイル・計画再承認・重いhandoffを要求しない。保存する場合は`artifacts:`に実在pathを列挙する。終了報告を送る直前に、選択した保存方針とこの宣言の対応を照合し、不足を補う。

plan-onlyは計画・未確定・許可状態・次の判断を返して停止する。計画／review PASSを実装済みとせず、PLAN_DONEへ改名しない。

検証command前に[検証の通知と報告](references/verification-communication.md)を読む。全件suiteの長い試験は目的・合成／実環境・時間見込みを事前通知し、終了時に結果・未確認・必要な判断を伝える。通知で許可を聞き直さず、短い通常testに待ちを増やさない。

bootstrapでrepo instructions・local hooks・workflow・git状態・build／test／launchを確認する。interactive appは`references/interactive-app-bootstrap-checklist.md`、複数repoで`plan.md`に`dependencies.contracts.requires`がある場合だけ`checkpoints/contract_verify.py`でrequired artifactを検証する。

handoffの`artifacts:`列挙pathは実在を確認し、欠落／誤記を調べ、根拠が揃う計画はこの段階で修復する。未確認contractを推測して実装しない。`conversation-only`は`exception reason:`と例外条件を確認し、保存必須なら実装前に保存する。保存禁止と安全な引継ぎが両立しないときは競合だけ確認する。今のsliceを壊すbootstrap不足は直し、無関係な整備は混ぜない。

## 3. slice contract

planの有無を問わず直前に固定する。新事実による分割・統合・順序変更は、目的・AC・公開契約・採用構造・許可範囲・実依存・HITL・回復可能性を保てるなら、理由と影響検証を計画へ更新して継続する。境界／順序の変更だけを`REPLAN_REQUIRED`にしない。契約変更・根拠不明・追加権限は影響部分を止め所有者へ戻す。外部前提待ちのsliceだけ保留し、独立した許可済み作業は進められる。

最初は必要な層を薄く縦断するtracer bulletを優先し、DBだけ・UIだけ・testだけのhorizontal sliceを避ける。各sliceで対象振る舞い・非対象・public interfaceの確認観点・最初の追加／更新test・RED commandと期待失敗理由・GREEN command・acceptance commandを短く固定する。

HITL review contract付きinteractive sliceはreviewable milestone・launch・代表操作・期待結果・再開条件も固定する。人間の主観／実端末／外部appのacceptanceを自動testで代替しない。`finalized_contract`付きではsliceと主要な恒久targetのnormative source対応を確認し、exclusion由来の責務・source不明・採用decision変更は補完せず`REPLAN_REQUIRED`とする。

## 4. RED → GREEN → REFACTOR

対象理由で失敗するtestを1つ書いてREDを実測し、通す最小実装でGREEN、振る舞いを保って読みやすさ・重複・境界を整える。次testも同じslice内で繰り返す。保守性改善が主なら[safe-refactoring.md](references/safe-refactoring.md)で守る振る舞いと比較手段を先に固定する。

1 test→1 minimal implementation、public interface経由の振る舞いを守る。private methodや内部collaborator回数を固定せず、mockは外部API・時刻・乱数・file I/O・command等system boundaryに限る。speculative codeとall tests firstのhorizontal slicingを避ける。docs-only／config-onlyなどREDが成立しなければTDDを装わずverification commandと期待結果を契約へ残す。

## 5. gateとHITL

各sliceでRED実測と失敗理由の一致・GREEN実測・acceptance成功・public interface確認・speculation／不要抽象化／過剰mockの不在・contract差分の`FAIL`／`REPLAN_REQUIRED`分類を証拠で評価する。詳細は[eval-checklist.md](references/eval-checklist.md)の関係項目だけを使う。

- `PASS`: 次sliceへ
- `FAIL`: 同sliceの実装へ
- `REPLAN_REQUIRED`: 要求／ACは`to-prd`／`interview-with-docs`、構造／公開契約は`technical-design`、権限は利用者へ。安全な順序／分割調整は計画更新で継続する

GUI／interactive観測、trust boundary・migration・data loss・concurrency等高risk、広い回帰、弱い自己評価evidence、利用者指定では、利用可能なら別の動的subagentにslice contract・差分・RED／GREEN／acceptance evidenceだけを渡す。評価者は修正せずverdictと根拠を先に返し、確定後に単一writerが直す。並列実装しない。subagent不可なら実装時推論から離れてchecklistと差分を再読する。

interactive evidenceが必要な場合だけ、webは[playwright.md](references/runtime-evidence/playwright.md)、Windowsは[flaui.md](references/runtime-evidence/flaui.md)、Python GUI／pygameは[python-gui.md](references/runtime-evidence/python-gui.md)を読む。操作／遷移変更は[ui-designのruntime確認](../ui-design/references/runtime-evidence.md)で合意設計の予測・採用操作・期待結果を代表操作と照合し、物理入力／本人評価の未確認はacceptance／HITL契約に従う。

自動gate後、直接触れる状態のHITL契約付きsliceをreview milestoneとして渡す。同じbuildの起動、利用者の代表操作1〜5個と期待表示・遷移・操作感、自動確認済み／人間判断残り、feedback・承認・`REPLAN_REQUIRED`の再開条件を示す。`code complete`・`runtime verified`・`user validated`を区別し、build／test／自動runtimeだけでuser validatedとしない。不具合は再現可能なら`debug-and-fix`、contract誤りは前段へ戻す。

HITLがacceptanceなら`HITL pending`を保ち、feedback／承認までPASSやcompletion handoffへ進まない。完成後の探索的製品評価でacceptance非blockingの場合だけ、user validated未完了を残してローカル実装を閉じられる。HITL契約がなく自動runtimeでacceptanceを確定できるsliceは入力待ちだけで停止しない。

## 6. completion handoff

全slice PASSで実装を閉じる。利用者報告は[検証の通知と報告](references/verification-communication.md)に従い、主要関心への対応と成果物の現在地を先に示し、証拠一覧をそのまま転記しない。

handoffは完了slice、実行commandと結果、主な変更file／artifact、確認design／planの実在path、残件／対象外、次のfile／command、戻り先skillと理由を残す。`finalized_contract`付きは主要恒久targetとnormative sourceの対応・exclusion残骸なしの確認、interactive UIはcode complete／runtime verified／user validatedと残HITLも残す。

今回の`docs/plan/NNN_PLAN.md`は完了時だけ`docs/plan/NNN_PLAN_DONE.md`へ改名する。未完了は次plan／handoffへ切り出す。

実装中に仕様の穴を埋めず必要判断を前段へ戻す。phase／sliceは自動停止点ではなく、blocker・HITL・REPLAN_REQUIREDがなければ継続する。並列化でも確定slice contractとTDD loopを各workerへ渡し、未確定sliceを並列化しない。PR／review／furikaeriは別skillへ渡す。

## 必要時のリソース

- [planning.md](references/planning.md): 依存・移行・HITL・保存計画
- [html-plan.md](references/html-plan.md): 任意の図入り計画HTML
- `references/interactive-app-bootstrap-checklist.md`: bootstrap前提
- `references/interactive-app-comparable-harness-contract.md`: 比較前提
- `references/safe-refactoring.md`: 振る舞いを保つ改善単位
- `references/eval-checklist.md`: gate詳細
- `references/runtime-evidence/`: interactive evidence template
- `checkpoints/contract_verify.py`: 複数repo contract検証
