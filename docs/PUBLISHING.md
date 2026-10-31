# LIBRIGHT LP 公開引き継ぎ

更新：2026-10-31。公開手続きを求めるユーザー指示を受領済み。現在は未公開。GitHub制作リポジトリの公開範囲や、外部サービスのアカウント設定は変更していない。

## 公開先の判断

GitHubは制作ソースの管理先として継続する。既存の `lupisflora-n/nkmc-repair-lp` は非公開を維持し、制作記録を含むリポジトリ全体を公開リポジトリに変更しない。

GitHub Pages公式の「GitHub Pages limits」は、オンラインビジネスの運営や商取引の促進を主目的とする無料ホスティング利用を許可しない旨を定めている。

> GitHub Pages is not intended for or allowed to be used as a free web-hosting service to run your online business, e-commerce site, or any other website that is primarily directed at either facilitating commercial transactions or providing commercial software as a service (SaaS).

出典：<https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits>

本LPは住宅補修の依頼・継続取引の獲得が主目的のため、今回の公開先としてGitHub Pagesを選ばない。これは本案件への適合性に関する制作側の判断であり、GitHubによる個別審査結果ではない。

代替候補は、GitHubの非公開リポジトリに接続して静的ファイルを配信するCloudflare Pages。公式公開ソースで、GitHubのpublic/privateリポジトリ接続、pushに連動したデプロイ、Free枠の月500ビルド・20,000ファイル・各ファイル25MiBの上限を確認した。無料枠を超える構成へ自動的に変更しない。商用用途と適用されるサービス規約・アカウント条件も接続前に確認する。

主担当が2026-10-31に公式ドキュメントの公開ソースを取得。ドキュメントサイトへの直接アクセスは403だったため、GitHub上のCloudflare公式リポジトリを参照した。

- [Pages limits](https://developers.cloudflare.com/pages/platform/limits/) ／ [公式公開ソース](https://raw.githubusercontent.com/cloudflare/cloudflare-docs/production/src/content/docs/pages/platform/limits.mdx)
- [GitHub integration](https://developers.cloudflare.com/pages/configuration/git-integration/github-integration/) ／ [公式公開ソース](https://raw.githubusercontent.com/cloudflare/cloudflare-docs/production/src/content/docs/pages/configuration/git-integration/github-integration.mdx)

Cloudflare無料枠への変更可否はユーザーへ確認中。現時点ではCloudflareのアカウント作成・GitHub接続・プロジェクト作成・デプロイを実施していない。無料でも新しい外部アカウントやサービス契約を無断で作らない。

## 公開前に整えるデータ

公開データは `site/content.json`。`python scripts/build.py --mode release` が残件を表示して停止する場合、確認版を代わりに公開せず、表示された項目を解決する。

- `publication.siteUrl`：実際に使用する正規HTTPS URL。確定後に設定し、仮URLを正式サイトとして配信しない。
- `publication.hostingConditionsChecked`：選んだ公開先の条件と設定を実際に確認してから更新する。
- `cases.publish` と各事例の `confirmed` / `publicationCleared`：ユーザーが写真を提供しLPへの差し込みと公開を指示した履歴を確認し、その指示が認める利用範囲を記録する。単に過去の未更新フラグが残っていることと、実際に未確認の事項を区別する。写真は原ファイルを使用し、SHA-256一致を維持する。
- `contact.channelConfirmedForLp`：LPの窓口としてInstagramを採用する指示・確認履歴を確認する。
- `contact.linkVerified`：指定アカウントのプロフィールから「メッセージ」へ進める実際の経路を確認する。URLが構文的に正しいことだけで確認済みにしない。テストのためのDMは送信しない。

releaseでは確認フラグにより、ブランド原点本文、仕事への姿勢、施工の流れ、TRC紹介等が確認版から非掲載になる場合がある。特にTRCの現行文は `partnerIntroduction.reviewDraft` にあり、確認版専用である。正式掲載内容への移行と根拠の確認を済ませるか、正式公開時に省くことを明確にする。公開ビルドが成功したことだけで、確認版と文章・構成が同じと判断しない。

## Cloudflare Pages接続時の設定案

以下は接続を行う場合の引き継ぎ手順。管理画面の表記や利用条件は実施時の公式資料に照らして確認する。

1. ユーザーの利用可能なCloudflareアカウントを確認し、GitHub連携の許可を得る。GitHub Appのアクセス対象はこの制作リポジトリだけに絞る。
2. 事前にプロジェクト名と予定の `pages.dev` URLを確認し、正規URLを `publication.siteUrl` に設定する。独自ドメインは今回の無料運用の必須条件にしない。
3. 未確認項目の解消前に初回公開が走らないよう、releaseビルドの停止条件を維持する。確認フラグを通すだけの変更はしない。
4. 接続するGitHubリポジトリは `lupisflora-n/nkmc-repair-lp`、本番ブランチは `main`、フレームワークは静的サイトとして設定する。
5. リポジトリのルートをビルドルートとし、ビルドコマンドを `python scripts/build.py --mode release`、出力ディレクトリを `dist` にする。ビルド環境でPython 3.10以上を使用できることを確認する。このビルドに秘密鍵やAPIキーは不要。
6. 配信対象を `dist` に限定する。`design/preview.html`、`dist-review`、`docs`、原稿、制作メモ、Git履歴、ブランド納品ZIP、内部限定の背景情報を配信しない。リポジトリのルート全体をアップロードしない。
7. プレビューブランチの自動配信は必要時だけ有効にする。別URLのプレビューが自動生成される場合は検索対象や共有範囲の扱いを確認する。制作確認版HTMLの `noindex` をアクセス制限の代わりと考えない。
8. デプロイ成功後、正式URLで下記の確認を行い、URLとデプロイ識別子を制作記録へ残す。

## デプロイ前後の確認

ローカルで公開用ビルドを実行し、生成された `dist` について確認する。

```sh
python scripts/build.py --mode release
```

releaseは正式URLに合わせたcanonical、OG URL、構造化データ、`sitemap.xml`、`robots.txt`を生成する。確認版の `noindex,nofollow` が正式HTMLに残っていないこと、本文とTRC紹介の掲載範囲、リンクの整合を確認する。

配信後は、HTTPSのHTTP 200応答、スマホ表示、マーク演出から本文への遷移、写真6枚の全体表示と原ファイルの一致、写真拡大、相談文コピーと代替手段、FAQ、Instagramのプロフィールまでの経路を確認する。正規URLとcanonical・サイトマップの一致も実URLで確認する。Search Consoleの所有権確認・サイトマップ送信は権限がそろった段階で行い、未実施を実施済みと記録しない。

## 変更と復旧

公開後も内容は `site/content.json`、表示は `site/styles.css`、操作は `site/app.js`、構造は `site/template.html` を変更して管理する。GitHubの `main` を更新すると本番へ自動配信される設定にした場合は、その事実をユーザーへ伝え、公開前に差分とビルドを確認する。

問題がある場合は、配信サービスで利用可能な直前の正常デプロイへの復旧方法を確認してから実行する。復旧後もGitHubのソースとの相違を解消し、次の自動配信で問題を再発させない。Git履歴の強制書き換えは行わない。
