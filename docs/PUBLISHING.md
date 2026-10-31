# LIBRIGHT LP 公開引き継ぎ

更新：2026-10-31。ユーザーは「Instagramへの誘導なので行けると思います。続けてお願い」とGitHubでの無料公開を改めて指示した。公開先はGitHub Pagesで手続きを進める。公開用ファイルと検証は完了したが、GitHub APIの権限不足で新規リポジトリ作成・Pages設定ができず、現在は未公開。必要な所有者操作と次の作業を末尾に記録する。

## 今回の公開方針

制作ソースは `lupisflora-n/nkmc-repair-lp` の非公開管理を維持する。制作メモ・編集原稿・ブランドの再編集資料・Git履歴を含む既存リポジトリ全体の公開設定は変更しない。公開用の別リポジトリには `python scripts/build.py --mode release` が生成した `dist` の配信物だけを入れる。配信用リポジトリは `lupisflora-n/libright`、予定URLは `https://lupisflora-n.github.io/libright/`。この準備時点では未作成であり、Pagesの設定・公開URLは実際の作成結果を確認して記録する。

サイトは住宅リペアのサービス・施工例を紹介し、ユーザー指定のInstagramプロフィールへ案内する静的ページ。ページ内で注文、予約、支払い、個人情報の送信を受け付ける機能は追加しない。相談文コピーは端末内で実行し、DMをこちらから送らない。

GitHub Pages公式には次の利用制限がある。

> GitHub Pages is not intended for or allowed to be used as a free web-hosting service to run your online business, e-commerce site, or any other website that is primarily directed at either facilitating commercial transactions or providing commercial software as a service (SaaS).

出典：<https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits>

この制限はInstagram等への外部リンクがあれば自動的に対象外になるという規定ではない。ユーザーは説明を受けたうえで現在の紹介ページとして公開を継続する意向を示したため、今回の指示に従って手続きを進める。GitHubによる個別の適合確認・承認を得たとは説明しない。前版の「GitHub Pagesは選ばない／Cloudflare必須」という制作判断は今回の指示で置き換える。GitHubから指摘や技術的制限が出た場合は、それを記録して対応し、別サービスを勝手に契約しない。

## 掲載内容を公開版へ移す

公開データは `site/content.json`。既存の確認フラグには、承認済みの作業後も未更新のものが残っている。ユーザーの写真差し込み指示と「OK」、掲載文を一括編集して返した原稿の反映指示、TRC紹介の再構成指示、今回の公開継続指示を根拠として、公開範囲と移行の記録を残す。フラグを変えたこと自体を事実の独立検証として扱わない。

- 写真は3組6枚を使用し、タイトル・説明・前後の組み合わせを現確認版から引き継ぐ。元ファイルのSHA-256一致を保ち、トリミング、補正、圧縮、形式変換、再エンコードをしない。
- 冒頭に移動したブランド文と原点本文、OUR APPROACH、HOW TO REQUEST、FAQを維持する。中段OUR STORYは削除指示どおり復活させない。
- TRC・RBS紹介は旧版では `partnerIntroduction.reviewDraft` と確認版専用分岐にあった。これを `partnerIntroduction.content` と共通レンダーへ移し、現在の文・配置・RBSとTRCへの2本の案内リンクを正式掲載する。公開版では「紹介文案」「最終確認前」の制作注記を外す。
- TRCの公認、雇用、大手メーカーとの直接取引等の新しい主張を加えない。ユーザー提供の背景と、調査済みの公開情報の範囲を守る。
- 料金、住所、電話、返信時間、保証等の未確定情報は引き続き非掲載。仮の値で埋めない。
- Instagram窓口の指定は今回のユーザー発言でも確認済み。URLは `https://www.instagram.com/libright_chiba/`。`profileUrlConfirmed=true` はユーザー指定URLと窓口採用の根拠を表す。実機DM経路の検証を表す `linkVerified` は未検証のまま `false` を維持する。プロフィールへの遷移と実際のDM経路の検証範囲を区別し、未検証の画面を確認済みと記録しない。DMや外部メッセージは送信しない。

## 公開用ビルドと配信物

正式URLが決まったら `publication.siteUrl` に設定する。`hostingConditionsChecked` は技術設定と利用条件の確認記録を伴って更新し、GitHubが個別承認したという意味にしない。必要な写真・文章・窓口の公開設定を反映し、次を実行する。

```sh
python scripts/build.py --mode release
```

出力の `dist` だけを配信用リポジトリへ登録する。`.nojekyll` を含め、HTML/CSS/JSと実際に参照される素材に限定する。確認版HTML、`dist-review`、`docs`、原稿、フォント本体、ブランドの再編集資料、ZIP、内部限定の創業背景を移さない。

現在の表示に必要な素材は、施工JPEG6枚、横ロゴSVG2枚、シンボルSVG1枚、favicon SVGとPNG各1枚の計11ファイル。使用SVGは文字アウトラインで、外部フォントや外部ファイルを参照していない。ロゴ使用の根拠は制作リポジトリ内のライセンス資料に保管する。

