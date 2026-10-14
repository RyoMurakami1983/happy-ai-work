# 条件付き実装契約

`artifacts:`、`finalized_contract`、複数repoのrequired artifactがある場合だけ、該当節を使う。目的・許可・TDD・停止条件はSKILL.mdの契約を維持する。

## 保存済みartifactまたはconversation-only

handoffの`artifacts:`が保存済みpathか、例外理由付きの`conversation-only`かを確認する。

- pathが列挙されているならrepo内に実在することをbootstrapで確認する。欠けていれば`REPLAN_REQUIRED`として`implementation-plan`へ戻す。
- `artifacts: conversation-only`には`exception reason:`が必要。利用者の明示指定、またはsmall one-sliceの例外条件を満たすか、[Work Artifacts](WORK_ARTIFACTS.md)で確認する。
- 複数repo、複数slice、public contract、long-lived structure、compatibility、migration / operationsへの影響がある場合は省略できない。違反するhandoffは`REPLAN_REQUIRED`。
- 保存省略と実装開始の許可は別。工程省略条件は[垂直スライスと短縮条件](vertical-slice.md)に従う。

保存構造は上記Work Artifacts、既存planの項目を確認するときは同梱の[PLAN template](../assets/NNN_PLAN_TEMPLATE.md)を参照する。実装のためだけに新しいplanを要求しない。

## finalized_contract

開始時に採用済みnormative source、exclusions、unknowns、主要target traceを確認する。slice直前には、そのsliceと追加する主要な恒久targetがどのsourceに対応するか確認する。

source不明、採用decision変更、実装を左右するUnknown、exclusion由来の新しい責務が必要なら、実装で穴埋めせず`REPLAN_REQUIRED`として該当する要求・設計・計画へ戻す。

gateとcompletion handoffには、追加した主要な恒久instruction・実装責務・testとnormative sourceの対応、およびexclusion由来の残骸がない確認結果を残す。非採用案の文言だけでなく、責務、抽象化、validation branch、mock、test seamも確認する。採用案にも必要なrepo規約・外部contract・安全invariantを、最小化の名目で削らない。

## 複数repoのrequired artifact

repo rootの`plan.md`に`dependencies.contracts.requires`がある場合だけ、同梱の[contract_verify.py](../checkpoints/contract_verify.py)の`verify_contracts(plan_dict, repo_root)`で検証する。これは人間向け`docs/plan/NNN_PLAN.md`とは別物。helperは既存と同じPyYAMLを使い、初回checksumを記録し、以後は内容一致を確認する。

required artifactの不足やchecksum不一致を無視してdependent sliceを開始しない。結果と理由を残し、artifact待ち／path確認か、前提変更として設計・計画へ戻すかを判断する。依存のないsliceや単一repoにこのcheckpointを追加しない。
