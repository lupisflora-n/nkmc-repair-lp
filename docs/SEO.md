# LIBRIGHT LP 基本SEO

更新: 2026-10-31。SEO専門担当の監査に基づき実装。順位・検索拡張表示の保証はしない。

## 実装済み

- title: 千葉の住宅リペア・キズ補修｜関東対応｜リブライト LIBRIGHT。
- description: 最新の対応部材と法人・個人の相談に合わせて設定。SEOの文章はsite/content.jsonのseoへ集約。
- 日本語指定、viewport、1つのH1、地域・サービスが分かる見出し、テキストの内部リンク、ユーザー指定の写真代替説明を維持。
- OGPのtitle/description/locale/site_nameとTwitter summaryを設定。未確認のOG専用画像は捏造・加工しない。
- 事業者の基本情報をOrganization型のJSON-LDに記述。公開住所が未確定のため、住所等が必要なLocalBusinessの検索拡張表示を狙う設定は行わない。屋号、英字屋号、事業説明、千葉県・関東地方、ユーザーが指定したInstagramだけを使う。住所・電話・料金・レビュー・TRC推薦等は作らない。
- 写真の原寸を読み取り専用で調べ、width/height属性を追加。元写真の編集・再保存・変換はしない。下部写真のlazy loadingを維持。
- 中段OUR STORY欄を削除。冒頭へ移動済みのブランド見出し・原点本文はその位置に保持。

## 正式URL確定後に自動生成するもの

publication.siteUrlに正規HTTPS URLを設定して公開用ビルドを行うと、canonical、og:url、構造化データのurl/@id/logo、sitemap.xml、robots.txtを生成する。
公開URL未定のまま仮のドメインを配信しない。URL未設定なら公開用ビルドは停止する。

reviewはnoindex,nofollowを維持し、canonical・og:url・検索登録用ファイルを生成しない。外部に配信する場合も確認版の位置づけを保つ。

サブディレクトリで配信する場合、robots.txtはドメインのルートが検索エンジンによる取得位置となるため、公開先決定後に配置方法を調整する。サイトマップURLはサブディレクトリも正確に反映する。

## 公開後に行うもの

- 実URLでのHTTP応答、noindex解除、canonicalと配信先の一致、モバイル表示を確認。
- Search Consoleの所有権確認・サイトマップ送信・URL検査は、公開先と権限がそろってから実施。現時点では未実施。
- 構造化データの実URL確認と、検索エンジンによる取得状況を確認。最小限の事業者情報はリッチリザルトの適格性を保証するものではない。

## 検証

scripts/verify_browser.pyで320/390/768/1440px、写真とロゴ、問い合わせ導線を検証。
tests/test_seo.pyで公開URL未定時の停止、確認版から正式URLを出さないこと、canonical/OG/サイトマップの一致、未確認情報の非掲載、JSON-LDエスケープ、写真寸法の読み取りを検証。

## 参照

- [Google SEOスターターガイド](https://developers.google.com/search/docs/fundamentals/seo-starter-guide?hl=ja)
- [タイトルリンク](https://developers.google.com/search/docs/appearance/title-link?hl=ja)
- [canonical](https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls?hl=ja)
- [LocalBusiness構造化データ](https://developers.google.com/search/docs/appearance/structured-data/local-business?hl=ja)

2026-10-31に各公式資料へのアクセスを確認。最低限の設定に留め、本文の不自然なキーワード追加や架空の評価・所在地は行わない。
