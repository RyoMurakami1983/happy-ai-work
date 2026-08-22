---
status: accepted
date: 2026-08-22
---

# Constitutionの正本と公開利用時の所有境界を分離する

個人philosophyとHappy Constitutionを一方から他方へ自動上書きする単一正本にはせず、GitHub profile READMEを個人philosophy、root `CONSTITUTION.md`を公式`happy-ai-work`のupstream Constitutionとして相互参照する。両者の意味変更はGit revisionと同期recordで検知し、3日警告、7日release／merge制限、10日hard stopを適用するが、同期、調査、修復、safe rollback、緊急安全対応は塞がない。publicな利用先はdownstream所有者のConstitutionを優先でき、upstream固有価値を暗黙適用しない一方、secret保護、破壊操作の抑止、評価独立性、過去結果の非改ざん、人間の所有権と修復可能性は緩和できない。この分離により、個人の変化、公式projectの一貫性、public利用者の多様性を同時に扱う。
