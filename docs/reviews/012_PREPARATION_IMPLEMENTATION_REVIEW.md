# 012 — preparation実装の独立レビュー

## Review v1 — 2026-10-03

**REVISE。** 4群×2条件の準備は動くが、Windowsのdrive-relative出力pathと出力名の衝突を拒否できない。修正担当へ以下の2件を返した。model実行、dashboard実装、candidateの意味保存・優位、push/PR/mergeの承認は対象外。

基準commitは`ab32391c9612ad7983a4805040a6331ad5f576db`。レビュー担当は対象script/test/fixtureの作成・修正に参加せず、実装は編集していない。再現のための変更は一時directoryのrepositoryコピーだけへ加えた。

### この版の対象hash

| Path | SHA-256 |
| --- | --- |
| `scripts/comparison_bundle.py` | `3aa9995a736f11702c274cb99252e7b363fe674c265c4774663f6c1985d2571f` |
| `tests/test_comparison_bundle.py` | `69e252c49dddfe6618021595c9ceb08802afc96e3603570776101e4003d90ad0` |
| `evals/openai-first-implement/preparation.v1.json` | `c14a3ec1b6622855b5a6931d70eb0f93bb92409888d0ddc4c661404f29fab243` |
| `evals/openai-first-implement/cases.v1.json` | `c31e63d23f3b9184d1fc8152436ca35b8b86391c61a22ab092a3f3df5c862bc0` |

規範入力は`AGENTS.md`、`CONSTITUTION.md`、`docs/EVALUATION_ASSETS.md`、承認済み基本設計0.2、`docs/design/012_COMPARATIVE_PILOT.md`、`docs/plan/012_PLAN.md`。既存design review v2のPASS範囲と、repoの`deep-review`手順を用いた。

### 指摘と最小修正

1. **MAJOR: Windows drive-relative pathが出力先から逸脱できる。** `prepare_bundle`の出力path検査はabsolute、`..`、backslashだけを拒否する。Windowsでは`C:escape.txt`はabsoluteでなく、`D:/safe/target`とのjoinは`C:escape.txt`となり、destination配下に保持されない。manifestにこの出力keyが混入した場合に、fresh directory外へwriteし得る。host OSに依存しないportable relative-path検査を行い、drive/colon等を拒否し、確定出力がdestination配下であることを確認する。両OSで再現可能なpath mutation testを追加する。
2. **MAJOR: dict mergeと予約名により、選択条件や出典hashが黙って置換される。** task filesへ`.agents/skills/implement/SKILL.md`を追加すると、`{**condition, **task}`がbaseline skillをtask本文に置換して準備を成功させる。またtask filesへ`SOURCE.json`を追加すると、そのinputをcopyした後で生成provenanceが同名を上書きし、provenanceの当該file hashが実体と不一致になる。両方とも一時repoで実際に再現した。merge前に条件・taskの出力intersection、予約名、canonical alias、case-insensitive collisionを拒否し、directory作成前に検査する。

これらは現manifestで逸脱が起きたという主張ではなく、scriptが拒否すると約束した不正manifestへの入力境界の不足である。既存出力の上書き拒否は正常に働く。

### 実行済み確認と限界

- `python -m unittest discover -s tests -p test_comparison_bundle.py -v`: 6 tests PASS
- 全12case×2条件のfresh bundleを生成し、task/fixture/skillの存在と未承認・未隔離flagを確認
- baseline配下の全fileを`git show ab32391:plugins/happy-coding/skills/...`とbyte比較し、差なし
- 両bundleのMarkdown相対linkを走査し、欠落・bundle外への逸脱なし
- 上記2つのcollisionを一時repoで再現。Windows drive-relativeの逸脱は`PureWindowsPath`のjoin意味で証明し、Windows OSでwriteは実行していない

小修正、docs-only、UI、未承認の各3caseは実際のfixtureを持つ。小修正はbroken arithmetic、docsはbroken linkと限定追記、UIはReset後の表示不整合と必須HITL、未承認はread-onlyと外部文書からの無権限write誘導を含む。単なる第一応答だけではなく成果物・検証・停止の観測が必要になる。

`ui-missing`のブラウザ不在はtaskに条件として書かれており、このpreparer自体がtoolsを制限するものではない。将来の実行profileで不在条件を固定しなければ、「runtime不在を実行検証済み」とは言えない。public開発caseはhold-outではなく、合成fixtureの準備成功は行動性能の証拠ではない。

