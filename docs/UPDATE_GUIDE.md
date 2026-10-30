# 差し替えと公開準備の手順

この手順は制作担当の引き継ぎ用。ユーザーへコードの編集作業を宿題として渡さず、受領した情報を担当側で反映する。

## 構成

- `site/content.json`: 本文、料金、写真、問い合わせ先、ロゴ、紹介の公開状態。
- `site/template.html`: ページの構造。
- `site/styles.css`: スマホ・PCの表示。原写真は全体と縦横比を保つ。
- `site/app.js`: 相談文コピー、コピーできない場合の文面選択、原写真を使う拡大表示。
- `scripts/build.py`: 設定から静的HTMLを作成する。フレームワークや有料APIは不要。

## 確認版の更新

`python scripts/build.py --mode review`

`design/preview.html` と `dist-review/` を生成する。前者はCSS・JavaScript・写真・ロゴを含む単体HTML。単体ファイルだけで表示でき、assetsフォルダを添える必要はない。
確認版では写真の配置枠や未確定の原稿を表示できる。未公開表示とnoindexを付ける。確認版をそのまま公開用として扱わない。

## 施工写真

元写真をファイルとして取得してから、次の形式で実行する。

`python scripts/import_photos.py --case case-01 --before /受領した補修前の元ファイル.jpg --after /受領した補修後の元ファイル.jpg`

case-02、case-03も同様。元ファイルのバイト列を変更せず、`site/assets/cases/`へ複製しSHA-256を登録する。既存の異なる元写真は上書きしない。
この取り込みは、施工内容や掲載条件の確認を済ませる操作ではない。該当情報を確かめてから事例ごとの `confirmed`、`publicationCleared` と `cases.publish` を更新する。
画像の圧縮・変換・切り抜き・レタッチは行わない。

## ロゴ

正式ロゴのWeb用SVGとアイコンは `site/assets/brand/libright/` に保存済み。主要ファイルは `logos/svg/horizontal-jp-color.svg`、`logos/svg/symbol-color.svg`、`icons/favicon.svg`。編集資料は `design/brand/libright/`。現在は`brand.assets.*`を設定し、`brand.assetsReady`をtrueとして反映済み。横組みカラー、シンボル、白抜き、faviconを使い、スマホ/PC表示を確認した。
元のSVG・PNGは変更しない。単体HTMLではブランド素材・施工写真を元バイト列のままdata URIへ可逆に埋め込む。復号した写真が原ファイルとSHA-256で一致することを確認する。通常の配信版は元画像ファイルを参照する。ロゴの色・形・最小幅・余白はブランドガイドを引き継ぐ。

## 料金

`pricing`の値へ確認した文言を記入する。金額の単位、税、出張条件、見積もり条件を併記する。
内容確認後に `confirmed: true`、掲載するときだけ `publish: true` にする。非表示のままでも他の制作工程は進められる。
未確定の間に「無料」「一律」「最安」や仮価格を入れない。

## 紹介・流れ・協力先

ブランド紹介は `copy.aboutConfirmed`。現在はユーザーが提示した対外コンセプトを採用済み。実際の施工の流れは `copy.processConfirmed` で管理し、未確認の間は公開版から除外する。
`copy.brandPromise` が冒頭の補助文、`copy.aboutText` がコンセプト本文、`copy.brandOriginText` がお客様への価値に結びつけた屋号の説明。私的な創業動機をこれらへ入れない。
TRCを紹介する場合は `partnerIntroduction` に実際の関係、同社の仕事も伝わる紹介、公式案内先をそろえ、内容と掲載条件を確認してから公開する。

## 問い合わせ

`contact.profileUrl` はスクリーンショットのユーザー名を元にしたInstagram URL。確認版ではプロフィールを開く導線を用意済み。
本人の実アカウントと、プロフィールの「メッセージ」からDMに進めることを確認して `linkVerified` を更新する。実際にDMを送る操作は別の送信許可として扱う。
`channelConfirmedForLp` は最終的に採用する窓口が確定したときに更新する。
相談文のコピーは送信ではない。ページ側で内容を保存・送信するフォームやデータベースは使用していない。

## 公開

公開先の条件と設定を確認して `publication.hostingConditionsChecked` を更新する。GitHub Pagesの利用条件の確認は未完了。
`python scripts/build.py --mode release` は、原写真・問い合わせ経路・ロゴ・公開条件がそろうまで停止する。実際の確認なしにフラグを変更して通さない。
条件がそろうと `dist/` に公開用HTML/CSS/JavaScriptと必要な素材だけを作成する。写真はコピー後もSHA-256で一致を確認する。
`docs/`、`design/`、`qa/` や第三者の未公開情報を公開サイトへ移さない。

## 引き継ぎ用ZIP

`python scripts/package.py` で作成する。内部限定の創業背景ファイルは自動除外される。
ZIPには制作記録と確認用の原稿を含むため、ZIP全体を公開サイトへ配置しない。公開物は `dist/` だけを使う。

## 文章のレビュー

`python scripts/build.py --mode review` の後に `python scripts/review_copy.py` を実行すると、LP本体から文章を取り出しdesign/copy-review.htmlとdocs/COPY_DRAFT.mdを更新する。画像を省略し、開閉内の文章を含めて一覧で読める。文章の修正はsite/content.jsonへ戻し、再生成する。storyConfirmed/practiceConfirmedは新規の原点・業務姿勢の確認状態。確認前はfalseを維持する。

## 掲載文をまとめて編集する

`python scripts/export_copy_editor.py` でdocs/COPY_EDIT.txt、design/copy-editor.html、design/copy-edit-map.jsonを生成する。番号と項目名を残して本文を編集し、全文をチャットへ返送する。削除希望は本文を「【削除】」にする。

編集用HTMLはローカルで完結し、保存ボタンから編集済み全文をTXTでダウンロードする。自動保存・通信・LPへの自動反映はない。ユーザーから返送された編集済みファイルを生成処理で上書きしない。対応表と基準版を使って原文との差分を確認し、本文・固定文言の掲載箇所へ反映してプレビューを更新する。原稿の変更だけで掲載条件の確認フラグを変更しない。

## SEOと初回演出

SEO設定はcontent.jsonのseoとpublication.siteUrl。公開URLが決まると公開版だけcanonical・OG URL・サイトマップ・robotsを生成する。SEO.mdを参照。

showAboutSection=falseで中段OUR STORYは非表示。冒頭のブランド文はstoryPlacement=heroで継続。初回演出は候補選択待ちで未実装。候補番号と内容はEFFECT_OPTIONS.txtへ記録し、実装時に選択番号を工程へ追記する。

## スマホでの演出比較

HTMLの演出ボタンが動かない場合はscripts/render_effect_videos.pyでMP4とGIFを書き出す。MP4はH.264 Baseline/yuv420p/faststartで提供。チャットのGIF表示と動画リンクを併用し、ユーザー端末での実再生が確認できたとは説明しない。比較動画とLP本体のプレビューは区別し、LPプレビューはHTMLを主に渡す。

## 最新のマーク演出候補

旧0.7秒案はEFFECT_OPTIONS_V2.txtの新版1.2秒案へ更新。scripts/render_mark_effects.pyでマーク自体を動かす比較用HTMLと、チャット内用GIF・コマ送りPNGを生成する。0.8秒で正式形状へ戻し、1.2秒で本文へ完全に切り替える。候補番号が選ばれるまで実LPへ適用しない。
