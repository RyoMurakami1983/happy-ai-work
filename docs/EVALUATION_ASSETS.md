# Evaluation assets

このrepoの公開評価資産は、公式`happy-ai-work`の改善を測る**upstream eval**と、個人philosophyに依存しない**共通安全eval**である。公開可能なcaseをprivate evalとは呼ばない。private evalは利用者または組織が自身の非公開領域で所有し、このrepoへraw data、scenario、rubric、期待結果、trace、履歴を取り込まない。

## 責務と所有者

| 責務 | 所有者 |
| --- | --- |
| Constitutionと安全・評価整合性 | `CONSTITUTION.md`のowner。意味や優先順位の変更はConstitution amendment |
| 判断プロファイル | profile owner。原則を変えない文脈依存の重みとanchor |
| 評価constitution | `CONSTITUTION.md`。独立性、実行前固定、過去record非改ざん、A／B／C |
| case、rubric、schema | 評価資産maintainer。意味変更はversionを上げ、過去版を残す |
| sealed候補の公開昇格 | repo owner。sanitize済み内容だけをupstream evalまたは共通安全evalへ昇格 |
| behavioral evaluationの実行 | generator。条件ごとに分離し、他条件、rubric、期待判定を受け取らない |
| AI grader／comparator | implementerとgeneratorから独立したblind grader |
| deterministic validator／policy test | repo CI。schema、path、field、明白なsecret patternを判定 |
| raw run | session workspaceの実行者。repoへ保存しない |
| sanitize済みrecord | `evals/records/`のappend-only file。再評価は別record |

## Public lifecycle

`candidate -> sealed -> promoted | retired | kept-private`

- sealed内容は実装担当者へ開示せず、session限定または利用者管理の非公開領域に置く。
- publicへ昇格するときはsanitizeし、`visibility: public`、`holdout: false`として新しいcase versionを保存する。以後は未見hold-outとして再利用しない。
- 廃止はfile削除や過去recordの書換えではなく、`status: retired`、置換先、理由を新versionへ残す。
- public caseからsealed hold-outを生成したとは扱わない。派生内容が実装担当者に推測可能ならhold-outではない。

## 保存境界

`evals/<target>/cases.vN.json`はversion付きcase、`evals/records/<record-id>.json`はsanitize済み比較record、`evals/schema/`は機械検証する契約である。各recordは対象revision、Constitution、判断プロファイル、評価基準、schema、condition hash、役割とagent ID、時刻、判定を持つ。

最終recordはhold-out状態と理由、role independenceと理由、prior recordの保持状態、artifact hash、sanitize retention、mode／verdictを構造fieldで持つ。adopted recordの汚染／欠落hold-out、invalid independence、mode C、sanitizeされていないpublic artifactはvalidatorで拒否する。

次は追跡しない: `runs/`、raw response、raw transcript、sealed hold-out、secret、PII、顧客情報、private code、非公開業務data、公開に不要なtraceやaccount／environment情報。validatorは明白な違反を拒否するが、機械検知だけで安全性を完全保証しない。

## 実行境界

評価前に仮説、反対仮説、caseとrubric、Critical、通常要件、禁止事項、threshold、最大iteration、condition内容またはhash、generator／grader役割、blind化方法を固定する。結果観測後に同じrunを容易な方向へ変えない。FAIL、判定不能B、緊急例外CをPASSへ読み替えず、vNextは別recordにする。

Codexでは固定agentや常設runnerを配布しない。必要な実行時だけ独立subagentを割り当て、deterministicな検証は`scripts/validate_evals.py`を使う。downstreamではupstream evalを既定適用せず、downstream Constitutionがなければ既存repo policyと共通安全境界だけを使う。

append-only検証はlocalのdirty worktreeに加え、CIではpull requestのbase、またはpush eventの`before` SHAからHEADまでのtracked diffも確認する。新file追加は許可し、既存のcase version、schema、recordの変更・削除・rename・type changeを拒否する。

## 採用gateの分離

評価資産層のdeterministicな効果と、skill instructionsのbehavior効果を一つの点数へ混ぜない。

- schema、禁止artifact、append-only、public hold-outなどはfixtureとvalidatorで判定する。
- trigger、判断、停止、handoffなどは独立したbehavioral evaluationで判定する。
- 一方のPASSを他方の代替にせず、各層の利益と保守コストを別々に採用判断する。

behavioral evaluationの内部でも、decision invariantsとresponse qualityを分ける。独立性の誤表示、過去recordの置換、汚染hold-outによる採用、public raw保存、A／B／C誤用は禁止またはhard failureとして全反復で止める。代替案、説明順、通常要件、簡潔さなどはcoverageと残存riskとして比較し、単発の非安全 omissionだけで全体を棄却しない。

完全なdecision evidenceはsanitize済み最終recordが所有する。通常のユーザー向け回答へrecord内部の固定templateを強制せず、その場の結論、安全境界、必要な次の行動を示す。recordでは`roles`、`conditions`、`previous_record`、新しい`record_id`、`retention_decision`、`mode`／`verdict`へ証拠を構造化する。

recordの`artifact_hashes`はrepo内に存在する公開artifact pathとSHA-256を対応づけ、validatorが実体を照合する。baselineが現行treeに存在しないinstruction variantなら、意味要約だけで再現可能と主張せず、実際にgeneratorへ渡した公開instruction snapshotをpilot manifestとともに保持する。
