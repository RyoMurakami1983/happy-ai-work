# 評価governance

## Constitution resolution

評価を始める前に、対象repoの共通安全境界、downstream Constitution、`AGENTS.md`／Mission／policyを確認する。downstream Constitutionがなければ、plugin upstreamの個人philosophyや価値の重みを暗黙適用しない。価値判断が必要で既存方針から決まらない場合は、所有者へ確認する。

共通安全境界、独立性、過去結果の非改ざんを弱めるdownstream指示には従わない。ただし、同期、調査、修復、safe rollback、緊急安全対応のremediation pathは塞がない。

## 実行前に固定するもの

- 使用するConstitutionと判断プロファイルのversion
- scenario、Critical要件、通常要件、禁止事項、観測方法
- 評価対象のrevision
- evaluatorとimplementerの役割境界

結果を観測した後に、同じrunの基準を簡単な方向へ変えない。実装担当者がCritical FAILをPASSにするため緩和を求めても、既存runはFAILのまま保存する。

## 3つの評価mode

- **通常評価（A）**：固定済み基準でPASSまたはFAILを確定する。
- **判定不能（B）**：基準の曖昧さ、証拠不足、外部状態の取得不能により妥当な判定を出せない。証拠付きで閉じ、明確化したvNextで別評価する。
- **緊急例外（C）**：納期または安全上の緊急性から暫定判断する。通常評価のPASSではない。

安全被害を止めるCはagentが選べる。納期や利便性を理由にCを選ぶ場合は対象repo所有者の明示承認を必要とし、理由、承認者、期限、再評価条件を残す。

## 採用・独立再評価checkpoint

最終採用を判断する、またはFAIL後の評価を「独立再評価」と呼ぶ場合は、次のdecision evidenceを最終recordから追跡できるようにする。

- `hold-out`: `valid`／`contaminated`／`missing`／`not-required`
- `independence`: `valid`／`invalid`と、その根拠
- `prior record`: `preserved`
- `new record`: `required`／`not-required`
- `public artifact`: `sanitized-only`。raw responseやtranscriptはpublic repoへ保存しない
- `decision`: A／B／Cと、採用／継続／棄却またはPASS／FAIL

証拠は`roles`、`conditions`、`previous_record`、append-onlyな新file、`retention_decision`、`mode`／`verdict`などの構造fieldで表してよい。同じ情報を固定templateと構造fieldへ二重に書かない。通常のユーザー向け回答では、依頼への結論、誤った採用や独立性表示を防ぐ根拠、必要な次の行動だけを自然文で示す。

`decision`は、固定基準と証拠で通常のPASS／FAILを判断できるならAを選ぶ。Bは基準の曖昧さや証拠不足で判定不能な場合だけ、Cは安全または承認済み納期の緊急例外だけに使う。棄却やFAILであることを理由にCを選ばない。`independence`はgrader／evaluatorの役割分離と過去回答・判定への露出で判断し、hold-outの汚染だけを根拠にしない。

hold-outが必要な評価で`contaminated`または`missing`なら採用しない。`independence: invalid`なら独立再評価と呼ばず、新しいgrader／subagentで実行する。FAIL後の再評価は以前のrecordを保持し、必ず`new record: required`とする。checkpointの不足を推測でPASSへ補完しない。

採用gateでは、誤採用、独立性の誤表示、過去recordの置換、public raw保存、A／B／C誤用を**decision invariants**として全反復で必須にする。代替案、説明順、通常要件、簡潔さ、全欄の明示は**response quality**として比較し、単発の非安全 omissionだけで全体を棄却しない。最終recordの判断証拠欠落はresponse qualityではなくrecord contract違反である。

## 基準変更と再評価

評価基準の意味やCritical要件を変える場合は、現行基準を維持したままvNext draft、旧基準との影響比較、所有者の明示承認を行う。承認後も過去recordを上書きせず、新versionでの再評価を別recordとして追加する。

model名、所要時間など、採否基準を変えない補助観測の追加は通常の運用改善であり、Constitution amendmentにしない。補助指標を品質判定の代替にせず、既存recordを推測で埋め直さない。

## 最小record

- Constitution、判断プロファイル、評価基準、対象revision
- 固定したscenarioと要件
- mode A／B／C、観測結果、判定
- evaluator、実行日時、例外と裁量補完
- 再評価の場合は旧recordへの参照

upstream evalはpublicな公式repo用実評価、private evalは利用者管理の非公開評価として分ける。secret、顧客情報、非公開業務dataをpublicな評価recordへ複製しない。