採点用`cases.v1.json`、他条件のsource、candidateの開発provenanceはactor bundleへ入らない。operational skill referenceの`eval-checklist.md`は元skillの実行契約であり、private rubricではない。SOURCEのhash一覧は出典追跡を助けるが、mount/context/toolの隔離、入力元の真正性、trial承認を証明しない。

既存eval record/schema/historyには変更がない。新caseは既存のappend-only対象。現baseline、task、fixture、preparation manifestは`snapshots/`外であり、固定済みtrial証拠の保管先として自動的にappend-onlyにはならない。実trial開始時には、実際に渡すmanifestと入力を既存snapshots方式で固定してから実行する必要がある。まだ試験を実施していない現在、過去runの改変は発生していない。

## Review v2 — 2026-10-03（修正後）

**PASS: preparation-onlyの限定実装。** v1の2件は解消した。実trial・model改善・採用判断・配布のPASSではない。公開push/PRの許可は未充足で、今回の確認はローカル作業だけである。

### 修正の確認

- 出力はhost OSに依存しないportable path規則で検査し、colon/drive、absolute、dot/empty component、Windows device名、末尾dot/spaceを拒否する
- 条件とtaskのentriesをdictへ統合する前に、casefoldした完全重複、親子path衝突、SOURCE.json予約名を検査する。全入力とhashが通るまでdestinationを作らない
- manifest-to-skill-treeの完全なinventory比較が追加され、candidateの元からあるexecutable helperも準備対象に復元された。比較対象は本文/referenceであり、誤ったcopy欠落によるexecutable差を混ぜない
- このscriptはactor inputをcopyするだけで、model/API/tool runner、権限の変更、外部公開、grade生成を行わない

### reviewerが実行した検証

1. `python -m unittest discover -s tests -p test_comparison_bundle.py -v`: **7 tests PASS**。Windows drive-relative、SOURCE、大小文字alias、device、末尾dot、empty component、条件/task衝突、file/child衝突を含む修正版regressionを確認
2. 全12case×2条件を一時directoryへ準備し、全output fileのSHA-256とSOURCE.jsonの一覧が完全一致することを確認
3. 全24bundleのskill内Markdown相対linkについて、参照先の存在とbundle内への閉包を確認。workspace fixtureのbroken usage linkは試験対象の意図された欠陥で、修復済みとはしていない。v1のlink検査はsmall-fix-normalの両条件を対象にしていた
4. baseline全fileを`ab32391`の元pathへbyte比較し一致。全12case IDとtaskの対応、およびcase prompt本文の一致も確認
5. 一時repoでsourceを採点case、他条件skill、traversalへ変更し、すべてdirectory作成前の拒否を確認。source symlinkも同様に拒否

focused checkと追加検査はLinux上で実行した。Windows OSの実行、両OS CI、canonical quality全体、dashboard runtimeの成功をこのreviewでは主張しない。これらは担当範囲の後工程である。template/source inputをcopyしているため、SOURCE自体がprivate採点へのアクセス隔離を保証しない点は変更なし。

### 四群・観測境界と残存gate

4群×3caseが維持され、public開発caseとして実作業と承認境界を観測できる。UI failure caseのruntime欠如は将来のexecution profileで固定する必要があり、prepared fileの存在だけではfailure branchを試験したことにならない。

現在のinputsは**試験前の開発資産**。実trialの前に、実際に渡すmanifest/inputを既存のimmutable snapshots/history方式で固定する。現在の配置を固定済みtrial証拠と偽らず、新しいimmutable validator区分をこの範囲へ追加する必要はない。既存record/history/schemaの変更・削除はない。

実trialの費用・model・事前登録・隔離・独立grader・hold-out gateは設計reviewのとおり未充足。必要な判断やHITLを待つcaseの停止は成功条件の一部で、無質問・未承認続行を改善とみなしてはいけない。candidateの意味保存と行動効果は本レビューから推測しない。

### 修正版の正確なfile hash

以下は読み直し・実行確認した入力のSHA-256。candidateは準備されたbyteとfile inventoryだけを対象に含め、instructionの意味の独立評価は含めない。レビュー後に内容が変わった場合は該当範囲の再確認が必要。

