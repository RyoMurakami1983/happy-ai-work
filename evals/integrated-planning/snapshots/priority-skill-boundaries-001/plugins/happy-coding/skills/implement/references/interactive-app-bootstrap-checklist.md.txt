# Interactive App Bootstrap Checklist

この checklist は `implement` の bootstrap checkpoint（ステップ 2）で、対象sliceの実装・検証を妨げる不足だけを見つけるために使います。既存appでは実在する入口を再利用し、新規appでは採用stackと受け入れ条件に必要な入口を用意します。該当stackと比較pilotの節だけを読み、全stackの整備を要求しません。

## 1. Target repo の現状

- 対象pathに適用される `AGENTS.override.md` / `AGENTS.md` 等の有効なinstructionsと既存workflowを確認する
- build / test / launchの入口は対象repoのREADME、manifest、scripts、CIから特定する。存在しないtemplateや同期scriptを前提にしない
- 既存repoへinstructionsやtemplateを再配布しない。Codex向け初期化自体が依頼範囲なら、利用可能な `workspace-bootstrap` を使い、既存内容を保つ差分と承認の境界に従う
- Git管理状態を確認する。`git init`やhooks設定は今回の作業に必要かつ依頼範囲の場合だけ行い、未初期化だけをapp検証のblockerにしない

## 2. Common contract

- 対象sliceに必要な build / test / lint / launch の入口が repo に存在するか（該当しない入口は理由を明記）
- generator handoff で test command と runtime launch command を返せる入口があるか
- interactive app の受け入れ条件に「live runtime で何を確認するか」が書かれているか
- 選択した stack で、同じ条件を再実行できる build / test / launch command を返せるか
- interactive app の比較 pilot なら、minimum comparable harness contract を採用するか判断したか
  - deterministic seed または同等の固定シナリオ
  - 共通 state dump schema
  - 共通 command runner
- 対象sliceを妨げる不足は依頼範囲で補い、実行できない検証とその理由は handoff / eval に明記したか

## 3. TypeScript / web

- fresh scaffold に test runner があるか（例: Vitest）
- dev / build / test の command が固定されているか
- runtime evaluator が起動できる URL または launch command があるか
- UI state を観測できる最低限の入口（title, control, canvas, screen text など）があるか

## 4. Python / pygame

- `python -m unittest discover ...` または採用した test command が安定して動く import 契約になっているか
- app の entrypoint と runtime launch command が 1 つに固定されているか
- pure logic と GUI loop が分かれ、state を test か runtime evaluator から追えるか
- runtime evaluator が画面状態または state dump を観測する手段があるか

## 5. WPF / desktop

- `dotnet build` の入口が固定されているか
- core logic を確かめる test project / test command が存在するか
- desktop app の launch command が 1 つに固定されているか
- FlaUI などで window title / control / status text / restart 動線を観測できる見込みがあるか

## 6. 不足と完了の扱い

- 今のsliceに必要な不足だけを補う。無関係な設定、依存、template配布は追加しない
- launchや観測が環境・権限で阻まれる場合は、その具体的なblockerと未確認範囲をslice gateへevidence gapとして渡す。build/testの成功だけでruntime verifiedとはしない
- bootstrapでは、適用instructions、必要な検証入口、起動方法とlive runtimeの観測対象を確認する。新規appならこれらを最初のsliceで実行可能にする
- bootstrap確認はruntime検証そのものではない。slice gateで実際に起動し、受け入れ条件に対応する表示・操作・状態を観測する

## 7. Comparable harness contract for pilot

この節は **比較用 pilot** のときに使います。通常の製品開発で seed 固定を必須にする意図ではありません。

- 詳細な正本は `references/interactive-app-comparable-harness-contract.md`

- deterministic seed を固定するか、同等の固定シナリオを用意するか
  - 目的は next queue や初期状態の差で比較がぶれないようにすること
  - 乱数自体を本番仕様から取り除くことが目的ではない
- state dump の最低項目を揃えるか
  - board または同等の可視状態
  - active piece
  - next queue
  - hold state
  - score / level / lines
  - last action または step counter
- command runner の最低 command を揃えるか
  - start
  - pause
  - left / right
  - rotate
  - soft-drop / hard-drop
  - hold
  - restart
