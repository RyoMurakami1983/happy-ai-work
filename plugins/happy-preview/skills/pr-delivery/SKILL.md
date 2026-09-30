---
name: pr-delivery
description: 「マージして」「merge PR」という対象PRの明示依頼、またはマージ済みPRの「マージ後整理」を受け、最新checks・マージ結果・base同期・安全な対象branch/worktree整理・結果報告まで進める試用skill。PR作成、review、CI監視だけの依頼ではマージしない。
---

# PR Delivery

明示された対象PRをマージし、その作業を安全に閉じる。実利用検証中のpreviewであり、自然文からの自動選択を保証しない。

## 対象と許可

- 会話の最新依頼と制約からrepo・PR・base/head・今回のマージ許可を確定する。対象が一意なら取得済みの許可を聞き直さない。対象不明、マージ禁止、未承認の判断が残る部分だけ確認する。
- 「マージして」はそのPRのマージ後のbase同期と安全な対象branch・専用worktree整理までを通常の終了条件とする。利用者が「branchを残す」「マージだけ」等と範囲を限定したら優先する。マージ済みPRの整理依頼は再マージせず整理から進める。
- skillの選択、PR作成・review・CI成功、過去の別PRの許可をマージ許可にしない。手順はtoolやplatformの権限を増やさない。承認レビューやアクセス制約を迂回せず、拒否された操作は停止し、許可された他の作業だけ進める。
- 自動マージ設定、認証、課金、security設定を変更しない。実行に必要なら該当部分を保留して影響を伝える。

## マージ

1. repo instructionsと実在するmerge policyを読み、指定された方式を使う。指定がなければrepoの設定・運用を確認し、方式が判断できない場合だけ尋ねる。特定方式を全repoへ固定しない。
2. 最新PR state・base/head SHA・checks・review/inline threads・競合を確認する。古いheadの成功を代用しない。必須check失敗・未完了、未解決の重大指摘、競合があればマージせず理由を伝える。修正も依頼範囲なら必要最小限で修正・再検証してから最新headで再確認する。
3. 明示マージ依頼があり必要な場合だけdraftを解除し、確認したheadに限定してマージする（対応toolのexpected head / match-head指定等）。実行直前にheadが変わったらchecksを再取得する。force mergeやcheck回避はしない。非同期でmerge待ちになっただけなら完了と報告しない。
4. PRのMERGED状態、merge SHA、実際に取り込まれたheadを取得し、対象baseのリモート履歴にmerge SHAが含まれることを確認する。確認不能なら削除へ進めず未確認を報告する。

## Base同期と対象だけの整理

マージの成功と整理の成功を分け、各操作の直前に状態を確認する。

1. local repo、全worktreeの所在・使用branch、対象head/baseの追跡先とtip、未コミット・未追跡・未push変更を確認する。無視されたfileもcache以外の利用者dataや別作業がないか確認する。PR headがdefault/base/shared branchの場合や、fork・他者所有branchを自分の作業branchとして削除しない。
2. 対象remoteからbaseをfetchし、既存base worktreeがcleanで履歴がfast-forward可能な場合だけ同期する。baseが未作成なら安全に作成できるか確認する。dirty・分岐・他作業中なら変更を保護し、reset/stashやcheckoutの強制で揃えない。同期のブロックが他の整理まで必ず止めるとは限らないが、各削除条件を独立して証明する。
3. 削除対象のremote名・repo・branch名・local branch・worktreeの絶対pathを固定する。現在のtipが確認済みPR headと一致し、未push・未統合の追加commitがないことを確認する。squash/rebaseでは単なるancestor判定に頼らずPRのMERGED情報とmerge/base履歴も照合する。証明できない対象は残す。
4. 専用worktreeは他の実行・別作業で使われておらず、未保存・未追跡data・未push・未統合変更がない場合だけ、worktree外から通常の`git worktree remove`で除去する。別worktreeの利用中branchを外すためにworktreeを消さない。
5. remote branchは上記条件を満たす自分の対象branchだけ、確認済みSHAを削除操作の条件にして削除する。直前の読取だけでは競合を防げない。force系optionを使わない比較条件付きAPIでtip変更時の拒否を保証し、保証できないtoolではremote branchを保持する。無条件deleteやforce系optionで代替しない。local branchは他worktreeで使われていないことを再確認し、通常の`git branch -d`で削除する。squash等で`-d`が拒否する場合も`-D`で押し切らず、local branchを保持して理由を報告する。強制削除、破壊的reset、全branch一括削除・広範なworktree pruneはしない。
6. 実際のremote/local branch不在、worktree登録とpathの除去、local baseとremote baseのSHA・clean状態を確認する。途中失敗で成功した操作を巻き戻すための再マージはせず、残る対象と理由を示す。

## 終了報告

PRのmerge状態・SHA、base同期結果、削除した対象、保持した対象と理由、未確認・残る判断を必要十分に伝える。マージ済み／整理完了／一部保持を区別する。判断事項がなければ追加質問をしない。