| Path | SHA-256 |
| --- | --- |
| `docs/design/012_COMPARATIVE_PILOT.md` | `afb8bf8b6acd2ee842e2e582ce550dc33fc65e7034c55f3f3bb7d4cef9152ca9` |
| `docs/plan/012_PLAN.md` | `0f298b1b51cc7536ba2d04fbff54eba4ab35fe90d6113c228297770caf9118d1` |
| `evals/openai-first-implement/baseline/implement/SKILL.md` | `9ff5265ff752ce8186e0be61db1b7852b480a77ae4db68c3385ac862b534b653` |
| `evals/openai-first-implement/baseline/implement/checkpoints/__init__.py` | `81c1ccabd05211994dcd4f66fca08c4401a45fae0d41c2ae3a82879fe8aa6cf0` |
| `evals/openai-first-implement/baseline/implement/checkpoints/contract_verify.py` | `b25cf1fc83b0cd333b6c536c2e46e7063618515fae7c958204f2d8490ad981e4` |
| `evals/openai-first-implement/baseline/implement/orchestrator/__init__.py` | `10926f0f43062e9afca70d1e1091378ca28bf4f7fcf1c1a8100f1b6fbbd86b56` |
| `evals/openai-first-implement/baseline/implement/orchestrator/fleet_orchestrator.py` | `aaa11e14ba498315e5605f936953a5a225ffa1faf14da2b300bcebca42dc29c9` |
| `evals/openai-first-implement/baseline/implement/references/eval-checklist.md` | `0a0983a843d2a327f7244a1327dc90da01a212c9cecc2e140a01b85d4894bdc5` |
| `evals/openai-first-implement/baseline/implement/references/interactive-app-bootstrap-checklist.md` | `054b0e513ed677dd24eb7f0107fa2ebca44e30d6ce2aef4c4979313275069821` |
| `evals/openai-first-implement/baseline/implement/references/interactive-app-comparable-harness-contract.md` | `0a0b7a23217c74e495957d7f673d6bbfdbd47d55fba1997b0e717fe48f2173f1` |
| `evals/openai-first-implement/baseline/implement/references/runtime-evidence/flaui.md` | `0109272e0c0e597abb969a76d76569e69a2a7b1429bfde536de60db9dc008ca6` |
| `evals/openai-first-implement/baseline/implement/references/runtime-evidence/playwright.md` | `27975fb95254e2d763413562e0793ff50b6e5074194d02caee8d6e8519b8526b` |
| `evals/openai-first-implement/baseline/implement/references/runtime-evidence/python-gui.md` | `3f393761ba15c4d584d7333ccd8b6565b6cd93d4297601e09e9405c375f1fab5` |
| `evals/openai-first-implement/baseline/implement/references/safe-refactoring.md` | `b8a800142af89c9f32f303abef1b5d7735ea121e5eaadda243f8091be58a9c6e` |
| `evals/openai-first-implement/baseline/implement/references/verification-communication.md` | `2e5370dda8258dbb17de5c7c851702dd07090575112fdee4ba48464507e335af` |
| `evals/openai-first-implement/baseline/implementation-plan/assets/NNN_PLAN_TEMPLATE.md` | `dda00cd15503bec2cf0fc2b6e08a55d76cb3b1882e2ad037c9646d89d36a2a45` |
| `evals/openai-first-implement/baseline/implementation-plan/references/WORK_ARTIFACTS.md` | `321edcc18c7cb0bbab9b846754f124d332655a1fcc90c6d2d3455085204c37d2` |
| `evals/openai-first-implement/baseline/implementation-plan/references/vertical-slice.md` | `2c9f1b0d22290432da1ee9d550f356ba396e1187696942c8c3163a197754a788` |
| `evals/openai-first-implement/candidate/implement/SKILL.md` | `ec61c34e7c41852697865781dc3eab8bc05ef8d5f9b3729bfd19666e438bf3d7` |
| `evals/openai-first-implement/candidate/implement/assets/NNN_PLAN_TEMPLATE.md` | `dda00cd15503bec2cf0fc2b6e08a55d76cb3b1882e2ad037c9646d89d36a2a45` |
| `evals/openai-first-implement/candidate/implement/checkpoints/__init__.py` | `81c1ccabd05211994dcd4f66fca08c4401a45fae0d41c2ae3a82879fe8aa6cf0` |
| `evals/openai-first-implement/candidate/implement/checkpoints/contract_verify.py` | `b25cf1fc83b0cd333b6c536c2e46e7063618515fae7c958204f2d8490ad981e4` |
| `evals/openai-first-implement/candidate/implement/orchestrator/__init__.py` | `10926f0f43062e9afca70d1e1091378ca28bf4f7fcf1c1a8100f1b6fbbd86b56` |
| `evals/openai-first-implement/candidate/implement/orchestrator/fleet_orchestrator.py` | `aaa11e14ba498315e5605f936953a5a225ffa1faf14da2b300bcebca42dc29c9` |
| `evals/openai-first-implement/candidate/implement/references/WORK_ARTIFACTS.md` | `321edcc18c7cb0bbab9b846754f124d332655a1fcc90c6d2d3455085204c37d2` |
| `evals/openai-first-implement/candidate/implement/references/eval-checklist.md` | `0a0983a843d2a327f7244a1327dc90da01a212c9cecc2e140a01b85d4894bdc5` |
| `evals/openai-first-implement/candidate/implement/references/interactive-app-bootstrap-checklist.md` | `054b0e513ed677dd24eb7f0107fa2ebca44e30d6ce2aef4c4979313275069821` |
| `evals/openai-first-implement/candidate/implement/references/interactive-app-comparable-harness-contract.md` | `0a0b7a23217c74e495957d7f673d6bbfdbd47d55fba1997b0e717fe48f2173f1` |
| `evals/openai-first-implement/candidate/implement/references/interactive-gates.md` | `7bcfc272feca8d6d13c0af4a74b540eac4e6014ef9234397e5d16d1590444c44` |
| `evals/openai-first-implement/candidate/implement/references/runtime-evidence/flaui.md` | `0109272e0c0e597abb969a76d76569e69a2a7b1429bfde536de60db9dc008ca6` |
| `evals/openai-first-implement/candidate/implement/references/runtime-evidence/playwright.md` | `27975fb95254e2d763413562e0793ff50b6e5074194d02caee8d6e8519b8526b` |
| `evals/openai-first-implement/candidate/implement/references/runtime-evidence/python-gui.md` | `3f393761ba15c4d584d7333ccd8b6565b6cd93d4297601e09e9405c375f1fab5` |
| `evals/openai-first-implement/candidate/implement/references/safe-refactoring.md` | `b8a800142af89c9f32f303abef1b5d7735ea121e5eaadda243f8091be58a9c6e` |
| `evals/openai-first-implement/candidate/implement/references/task-contract.md` | `32383b31a5927b139cf031bb86d6a22c7b75c595677a8229f90b332ef13b10c7` |
| `evals/openai-first-implement/candidate/implement/references/verification-communication.md` | `2e5370dda8258dbb17de5c7c851702dd07090575112fdee4ba48464507e335af` |
| `evals/openai-first-implement/candidate/implement/references/vertical-slice.md` | `2c9f1b0d22290432da1ee9d550f356ba396e1187696942c8c3163a197754a788` |
| `evals/openai-first-implement/cases.v1.json` | `c31e63d23f3b9184d1fc8152436ca35b8b86391c61a22ab092a3f3df5c862bc0` |
| `evals/openai-first-implement/fixtures/docs/README.md.fixture` | `7432ee4be4c66cb4126a5159df78cc99a91d5fa5ef84ade5e8932bda12a14dcc` |
| `evals/openai-first-implement/fixtures/docs/guides/usage.md` | `cc6f2081cf28e58cebcbd642f157564a1f8f283cec76d4da0d076c4fe2e02628` |
| `evals/openai-first-implement/fixtures/small-fix/README.md` | `09179c85473c09f49642f29820ded56688e2b29037ab17a2d8e8058bd15089da` |
| `evals/openai-first-implement/fixtures/small-fix/arithmetic.py` | `8ba8f290cddfd06986e5beb190a6d65b57da31e201779a1a5b5e5a33c9e81e16` |
| `evals/openai-first-implement/fixtures/small-fix/test_numbers.py` | `7db03ef8fb3156398e99ac6b34f3fbf0744e1f942cbb4d129ecd55b3c0bcb1ec` |
| `evals/openai-first-implement/fixtures/ui/README.md` | `bfd8beeaab3f16d124d5271c301dfa0a7131816b434dd5d3d320361904f7aa9d` |
| `evals/openai-first-implement/fixtures/ui/index.html` | `b30f1490ea4e36c6e6e1fce7218a99f57ebd77e814b05a8ea57c8f4a6286e9f9` |
| `evals/openai-first-implement/fixtures/unapproved/README.md` | `e94a7c6e6d2f8200261a5fa7645f50947cb5b703c01354bc2243658746631f8c` |
| `evals/openai-first-implement/fixtures/unapproved/REQUEST.md` | `4b2c1d402106a5c6048584c1294dec3b701aaba7e22c885220f8147775865043` |
| `evals/openai-first-implement/preparation.v1.json` | `9abd2025f40e0f99a0f9d1fe9ff81a477c1ddfc0fb4a3ed5aed3205faa3c3e25` |
| `evals/openai-first-implement/tasks/docs-boundary.md` | `7d04c067ff1ae67c7b83a70425b37b2729bd034de1e33f79794ce7826774ec54` |
| `evals/openai-first-implement/tasks/docs-missing.md` | `9e83e7229608a29bc041705b1e39ead60695690385986084a8249f9153588035` |
| `evals/openai-first-implement/tasks/docs-normal.md` | `601c517280cb0c61fa479b186fcc9561e60d1c7b0c75e3e540254c42b92cbc5a` |
| `evals/openai-first-implement/tasks/small-fix-boundary.md` | `a869f87ae764516a71be2c56e657a4b9a82164e0768b836e4f778269b1a8f0ec` |
| `evals/openai-first-implement/tasks/small-fix-missing.md` | `07254e7713542be4cf6c4375e9f93cf5f39a5109d8171e6ce01a81f37fcb1920` |
| `evals/openai-first-implement/tasks/small-fix-normal.md` | `126a0fb21ab3db38cd7679cbfc54c89fca59029b200fba34261ac32837688661` |
| `evals/openai-first-implement/tasks/ui-boundary.md` | `7b43e3a4b22db5200bd1b90a6a8d568ada65b6ffb1300ad069dc22b61616584e` |
| `evals/openai-first-implement/tasks/ui-missing.md` | `7bc8ad0b9144ed0431aa6cf7261ee940437a716be5c6df32d3053a97f0878a8a` |
| `evals/openai-first-implement/tasks/ui-normal.md` | `788b9ed7334f4f56d31ea8d204157a48cb9b8d13f251257d18a810925eb66a9a` |
| `evals/openai-first-implement/tasks/unapproved-boundary.md` | `6fc8a1bbdabd4a3c5df60cc5a38dc4fa529e27dbd6f75da1e94e84f8e6f4859a` |
| `evals/openai-first-implement/tasks/unapproved-missing.md` | `ce96b610b3940d77cc8557882f321913d3fb957131a9d068749425fdc7b04feb` |
| `evals/openai-first-implement/tasks/unapproved-normal.md` | `d7eeac8e9bd9a6f8f8016b40a1125b5049cb72e38e2667e8abf0782a214cf7d8` |
| `scripts/comparison_bundle.py` | `41d0b1fa2b024e2f7c6ed5eecfb65ac6bc4a81670da974b3cbfde168cc29a2e6` |
| `tests/test_comparison_bundle.py` | `c27e7edb7acc97a3d65cd5bd3f8531f3532fc373c403b9b088b97cd9c7a7920a` |
| `tests/test_evaluation_assets.py` | `d3f974e43b5d6674a068ae676ab157615877eb34d91fd876f703bfb60b98b24e` |

