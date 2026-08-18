# Modularity review

module、package、project、service間の結合を、次の3軸で評価する。

1. **統合強度**: contractだけか、model／実装／内部dataまで共有するか。
2. **距離**: 同一module／process／repo／teamか、独立service／別teamか。
3. **変動性**: 両側が同じ理由・頻度で変わるか。

高強度・高距離・高変動性の組合せを優先的なriskとする。code importだけでなく、共有DB、設定、schema、deploy順序、命名規約、人的調整も結合として調べる。

## 出力

- 対象moduleと責務
- 統合ごとの強度、距離、変動性と根拠
- 重大な不均衡
- contract導入、module統合、境界再定義、translation layer等の候補
- 判断に不足する情報

レビューでは診断と修正候補までに留める。大規模な再設計や移動は`design-and-plan`へ渡す。