配信用リポジトリのPages配信元は、実際に作成したブランチのルートを選ぶ。無料プランでの可否と現在のAPI権限は実アカウントで確認する。公開済みでないURLを公開完了として渡さない。

## 公開前後の検証

公開版のHTMLについて、確認版との本文・順序の差分を点検する。意図した差分は制作確認バー、再生操作、TRC紹介の制作注記の除去と、公開URLに合わせたSEOタグ等である。

確認する項目：

- `index,follow`、canonical、OG URL、JSON-LD、`sitemap.xml`が実際の正式URLを指している。
- GitHubプロジェクトPagesのサブディレクトリでもCSS、JS、画像、ページ内リンクが解決する。
- `robots.txt` はオリジン直下でのみ参照されるため、プロジェクト配下の配置だけでクロール制御が有効とは説明しない。Search Consoleへの登録・送信は別作業。
- 施工写真6枚の全体表示・元ファイル一致、横ロゴの比率・サイズ、320/390/768/1440px表示。
- 2番のマーク演出は合計2.4秒。開始保持0.3秒、復元1.2秒、完成保持0.5秒、フェード0.4秒。低減モーション、スキップ、JavaScript無効時も本文が見える。
- 写真拡大、閉じる操作、相談文コピーと代替手段、FAQ、Instagramプロフィールへのリンク。
- 公開URLがHTTPSでHTTP 200を返し、公開した写真のバイト列が制作元と一致する。
- 制作メモ、未確認注記、個人情報、秘密情報が配信物に混入していない。

GitHub Pagesのデプロイ完了と実URLの表示確認を別々に記録する。実機スマホ、Instagramログイン後のDM画面、問い合わせ送受信、検索掲載の結果は、確認できたものだけを記録する。

## 更新と復旧

本文は非公開制作リポジトリの `site/content.json`、構造は `site/template.html`、表示は `site/styles.css`、操作は `site/app.js` で変更する。公開用ビルドと必要な検証後、配信用リポジトリに生成物を反映する。配信リポジトリに直接加えた変更は制作ソースにも戻し、次回ビルドで失わないようにする。

不具合があれば、配信用リポジトリで直前の正常な配信物へ戻し、GitHub Pagesで再配信する。Git履歴の強制書き換えをしない。有料プラン・独自ドメイン・外部サービスへの移行は自動で行わない。

## 作業結果と権限の制限

2026-10-31、主担当がGitHub APIへ実際にリクエストした結果：

- `POST /user/repos`（配信用のPublicリポジトリ `libright` の作成）：HTTP 403、`Resource not accessible by integration`。
- `POST /repos/lupisflora-n/nkmc-repair-lp/pages`（接続済みリポジトリのPages設定）：HTTP 403、`Resource not accessible by integration`。既存リポジトリの公開範囲は変更していない。

これは現在の接続にある操作権限の制限であり、サイト内容についてGitHubが個別審査・却下した結果とは扱わない。利用可能なブラウザ操作ツールも見つからず、所有者の画面操作を代行できる状態ではなかった。権限を迂回する手段は取っていない。

配信用リポジトリ `lupisflora-n/libright` は未作成であり、予定のPages URLも未公開。ユーザーには、[GitHubの新規作成画面](https://github.com/new?name=libright&visibility=public)で空のPublicリポジトリを作成し、CodexのGitHub接続対象へ追加する操作を依頼済み。サイト公開と掲載への許可は受領済みのため、同じ許可を改めて求める必要はない。

公開用ビルドの残件は0。独立点検で確認版と公開版の `<main>` 内HTML完全一致、写真6枚の元バイト・SHA一致、必須素材11点＋HTML/CSS/JS/SEO/`.nojekyll`の計17ファイルのみ、TRC/RBS案内2リンク維持、OUR STORYと制作注記の除去、予定URLでのSEO設定を確認済み。ローカルの完成はWeb配信完了を意味しない。

## 再開時の具体的手順

1. ユーザーが `lupisflora-n/libright` をPublicで空の状態にして作成し、CodexのGitHub接続でそのリポジトリを選択する。非公開の制作リポジトリをPublicへ変更しない。
2. 主担当が新しいリポジトリへの読み書きを確認し、用意した配信物17ファイルだけを `main` のルートへpushする。内部資料や制作ソース全体は移さない。
3. 主担当がPublic配信リポジトリのPages設定を試す。現在の接続で引き続き403となる場合、ユーザーが対象リポジトリの **Settings → Pages → Build and deployment** で **Source: Deploy from a branch / Branch: main / Folder: /(root)** を選びSaveする。`main` は配信物をpushした後に選択できる。
4. 主担当がPagesのビルド完了と実URLのHTTPS応答を確認し、`https://lupisflora-n.github.io/libright/` の表示・素材・演出・相談リンクを検証する。設定前や404の段階で公開完了と案内しない。
5. 実際の配信コミット、デプロイ結果、公開URLをこの資料と `docs/WORKFLOW.md` へ追記する。別の公開名・URLとなった場合はcanonical/OG/sitemapも一致させて再ビルドする。

この段階で必要なのはGitHub所有者によるリポジトリ作成・接続対象の指定であり、Cloudflare等の別サービスへの移行承認ではない。
