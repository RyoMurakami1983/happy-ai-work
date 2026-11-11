# Done 023: 極めと残心の試用実装

## 契約

所有者が「極めと残心」の本文案を確認して実装を依頼した。目的はタイミング・確定・回復の共通観点を試せる形にし、具体的な設計・検証を既存coding skillへつなぐこと。

規範入力: 所有者確認済み本文、[採用範囲](../design/023_KIME_ZANSHIN_PREVIEW.md)、ADR 0004、現行repoの品質契約。

非対象: coreへの昇格、home/AGENTS.md変更、端末plugin導入、実案件の改修、外部公開・PR・merge。実利用効果や性能改善をこの作業の完了主張に含めない。

## Sliceと検証

1. preview skill本体・必要な例・UI metadataと配布案内を追加する。
2. codingの設計・実装へ任意参照を加え、UI状態・非同期contract・自動計測を既存の責務内で補う。preview未導入でも進められることを保つ。
3. 公式形式検証、repo validator、参照確認、6つの公開合成promptへの応答と独立再読、標準品質入口で検証する。

文書・設定差分のためREDを作らず、形式・リンク・変更された指示の実行可能性を確認する。失敗は差分へ戻し、権限・契約の変更が必要ならその部分のみ保留する。

## 現在地

3つのsliceのローカル実装・基本検証を完了。公式形式検証とrepo validatorが成功し、6つの合成promptは独立採点でPASS。標準品質入口は255件中253件のunit test成功・環境条件による2件skip、lint・型検査・diff check成功。

[検証範囲と未確認](../design/023_KIME_ZANSHIN_PREVIEW.md)および[合成課題の判定記録](../../evals/records/kime-zanshin-preview-001.json)を保存した。通常coreへの昇格、実利用効果の判定、外部公開や端末導入はこの完了に含めない。
