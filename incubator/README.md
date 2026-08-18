# Incubator

まだpluginとして配布しないworkflowやskill候補を、実利用で価値を確認するための領域です。

## ルール

- `plugins/*/skills/`へ置く前の仮説、利用scenario、観測結果だけを扱う。
- ここに完成品を装った`SKILL.md`を置かない。自動検出や配布対象と誤解させないためです。
- marketplace、plugin manifest、READMEの公開skill一覧から参照しない。
- 実際の反復利用、独立したtrigger、既存skillでは代替できない理由が揃ったらpluginへ昇格する。
- 利用されない候補は保持し続けず、削除または通常docsへ戻す。
- secret、個人data、実案件の未加工artifactを保存しない。

## 現在の候補

- writing deliverables: slide、report等を含む成果物作成は、旧`pptx`を移植せず、新しいwriting workflowとして利用scenarioから設計する。

`safe-refactor`は`implement`のreference、`knowledge-capture`は現時点では既存workflowや外部knowledge pluginで代替できるため、incubator候補にも置きません。
