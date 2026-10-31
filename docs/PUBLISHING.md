# LIBRIGHT LP 公開手順と現在地

更新：2026-10-31。ユーザーの「repairctのLPと同じようにして公開」に従い、既存の `lupisflora-n/nkmc-repair-lp` にGitHub ActionsからGitHub Pagesへの配信を実装済み。GitHub上でビルド成功、Pages初期設定が未有効のためデプロイ失敗。まだWeb未公開。

## repairctで確認した方式

- 参照元：`lupisflora-n/repairct`（Public、has_pages=true）。GitHubコネクタでREADME、docs/github-pages.md、.github/workflows/pages.ymlを取得した。
- repairctはmainへのpushでactions/configure-pages@v5 → actions/upload-pages-artifact@v3 → actions/deploy-pages@v4を実行する。GitHub側の初回設定はSettings → Pages → Source: GitHub Actions。
- LIBRIGHTでは同じ配信方式を採用し、公開対象をリポジトリ全体ではなくrelease生成物のdistだけに限定した。別の公開用リポジトリを先に作ることは現在の必須手順としていない。

## LIBRIGHTの設定

- 制作・配信設定のリポジトリ： https://github.com/lupisflora-n/nkmc-repair-lp
- ワークフロー： `.github/workflows/pages.yml`
- 予定URL： https://lupisflora-n.github.io/nkmc-repair-lp/ （現在未公開）
- mainのsite/scripts/tests/workflow変更をpushすると起動。workflow_dispatchで手動起動もできる。
- buildジョブ：Python 3.12 → 7単体テスト → python scripts/build.py --mode release → distのみPages artifactへアップロード。
- deployジョブ：Pages設定確認 → GitHub Pagesへ配信。必要なpages:writeとid-token:writeをこのジョブに限定。
- GitHub Actions側でテスト・写真検証・生成・アップロードまで成功した。写真は6枚とも元ファイルのままで、SHA-256が一致する。
- 既存リポジトリの可視性はPrivateのまま。制作メモを含むリポジトリ全体のPublic化やGit履歴書き換えはしていない。

## 実行結果と止まっている箇所

対象コミット：a1a70e27692f3793b3741402b6b9e05f18095e49

実行： https://github.com/lupisflora-n/nkmc-repair-lp/actions/runs/41151444803

- buildジョブ成功。deployジョブのSet up Pagesが失敗し、公開ステップはskip。
- ログ：`Get Pages site failed. Please verify that the repository has Pages enabled and configured to build using GitHub Actions` / `Not Found`。
- 管理APIは以前の実リクエストでPOST /user/reposとPOST /repos/lupisflora-n/nkmc-repair-lp/pagesが403 Resource not accessible by integration。現在のGitHub接続はリポジトリへのコミットは可能だが、Pagesの初回管理設定は操作できない。
- actions/configure-pagesのenablement入力の公式定義も確認。自動有効化にはGITHUB_TOKEN以外のトークンが必要で、GitHub Appではadministration:writeとpages:writeが必要。単にenablement:trueを設定して回避しない。

## 所有者にお願いしている初回設定

https://github.com/lupisflora-n/nkmc-repair-lp/settings/pages

Sourceを **GitHub Actions** にする。設定後、主担当が失敗したdeployジョブだけ再実行し、実URLと公開内容を確認する。Pages artifactが期限切れならワークフロー全体を再実行する。

GitHub FreeではPublicリポジトリがPagesの対象であり、PrivateリポジトリのPagesには対応プランが必要。repairctがPublicである一方、nkmcはPrivateである点は残る。画面で有料プランを案内された場合は、無料運用の希望を守り契約せず、表示内容を確認する。制作メモを含む元リポジトリを丸ごとPublicへ変更する手順は案内しない。必要なら公開用ファイルだけを入れる別Publicリポジトリを所有者が作成する代替へ切り替え、URLを合わせ直す。

現在はユーザーにこの設定の実施可否・案内文の返信を依頼中。Pages未設定・404・ビルド成功だけの段階で「公開完了」と報告しない。

## 掲載内容と素材の管理

ユーザーによる写真差し込みとOK、編集原稿の反映、TRC紹介再構成、公開継続の指示を根拠に公開設定を更新済み。この更新は第三者による個別許諾取得や業務実態の独立検証を意味しない。

- `partnerIntroduction.content`：現在のTRC/RBS原稿を確認版・公開版で共通利用。本文と2つの公式案内リンクを欠落させない。
- 写真3組・6枚、ブランド本文、姿勢、施工の流れ、FAQを確認版と同じ内容で維持。OUR STORYは非掲載。制作確認バーと紹介文案注記は公開版から除去。
- `contact.profileUrlConfirmed=true`：ユーザー指定URLと採用窓口の確認。`contact.linkVerified=false`：実アカウントのDM到達は実機未確認。検証のためのDMは送らない。
- distはHTML/CSS/JS/SEO/.nojekyllと必要素材11点の計17ファイルだけ。docs、design、qa、編集原稿、ブランド再編集資料、私的な創業背景、Git履歴をWeb配信しない。
- 単体HTMLの確認用書き出し：`python scripts/build.py --mode release --standalone-output design/release-preview.html`。通常配信版の画像は元ファイルをそのまま参照する。

## 利用条件の確認記録

GitHub公式はオンラインビジネスや商取引促進を主目的とする無料ホスティングへの制限を定めている。

> GitHub Pages is not intended for or allowed to be used as a free web-hosting service to run your online business, e-commerce site, or any other website that is primarily directed at either facilitating commercial transactions or providing commercial software as a service (SaaS).

https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits

外部Instagramリンクがあれば自動的に対象外になるという規定ではない。ユーザーは説明後、現在の事業紹介・Instagram案内構成でGitHub公開を続行する意向を示した。GitHubから個別の適合承認を得たとは説明しない。hostingConditionsCheckedは利用条件の確認記録であり、配信成功を意味しない。別サービスへ勝手に切り替えたり有料契約したりしない。

## 公開後の確認

HTTPS 200、マーク演出2.4秒から本文への遷移、スマホ表示、写真6枚の全体・拡大表示とSHA一致、相談文コピーと代替、FAQ、Instagramプロフィール宛先、canonical/OG/sitemapと実URLの一致を確認する。Search Consoleの操作は未実施。運用時はmainの該当ファイル変更が本番配信につながるため、公開前に差分とテストを確認する。
