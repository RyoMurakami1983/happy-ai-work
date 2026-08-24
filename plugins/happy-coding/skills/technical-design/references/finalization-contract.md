# Finalization contract

複数案を比較した設計や、途中で採用決定が変わった設計から、恒久成果物へ何を昇格するかを確定するための条件付きcontractです。議論を消す手順ではなく、decision historyと実行時の規範入力を分離します。

## 適用条件

次のいずれかに該当するときに使います。

- 複数の実質的な代替案を比較した
- planやtest案を作った後で採用決定が変わった
- 案固有のlocator、責務、抽象化、validation、test seamが恒久成果物へ入り得る
- AGENTS.md、SKILL.md、reference等の長期的なinstructionを設計判断から更新する

比較案のない局所修正、typo、既存contract内のsmall one-sliceには要求しません。

## 分類

### Normative

後続工程が実装根拠として使えるものです。

- 合意済みAcceptance Criteria
- 採用済みdecision
- 既存の恒久repo規約
- 採用案から独立して必要な外部contractまたは安全invariant

候補として詳しく議論されたこと自体は根拠になりません。非採用案で初出したconstraintでも、採用案に独立して必要なら既存policy等へ再根拠付けして残します。

### Decision history

採用、非採用、保留、supersededと理由です。将来の再議論防止に価値がある場合だけdesign／ADRへ残します。実装handoff、AGENTS.md、SKILL.md、reference、testへ規範として再展開しません。

### Non-goals / Unknowns

Non-goalは今回のscope外であり、別途採用されない限り恒久的な禁止ではありません。Unknownは決定事項へ混ぜず、実装を左右するなら前段へ戻します。

## Promotion gate

恒久成果物へ追加する主要な規範ごとに確認します。

1. この議論を知らない読者にも必要か。
2. Acceptance Criteria、採用decision、既存repo規約、外部／安全invariantのどれに根拠があるか。
3. repo全体の常時規約、skill workflow、条件付きreference、利用者向け説明、実装、test、decision historyのどこへ置くべきか。
4. 非採用案固有の文言だけでなく、責務、抽象化、branch、mock、test seamが残っていないか。
5. 最小化によって採用済みconstraintまで欠落していないか。

行単位のID付与は強制しません。sliceと主要な恒久targetからsourceを追える粒度にします。AGENTS.md、SKILL.md、reference等のinstructionを更新する場合は、「この議論を知らない読者にも必要か」に対する理由を一行だけtarget traceへ添えます。

## Handoff

必要な案件では次の形を使えます。IDの名称より、sourceとstatusが曖昧でないことを優先します。

```yaml
finalized_contract:
  normative:
    - AC-1
    - DEC-REPO-LOCAL
    - POLICY-HOME-SAFETY
  exclusions:
    - id: ALT-WRAPPER
      status: rejected
    - id: NG-HOME-BOOTSTRAP
      status: non-goal
  unknowns: []
  target_traceability:
    plugins/example/SKILL.md:
      sources:
        - AC-1
        - DEC-REPO-LOCAL
      placement_reason: 議論を知らない実行者も採用済みworkflowを再現するため
  exclusion_policy:
    rejected: 別途negative requirementとして採用されない限り恒久禁止ではない
    non-goal: 今回のscope外であり恒久禁止ではない
```

`exclusions`は短い識別子、`rejected`／`non-goal`／`superseded`等のstatus、decision historyへのpointerだけを伝え、非採用案のlocatorや手順をhandoffへ複製しません。handoffでは`non-goal`が今回のscope外であって恒久禁止ではないこと、`rejected`も別途negative requirementとして採用されない限り禁止規約へ昇格しないことを短く明示します。normative sourceが確定できない、Unknownが実装を左右する、または決定が変わった場合は`implementation-plan`や`implement`へ進まず設計を再finalizeします。