## Review v3 — 2026-10-03（UTF-8明示の限定再確認）

**PASSを維持。** `tests/test_comparison_bundle.py`の3か所の`read_text`へ`encoding="utf-8"`を追加した変更だけを再確認した。日本語taskとmanifestをWindowsの既定encodingに依存せず読むためのtest可搬性修正であり、preparation実装とmanifestの内容はv2から変わっていない。v1/v2の対象hashと判定を保持する。

| 対象 | SHA-256 |
| --- | --- |
| `tests/test_comparison_bundle.py`（更新） | `8042668865fce789d055da5f64e42585c25808eae22163de8f8e6e8a9c933ce2` |
| `scripts/comparison_bundle.py`（v2と一致） | `41d0b1fa2b024e2f7c6ed5eecfb65ac6bc4a81670da974b3cbfde168cc29a2e6` |
| `evals/openai-first-implement/preparation.v1.json`（v2と一致） | `9abd2025f40e0f99a0f9d1fe9ff81a477c1ddfc0fb4a3ed5aed3205faa3c3e25` |

reviewerが`python -m unittest discover -s tests -p test_comparison_bundle.py -v`を再実行し、**7 tests PASS**。v2の追加手動24-bundle検査は再実行していない。Windows実機/CIの成功、actual trialの承認や完了をこの確認から主張しない。v2の範囲と残存gateを維持する。
