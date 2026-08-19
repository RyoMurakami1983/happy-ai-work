---
name: happy-add-issue
description: Happy AI Workの利用中に生じた軽い違和感や未成熟なfeedbackを、固定の母艦repo `RyoMurakami1983/happy-ai-work` へ低摩擦で安全にIssue化する。対象とAcceptance Criteriaが明確な実装backlogには使わない。
---

# Happy Add Issue

Happy AI Workへの軽いfeedbackを失わず、母艦repoで後から具体化できるIssueにする。投稿先は`RyoMurakami1983/happy-ai-work`に固定する。

## ワークフロー

1. どのskill、plugin、docs、Hooks、導線で困ったかと、どう変わってほしいかを一文ずつにする。
2. 既存Issueを読み取り専用で検索し、重複なら新規作成せず接続案を示す。
3. 公開Issueへ書けないprivate repo名、顧客名、内部URL、秘密情報、固有の業務dataを除外または匿名化する。
4. 必要な場合だけ背景、具体例、期待する改善を補う。未成熟なfeedbackへ重い仕様や実装方法を捏造しない。
5. 作成前に、固定投稿先、公開範囲、title、body、既存label候補をpreviewし、ユーザーの確認を得る。
6. 利用可能なGitHub connectorを優先し、必要なら`gh`を使う。どちらも使えなければ投稿可能なdraftを返す。
7. 作成後はIssue URLと、必要ならNotionの次のタスクへ置く一歩を返す。

## 最小形

```markdown
## 背景
- どこで気づいたか

## 困りごと
- 何が分かりづらい／使いにくいか

## こう変わってほしい
- 期待する改善
```

現在作業しているrepoの具体的なバグや後続作業は`github-issue`へ渡す。`happy-ai-work` repo内でも、対象とAcceptance Criteriaが明確な実装backlogは`github-issue`を使う。
