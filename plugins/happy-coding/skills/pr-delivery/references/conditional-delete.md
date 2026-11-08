# 対象refと期待SHAを固定した条件付き削除

この選択肢はSKILL.mdの許可・MERGED状態・取り込まれたheadとbase履歴・所有対象・未push/未統合変更・worktree保護をすべて満たしたremote branchだけに使う。leaseの存在だけで安全とは判断しない。localは通常の`git branch -d`だけとする。

## 実行前に固定する値

- `repo`: 確認済みlocal repoの絶対path
- `remote`: 対象PRのhead repoに対応するremote名。fetch先だけでなく`git remote get-url --push --all "$remote"`でpush先を確認する。複数push先、別repo、URL rewrite等で接続先を証明できない場合は保持する
- `push_url`: 上で確認した唯一のpush先。remote名や暗黙のupstreamではなく、確認済みの接続先を操作に渡す。認証情報入りURLを報告・記録しない
- `ref`: 自分の対象branchの完全な`refs/heads/...`。default/base/shared・fork・他者のrefは除外する
- `expected`: 取り込み済みPR headと照合した、空でも全ゼロでもない完全なcommit object ID。削除直前に読んだtipを無条件に採用しない

Gitの[明示した期待値付きlease](https://git-scm.com/docs/git-push)はremote refがその値と一致するときだけ更新する。上記値を確認した場合の削除形は次のとおり（shellでは各値をquoteする）。これは実行許可を与えるsnippetではない。

```sh
git -C "$repo" push --no-follow-tags --recurse-submodules=no \
  "--force-with-lease=$ref:$expected" -- "$push_url" ":$ref"
```

更新するrefspecは空のsourceを持つ`:$ref`の1件だけ。tag自動送信とsubmoduleへのpushも抑止する。`--force`/`-f`、`+`付きrefspec、`--mirror`/`--all`/`--tags`/`--prune`、`--no-verify`、値を省略したleaseを追加しない。暗黙のremote-tracking refを期待値にしない。条件付きAPIを選ぶ場合も、repoと単一の完全refと期待SHAを指定し、サーバ側の比較と削除が不可分である保証が必要。読取→無条件deleteの2操作は代替にならない。

## 競合・拒否・結果不明

拒否時は停止し、確認した新tipや理由を報告してbranchを保持する。fetchがremote-tracking refを進めても元の期待SHAを更新して自動再試行しない。無条件delete、force、別toolや認証変更で押し切らない。通信失敗などで結果不明ならread-onlyで同じrefの状態を確認し、削除完了を推測しない。成功時も同じ接続先の正確なrefが不在であることを確認し、local/worktree整理と区別して報告する。

この保証は「操作時に期待SHAと一致するrefだけ」を対象とする。実GitHubの権限・branch protection・tool対応は別途確認し、合成local bare remoteの結果を実環境での成功保証にしない。
