# Emotebook
![usage](https://user-images.githubusercontent.com/43209256/113474828-44d51380-94ad-11eb-9906-c4d4fa01f834.gif)

https://emotebook.herokuapp.com/

herokuへデプロイしました！

# ところで

- 試験やプレゼンを控えて、不安が押し寄せてくる。やるべき事に身が入らない……。
- 会社の同僚、はたまた配偶者にムカついてしょうがない。ついカッとなってしまう……。
- やる事が多すぎてストレスがたまっている。最後にリラックスできたのはいつだったっけ……？

こんな事はありませんか？私自身はありました。前職でNHKの収納業務をしていたのですが、お客様からの罵倒や見られ方、上手く行かない人間関係等からストレスを抱えていました。
このようなストレスとはどのように向き合えばいいのか？いろいろな本を調べ、できる限り実践した結果、私の中で一定の効果をあげたのが、**エクスプレッシブライティング**です。

# エクスプレッシブライティング―概要

感情に対して *客観性* を得る事で自分と感情の間に距離が生まれ、嫌な感情にとらわれづらくなります。そのために、ひたすら感情や思考を書き下す行為を *エクスプレッシブライティング* と呼びます。
数百を超える論文で実証されており、前述の通り、私自身NHK営業がキツかった時にお世話になった方法でもあります。

# これから追加していきたい機能

- evernote・notion連携
- SPA化
- 日記一覧画面で、色によってフィルタリング(できれば大まかなフィルタリングも)
- 日記の表示形式を色だけにしてグリッド表示
- APIを作成して、flutterでアプリを作成

# 作る動機

- 自分で使用するには多機能すぎる記録アプリが多かった
- 感情をより細かく表現すればするほど、客観性を身につける事ができると考えた

これらの理由から、シンプルに色も保存する事ができる日記アプリを作りました。

# 苦労した所

- テストの書き方や、どのように考えればいいかが全く解らなかったのでとても時間がかかりました。今はいい書き方がわかる！というわけではありませんが、テストについて知識が0だったので、スキルをスタートラインに持っていくのに苦労しました。
- フロントエンドに関して、小学校の時にHTMLを少し触った事がある程度で、javascriptを使用した事すらなかったので、Vueなどに苦労しました。当初は2週間程度でフロントのデザイン等も終わるだろうと考えていました。ですが全くの見当違いで、デザインの修正など頻繁に起って最終的に2ヶ月半もかかってしまいました。

# 学んだ所

- 1種類のモデルには1種類のView
日記を編集するViewを、内容編集と色・レベル選択とに分けてしまってView間の連携がとても取りづらかったです。"色選択だけして日記は書かない"という使用状況を想定して、Viewレベルで関数を分けてしまったのですが、一つのViewにして、フロントエンドの方で出し方を分けたほうがわかりやすかったです。

- フロントエンドとバックエンドは切り分けたほうが圧倒的に実装しやすい
今回はvueの感覚が全くつかめていなかったので、Djangoのテンプレート内にVueをその儘実装してしまいました。そのため、Vueの特徴の一つであるコンポーネントを利用する事ができなくなってしまったのと、実行速度が遅くなってしまったのがとても痛いです。

# 使用した技術

バックエンド――Django
テンプレート内に直書きでVue.js3を使用。

このバージョンではまず動く事を最優先にしていたのでこの実装となりましたが、次回のバージョンでは、バックエンドにAPIを実装して、フロントエンドはVueのSPAで実現していきたいと考えています。また、恐らくAPIにすればネイティブアプリも作りやすいと思うので、Flutterも学んでアプリ化していきたいと思います。

# 参考

[https://yuchrszk.blogspot.com/2014/12/blog-post_30.html](https://yuchrszk.blogspot.com/2014/12/blog-post_30.html)

[https://yuchrszk.blogspot.com/2016/09/blog-post_29.html](https://yuchrszk.blogspot.com/2016/09/blog-post_29.html)
