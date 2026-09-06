# componentと入力の接続

C#の知識があっても、Unityで動く条件は別に確認する。以下は調査時の版付き公式資料。対象projectの版へ合わせて読む。

## component

- MonoBehaviourはGameObject上のcomponentとして扱う。通常のC# classの`new`による生成と混同しない。serialized fieldの参照がInspectorで割り当てられているか確認する。
- `Awake`は自身の初期化、`OnEnable`／`OnDisable`は有効期間に対応する処理、`Start`は開始処理、`Update`はframeごとの処理、`FixedUpdate`は物理更新に関係する処理として、今回必要な役割だけ説明する。他objectの`Awake`順序に依存しない。[Awake](https://docs.unity3d.com/6000.0/Documentation/ScriptReference/MonoBehaviour.Awake.html)、[FixedUpdate](https://docs.unity3d.com/6000.0/Documentation/ScriptReference/MonoBehaviour.FixedUpdate.html)
- 見た目が2Dでも物理の選択は別に確認する。`Rigidbody2D`／`Collider2D`と3Dの`Rigidbody`／`Collider`は別系統で、衝突callbackも対応させる。[2D introduction](https://docs.unity3d.com/cn/2023.2/Manual/2D-introduction.html)

## 入力

- legacy Input ManagerかInput Systemか、package版、Active Input Handling、action／binding、利用するdeviceを確認する。古い教材の`Input`呼出しと新方式を無自覚に混ぜない。
- 新Input Systemはinstallだけで有効化まで完了したとは限らない。backend変更は再起動を伴い得る。既存projectを理由なくBothへ広げず、採用方式と既存コードの整合を確認する。[Input System installation](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.17/manual/Installation.html)
- 「押した瞬間」と「押している間」を区別し、入力取得と物理更新の周期差を考慮する。callbackやupdate modeは採用packageの設定に合わせる。操作の取りこぼしを単純な速度調整で隠さない。
- legacyの押下取得は[GetButtonDown](https://docs.unity3d.com/6000.0/Documentation/ScriptReference/Input.GetButtonDown.html)に従い`Update`で行う。物理処理へ渡す場合は押下を保持して一度消費し、いつ破棄するかも決める。新方式は[混在する更新タイミング](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.17/manual/timing-mixed-scenarios.html)を参照し、全方式を無条件に同じ更新位置へ変えない。

## 時間と保存を扱う変更

- 値が「毎秒の速度」か「今回の変位」かを確認する。[deltaTime](https://docs.unity3d.com/6000.0/Documentation/ScriptReference/Time-deltaTime.html)を何にでも掛けず、[AddForce](https://docs.unity3d.com/6000.0/Documentation/ScriptReference/Rigidbody.AddForce.html)等ではAPIとForceModeの意味に合わせる。
- Inspectorで使う値はUnityの[serialization rules](https://docs.unity3d.com/6000.0/Documentation/Manual/script-serialization-rules.html)に合うfieldか確認する。通常のproperty、static等を同じように保存できると思わない。
- [Play Mode](https://docs.unity3d.com/6000.0/Documentation/Manual/GameView.html)で調整したSceneの一時値は、採用するなら停止後にScene／Prefabへ反映・保存して確認する。Play中に行ったすべてのファイル書込みが巻き戻るという意味ではない。

## つながらないとき

Consoleの最初の関連エラーから再現する。scriptのコンパイル→object／componentの有効状態→Inspector参照→入力設定→物理componentとlayer→Scene／Prefabの保存状態のうち、症状に関係する箇所を絞る。何でもpackage再導入・Library削除へ進めない。
