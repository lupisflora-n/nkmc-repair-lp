# LIBRIGHT LP 公開手順と現在地

更新：2026-10-31。ユーザーは「NKMCの方で変えた」と公開先を指定。現在は既存のnkmc-repair-lpからGitHub Actions→Pagesで公開を進める。Public化とPagesのSource設定を確認し、再実行に成功。現在Web公開済み。

## 現在の公開先

- リポジトリ： https://github.com/lupisflora-n/nkmc-repair-lp
- Pages初回設定： https://github.com/lupisflora-n/nkmc-repair-lp/settings/pages
- 公開URL： https://lupisflora-n.github.io/nkmc-repair-lp/
- 配信設定： .github/workflows/pages.yml
- 対象run： https://github.com/lupisflora-n/nkmc-repair-lp/actions/runs/41151444803

ユーザーが所有者画面でPrivateからPublicへ変更した。当方は公開範囲を変更していない。GitHub FreeのPagesを使うにはPublicが必要。元repoは制作記録も含めリポジトリ経由で公開されるため、新たな内部限定情報はGitへ加えない。私的な創業背景ファイルは従来どおり.gitignoreで除外する。現在このrepoから配信するため、Privateへ戻すと無料Pagesには影響する。

## repairctと同じ方式

PublicのrepairctのREADME・初回手順・workflowをGitHubコネクタで確認済み。mainの変更からActions→Pagesで配信する構成を採用した。

- buildジョブ：Python 3.12、7単体テスト、元写真のSHA検証付きrelease生成、distだけPages artifactへ。
- deployジョブ：configure-pages@v5 → deploy-pages@v4。公開対象は生成物17ファイルだけ。
- mainのsite/scripts/tests/workflow変更で起動。workflow_dispatchにも対応。
- リポジトリ全体をPagesへアップロードしない。docs/design/qa/編集原稿/再編集素材/Git履歴をWeb配信しない。ただしPublic repo自体からはGitに登録済みの制作資料が閲覧可能である点を区別する。

## 実行結果

- 初回commit a1a70e27692f3793b3741402b6b9e05f18095e49のrun 41151444803でbuild成功。Set up PagesがNot Foundで失敗。
- 「NKMCの方で変えた」の返信後、Public化を確認し同runを再実行した。新job 124392558348もSet up PagesでNot Found、公開はskip。buildは成功している。
- ログ：`Please verify that the repository has Pages enabled and configured to build using GitHub Actions`。
- 管理APIへのPOST /repos/lupisflora-n/nkmc-repair-lp/pagesは403 Resource not accessible by integration。現在の接続はコミット・Actions再実行は可能だがPagesの初回管理設定はできない。

所有者がSourceをGitHub Actionsに設定後、run 41151444803を再実行。deploy job 124393084285が成功し、公開URLのHTTPS 200を確認した。公開HTMLとローカルの検証済みreleaseがバイト一致、配信された写真6枚のSHAが元ファイルと一致することを確認。

configure-pagesのenablement入力はGITHUB_TOKEN以外の管理権限付きトークンが必要。フラグだけで有効化できると仮定しない。別サービスへの変更・有料契約・Git履歴の強制書き換えはしない。

## 別リポジトリlibrightの扱い

同じユーザー操作の後、空のPublicリポジトリlupisflora-n/librightも作成されていた。その時点で公開配信物17＋Pages workflowの計18ファイルを初回commit 3190f88f878895b6577de69c0aa283e24402e194としてpushした。

librightのrun 41152414796もPages初回設定未有効で失敗。ユーザーがその後NKMC側を指定したため、現在librightのPages設定を依頼したり、こちらへデプロイしたりしない。作成済みファイルは勝手に削除せず残している。公開用ファイルだけで制作メモは含まない。主担当の作業先を混同しない。

## 掲載内容・検証

- 確認版と公開版のmainの本文・構造を一致させ、写真3組、ブランド本文、TRC/RBSの2リンク、姿勢、施工の流れ、FAQを保持。OUR STORYは非掲載、制作確認注記は公開版から除去。
- 写真6枚は元ファイルとSHAが一致。加工・圧縮・形式変換なし。
- 掲載可否は写真差込とOK、編集原稿反映、TRC再構成、公開指示を根拠とする。独立した第三者承認や実績検証を取得したという意味ではない。
- contact.profileUrlConfirmed=trueは指定プロフィールURLの採用確認。linkVerified=falseは実機DM到達未検証。検証のためのDMは送らない。
- 2.4秒演出と本文UIに変更なし。同一の合格済みローカルブラウザ試験は理由なく反復せず、配信後の実URL確認を行う。

## 更新と公開後確認

両チャットによる変更を取り込み、site/content.json等を編集。必要なテストと `python scripts/build.py --mode release` を実行後、nkmc/mainへpushする。distがGitHub Actionsで生成されPagesへ自動反映される。単体HTMLの確認版は `python scripts/build.py --mode release --standalone-output design/release-preview.html`。

公開後はHTTPS 200、マーク演出から本文、スマホ表示、写真6枚の全体・拡大・SHA一致、コピーと代替、FAQ、Instagram宛先、canonical/OG/sitemapと実URL一致を確認。Search Consoleは未実施。

## 利用条件の記録

https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits のオンラインビジネス等を主目的とする無料ホスティング制限は確認済み。外部Instagramリンクがあれば自動的に対象外になる規定ではない。ユーザーは説明後、現在の紹介・Instagram案内構成で公開続行を指示した。GitHubによる個別適合承認を取得したとは説明しない。

## 公開完了と実URL検証（2026-10-31）

https://lupisflora-n.github.io/nkmc-repair-lp/ で公開完了。

- run 41151444803の最終再実行はbuild/deploy成功。deploy job 124393084285成功。
- 公開HTMLが検証済みreleaseとバイト一致。写真6枚はHTTPS取得後のSHAが元ファイルと一致。
- 390/1440pxで横はみ出しなし、演出終了・写真拡大・FAQ・相談文コピー・Instagramプロフィール宛先・canonicalを確認。JS例外なし。
- 検証環境のChromiumにはプロキシCAが未登録のため、直接のHTTPSナビゲーションは証明書エラー。TLS検証を有効にしたurllibで実URLの応答を取得し、その元応答をChromiumへ渡して描画・操作した。HTTPS検証を無効化していない。ユーザーのスマホ実機での表示とDM到達、Search Consoleは未実施。
- ローカルの結果はqa/live-report.json（Git対象外）。更新後もmain→GitHub Actions→dist限定Pages配信を維持する。
