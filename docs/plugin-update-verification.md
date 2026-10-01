# plugin更新の確認

Refs [#48](https://github.com/RyoMurakami1983/happy-ai-work/issues/48)。repo更新、marketplace更新、導入済み内容、実home、新しい会話の読込を別々に記録する。version変更だけでcache刷新や読込成功とは判定しない。

## 配布version

内容が変わったpluginは、次の配布でmanifestの数値versionを上げる。同じversionを異なる配布内容へ再利用せず、build metadataの日付だけに識別を頼らない。修正はpatch、後方互換のskill追加はminorを目安に、各pluginを個別判断する。manifestと変更を同じcommitに含め、PRで配布対象のfull commit SHAとversionを対応づける。commit自身のSHAをmanifestへ埋め込まない。

今回の配布識別は次のとおり。skillの振る舞いは変更しない。

| plugin | 旧version | 今回 |
| --- | --- | --- |
| happy-core | 0.2.0+codex.20260822145828 | 0.2.1 |
| happy-coding | 0.4.0+codex.20260824000000 | 0.4.1 |
| happy-preview | 0.2.0 | 0.3.0 |

core/codingは既存skill修正、previewはpr-delivery等の追加を識別する。今後の変更では上表を期待値として使い回さず、対象commitのmanifestを正本にする。

## PRでversionの上げ忘れを自動検出する

`quality` CIはPRの作成・更新時に`validate_plugin_versions.py`を自動実行する。開発者が確認commandを実行し忘れても、配布内容を変更してversionを据え置いたPRは検査が失敗する。PRタイトルには依存しない。

- 対象: `plugins/<name>/`配下の全tracked file。SKILL.md、reference文書、plugin内README、script、agent設定、asset、manifestの変更・追加・削除・移動を含む
- 対象外: repo直下README、`docs/`などplugin外だけの変更
- 既存plugin: manifestの数値`MAJOR.MINOR.PATCH`をPR baseより増やす。`+metadata`だけの変更、据置、減少は失敗。比較は文字列順ではなく数値順。現行配布形式に合わせ、このgateではprerelease suffixを扱わない
- 新規plugin: directory名とmanifest名の一致、有効な数値versionを必須にする。比較元のない新規identityとして扱う
- 全削除: 廃止としてversion増加は不要。catalogとの整合は既存repo validatorで確認する。fileが残るのにmanifestだけない状態は失敗
- 移動: file renameを追加・削除として比較し、移動元・移動先の存続pluginを両方確認する。plugin directoryのrenameでmanifest名を据え置くと失敗。名前も変える場合は旧identityの廃止＋新identityの追加としてreviewする

PR固有の変更はbase/headの共通祖先からheadまでで求め、versionの期待値は現在のPR base commitから取得する。これによりbase側だけの変更をPRの変更に数えず、古いbranchでbase以下のversionを再利用することも防ぐ。GitHubの仮merge commitや作業中fileではなく、eventが渡すbase/head SHAを使う。履歴不足や参照不明は失敗にする。

ローカルでもcommit済み変更を比較できる:

```powershell
python scripts/validate_plugin_versions.py --base origin/main --head HEAD
```

これは配布側の上げ忘れを検出する検査で、利用者のPCを調べたりpluginを更新したりはしない。CI失敗をmerge禁止にするにはrepositoryのrequired checks設定も必要で、この変更では設定を変更しない。導入済み内容の更新忘れは以下の手順で別に確認する。

## 1. 更新前の現在地

許可された導入先で実施する。全設定、全cache、全file一覧、個人pathをIssue/PRへ貼らない。次の出力はまずローカルだけで確認し、公開記録には末尾の限定した項目を転記する。

```powershell
codex --version
codex plugin marketplace list --json
codex plugin list --json
```

- 対象marketplaceの名前・配布元と実際の`root`を確認する。Git登録かローカル登録かも分ける
- `installed`側で対象pluginの導入有無・enabled状態を確認する。`available`にあるだけなら導入済みではない
- 導入済みpluginの実pathは、導入時の`add --json`が返した`installedPath`、または導入先の正式な診断で確認する。過去のpathやversion文字列から推測しない。更新前pathが確認できなければ、その段階は未確認として残す
- 配布元のcloneとmarketplace rootでそれぞれ`git rev-parse HEAD`と`git status --porcelain`を確認し、full SHAとclean/dirtyを記録する。dirtyならcommitだけで実bytesを説明できないため、差分を確認するまで照合を止める。Git情報がない場合もcommit確認は未確認とする

変数は実際に確認した値をローカルで設定する。以下の例の`$Source`は配布commitをcheckoutしたrepo、`$MarketplaceRoot`はlistが返したroot、`$InstalledCore`等は実際のinstalledPathを指す。cloneの`plugins/...`を導入先の代わりに渡さない。

```powershell
git -C "$Source" rev-parse HEAD
git -C "$Source" status --porcelain
git -C "$MarketplaceRoot" rev-parse HEAD
git -C "$MarketplaceRoot" status --porcelain
python scripts/verify_plugin_update.py --plugin happy-core --source "$Source/plugins/happy-core" --installed "$InstalledCore"
python scripts/verify_plugin_update.py --plugin happy-coding --source "$Source/plugins/happy-coding" --installed "$InstalledCoding"
```

scriptはrepoルートから実行する。Python標準libraryのみを使う。manifestと対象skillの固定allowlistだけを読み、相対path・存在・SHA-256を出す。設定やhome、cacheを変更しない。version値はsourceとinstalled双方のmanifestからローカルで確認し、記録する。manifest自体のhashも比較する。

- `samples_match`（exit 0）: 対象fileのbytes一致だけを意味する。plugin全体・実home・会話での読込成功ではない
- `mismatch`（exit 1）: 内容差、missing、読取不可、root外symlink等。双方missingも一致にしない
- `not_checked`（exit 1）: `--installed`を省略。導入先未確認。未導入かどうかはplugin一覧で別に判断する
- `session_load`は常に`not_checked`。このscriptでは会話での読込を証明できない

happy-previewは任意導入のまま。試用希望と導入が確認できた場合だけ、`--plugin happy-preview`、対応するsource、installedPathで比較する。未導入なら「未導入・更新対象外」と記録し、チェックを通すために導入しない。

## 2. 対応する方法で更新する

[公式CLIコマンド](https://learn.chatgpt.com/docs/developer-commands)と導入先の`--help`を照合する（資料確認日: 2026-10-01）。Git登録の対象marketplaceだけを更新する。

```powershell
codex plugin marketplace upgrade happy-ai-work-marketplace --json
codex plugin marketplace list --json
```

`errors`、更新後root、HEAD、clean状態を確認する。ローカル登録のrootはこのGit refreshで更新されたと見なさず、所有者が管理するcheckoutを対象commitへ更新してから確認する。配布元とmarketplaceのfull SHAが意図した対象に一致しなければ、先へ進まずref・登録元を調べる。

marketplace更新とpluginの再導入は別操作。対象pluginへの再導入が許可されていることを確認してから、対応するCLIまたはアプリのplugin画面で実施する。CLI例:

```powershell
codex plugin add happy-core@happy-ai-work-marketplace --json
codex plugin add happy-coding@happy-ai-work-marketplace --json
```

返された`installedPath`を使い、手順1のhash比較とmanifest version確認を再実行する。`plugin list --json`で導入・enabled状態も確認する。`add`の成功表示だけでは再コピーされたと断定しない。

内容が古いままなら、その結果を残す。対応CLIの`plugin remove`→`plugin add`による再インストールを、設定/cacheが削除される影響と対象を確認してから行う。remove成功後にaddが失敗したら「未導入・停止」とし、成功扱いにしない。cacheの手動削除・直接編集を更新手段にしない。

[公式のlocal marketplace説明](https://developers.openai.com/plugins/build/plugins#how-local-marketplaces-work)では、local pluginは元ディレクトリではなくcache内の導入済みcopyから読み込まれる。本repoはmarketplace自体をGitから登録しても、各entryは`source: local`である。manifestのversion、marketplaceのHEAD、cacheディレクトリ識別子は同一概念ではない。内部pathの命名を仮定せず、その導入先が返すroot/installedPathと実bytesを使う。source形式の移行はこの手順の対象外。

## 3. 新しい会話と実homeは別確認

更新後は対象pluginを有効にした新しい会話で、pluginの対象skillが利用可能か、どの導入済みcopyから読まれたかを確認する。旧会話の継続やrepo内fileの直接読取を、この証拠の代わりにしない。

- #46: installedの`implement`/`debug-and-fix`/`dotnet`と通知referenceを確認し、新しい会話で検証の事前通知・終了報告の指示が読み込まれるか確認する。長時間試験を実行する必要はない。実際の通知品質の観測は#44/#45で別に扱う
- #47: preview試用者だけ、新しい会話で`pr-delivery`の利用可能性・読込元を確認する。読込確認のためにPRをmergeしない。明示指定での読込と自動選択は別に記録する
- coreのhome-bootstrap配布templateが更新されても、実homeへ自動反映されない。実home適用はこの更新確認の対象外。別途依頼時にdry-run・差分・backup・明示承認を経る。通知指示の配布template、実home適用、新しい会話での有効化を混同しない
- 読込元を確認できない、CLIが未対応、認証/接続で止まる場合は「未確認」と停止理由を残す。hash一致だけで完了へ繰り上げない

## 次回にも使う短い記録

更新前/更新後の2つを残す。公開してよいのは配布物の証拠だけ。root/installedPathの実値、ユーザー名、設定全文、会話全文は公開しない。

```text
確認日・OS・Codex CLI版（アプリ利用ならアプリ版も）:
配布元: repository URL / full commit SHA / clean or dirty
marketplace: name / Git or local / full HEAD SHA / clean or dirty
plugin: name / source version / installed version / installed・enabled状態
対象file: allowlistの相対path / source SHA-256 / installed SHA-256 / 存在状態
更新操作・結果: 未実施 / 実施したコマンドの種類 / 成功・失敗
installed内容: 対象bytes一致 / 不一致 / 未導入 / 未確認
実home: 対象外 / 別途承認された適用結果
新しい会話: 読込元確認済み / 未確認・停止理由
preview: opt-in有無 / 明示指定読込 / 自動選択は別記
次の一歩:
```

1. 対象commit・plugin・導入先の許可を確認した
2. 更新前を記録し、対応方法でmarketplaceとpluginを更新した
3. full SHA・version・対象bytes・enabled状態を更新後に確認した
4. 新しい会話の読込と実homeを別判定にした
5. 未導入・未確認・停止理由を残した

## この変更の検証範囲

cloud上の開発と合成fixtureのテストは、実利用先の更新を証明しない。テストは同versionの内容差、新versionでも古い内容、missing、未確認path、preview非選択、root外symlink、CLI結果を扱う。公開PRにはテストしたcommitとCI結果を残す。利用者のinstalled plugin更新、実home適用、新しい会話での読込は、別途実測するまで未確認。
