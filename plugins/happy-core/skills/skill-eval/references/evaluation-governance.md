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
