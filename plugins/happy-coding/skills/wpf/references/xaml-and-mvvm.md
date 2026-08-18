# XAML and MVVM

- XAMLは表示構造、resource、bindingを中心にし、業務判断を置かない。
- ViewModelは画面状態とuser intentを表し、UI control型やdispatcherへの依存を必要最小限にする。
- domain／application serviceはWPFから独立させ、ViewModelをdomain modelの代用にしない。
- commandの実行可否、非同期中状態、cancel、error表示を一つの状態モデルとして整合させる。
- validationは入力途中、確定時、domain invariantの層を分ける。
- `INotifyPropertyChanged`、source generator、MVVM frameworkはrepo既存の選択へ合わせる。
- resource key、style、templateは局所性と再利用範囲を合わせ、巨大なglobal dictionaryを増やさない。
- code-behindはView固有のfocus、animation、control event等に限定できる。ゼロを目的にしない。

確認時はbinding error、DataContext、property名、update trigger、collection thread、resource解決順を優先して調べる。
