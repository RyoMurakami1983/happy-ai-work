# 短歌と俳句の参照組込み

Date: 2026-11-07 (UTC)
Status: 所有者承認済みの変更案。長期効果は未評価。

## 判断概要

実装・設計・Issueで目的と必要な情報を伝えやすくするため、3スキルから共通の`tanka-to-haiku`を参照する。元本文は変更・複製しない。設計資料は判断概要から詳細へ進める形にする。意味・契約の欠落と概要／詳細の不一致が主要riskであり、既存のAC・許可・検証・未知の扱いは維持する。

[評価Issue #73](https://github.com/RyoMurakami1983/happy-ai-work/issues/73)で継続追跡する。ハーネス・比較条件・記録方法・採否基準は今回の変更後に所有者と決める。実例評価を開始せず、効果を実証済みと扱わない。

## 根拠と範囲

所有者は2026-11-07に、`implement`、`technical-design`、`github-issue`への共通スキル参照、設計冒頭の判断概要、長期評価Issueの作成を承認した。実例評価とハーネスはこの変更完了後に詰めるとの指定を優先する。

| 配置 | 変更する判断と理由 |
| --- | --- |
| implement/SKILL.md | 計画・命名・処理・完了報告を整えるときに共通スキルを読む。AC・許可・証拠・振る舞いを保持するため |
| technical-design/SKILL.md | 目的と構造・説明に共通スキルを使い、概要と実装契約を同じ正本に置くため |
| technical-design/assets/technical-design.md | 新しい設計資料でも判断概要を生成できるようにするため |
| technical-design/references/html-design.md | HTML入口でも重要riskと未決事項を隠さないため |
| github-issue/SKILL.md | 困りごと・目的・期待結果を整えつつ、AC・証拠・非対象を残すため |

coding単独導入は維持し、happy-coreが未導入なら既存手順を続ける。自動インストール・導入待ちにしない。参照は利用環境で現在利用可能なスキルを読むもので、repo更新だけで利用者のインストールや既存会話へ自動反映されるとは扱わない。

## 検証と後続

今回の静的検証は参照先の実在、元本文の不変、既存契約の保持、概要と詳細の構成、repo品質契約を対象とする。文字列や静的検査の成功を読解・実装能力向上の証明にしない。[従来評価](018_SKILL_COMPRESSION_AND_TANKA_MIGRATION.md)の本文圧縮・成果物評価結果は変更しない。

happy-coreを0.5.1、happy-codingを0.7.2へ更新する。利用者PCのplugin更新、マージ、全スキルへの適用は今回の範囲外。効果に問題があれば今回の参照と表示構成の差分を戻せる。評価Issueは導入PRだけでは閉じない。

## リリース前の既存ブロッカー

2026-11-07の`validate_constitution.py --check-remote`は、`personal-philosophy`の未同期開始を2026-10-30T16:30:42Zと検出し、7日超の`restricted`を返した。現行規約に従い、動作変更を伴うrelease／mergeは同期の確認まで行わない。このPRはdraftで停止し、同期記録やConstitutionを都合よく更新しない。品質checkの成功とは別に扱う。
