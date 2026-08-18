---
name: repo-onboarding
description: 未知のリポジトリを変更せずに調査し、目的、構造、技術、build／test契約、重要境界、未確認事項の最初の地図を作る。新しいrepoへ入るときや実装前のorientationで使う。bootstrap変更は扱わない。
---

# Repository onboarding

read-onlyを既定にし、READMEだけでなくmanifest、lockfile、CI、`AGENTS.md`、近接docsを根拠として地図を作る。

## ワークフロー

1. repo root、git状態、`AGENTS.md` chain、README、docs入口を確認する。
2. solution／workspace／manifest／lockfile／CIから主要言語、runtime、dependency、build、test、lintの正本を特定する。
3. 主要directory、entrypoint、public interface、data store、external integrationを浅くたどる。
4. 代表的な一つの処理経路を入口から出力まで追い、責務境界を確認する。
5. commandは推測せず根拠を添える。実行が必要な場合も、read-onlyで安全なversion／help／test discoveryから始める。
6. 目的、技術、構造、主要flow、build、test、注意点、未確認事項を短く返す。

repoへ`AGENTS.md`、CI、hook等を追加する依頼は`workspace-bootstrap`へ分離する。onboardingの名目で設定を書き換えない。

## 出力

1. repoの目的
2. 主要技術と実行環境
3. directoryとentrypoint
4. 代表flowと責務境界
5. build／test／lint commandと根拠
6. 重要な制約・risk
7. 未確認事項と次に読む場所
