# NKMCリペアLP

LIBRIGHT（リブライト）のLP制作案件。工務店・建築会社からの継続的な補修依頼を最優先とする。

- 制作方針・決定事項: [docs/PROJECT.md](docs/PROJECT.md)
- 工程・現在地・次の作業: [docs/WORKFLOW.md](docs/WORKFLOW.md)
- 法人向け構成・原稿の初稿: [docs/COPY_DRAFT.md](docs/COPY_DRAFT.md)
- 施工写真の受領・観察台帳: [docs/PHOTO_REGISTER.md](docs/PHOTO_REGISTER.md)
- 最新の操作できる確認版（ロゴ・施工写真反映済み）: [design/preview.html](design/preview.html)
- GitHubで見られるスマホ・PCプレビュー画像: [design/previews/](design/previews/README.md)
- 初期の画面ラフ: [design/review.html](design/review.html)
- 検証結果と残る項目: [docs/QA_REPORT.md](docs/QA_REPORT.md)
- 差し替え・公開準備の引き継ぎ: [docs/UPDATE_GUIDE.md](docs/UPDATE_GUIDE.md)
- 別チャット用ロゴ制作依頼: [docs/LOGO_PROMPT.txt](docs/LOGO_PROMPT.txt)
- 制作中のロゴチャットへの追加ブリーフ: [docs/LOGO_CONCEPT_ADDENDUM.txt](docs/LOGO_CONCEPT_ADDENDUM.txt)
- 公開情報の差し替え用データ: [site/content.json](site/content.json)
- 参照資料と確認範囲: [docs/SOURCES.md](docs/SOURCES.md)

現段階は静的LPの確認版実装と表示・基本操作の検証まで完了。施工写真3組・計6枚を無加工で配置済み。原ファイルとのSHA-256一致、スマホ・PCの全体表示と拡大操作を確認。HTMLとdesign/assetsを一緒にダウンロードする。
対外ブランドの軸は「傷を直す。その先の、晴れやかな暮らしまで。」。創業者の私的な背景は公開用ファイルや配布用ZIPへ含めない。
写真はユーザー指示により編集・変更禁止。元ファイルのまま、全体と縦横比を保って表示する。
正式ロゴをLPへ組み込み、黒白・黄色・赤のブランド配色でレイアウトを再構成。SVGとfaviconの読み込み、320〜1440px幅での表示・操作を確認済み。Web公開URLは未確定。GitHub管理リポジトリは非公開で用意済み。公開用ビルドは確認事項がそろうまで停止する。
GitHubでのソース管理と無料公開が希望。GitHub Pagesの利用条件への適合性は確認事項として残す。

`docs/`、`design/` と `AGENTS.md` は内部制作記録・確認用資料。公開サイトにはそのまま配信しない。
`python scripts/build.py --mode review` で `site/content.json` の内容をHTMLへ反映する。相談文コピーとFAQを実装済み。
本番用は `python scripts/build.py --mode release`。未確定のまま公開しない。

## GitHub管理への移行

管理先: https://github.com/lupisflora-n/nkmc-repair-lp

非公開（Private）、管理ブランチはmain。ユーザーが作成した空のリポジトリへの接続と書き込み権限を確認し、制作ソース・制作方針・工程表をGit管理へ移す。
内部限定の創業背景ファイルは.gitignoreで除外する。Web公開の設定は未実施。

## LIBRIGHTロゴ・制作素材

- Web用素材: [site/assets/brand/libright/](site/assets/brand/libright/README.md)
- ブランドガイド・再編集データ: [design/brand/libright/](design/brand/libright/README.md)
- 今後のアイコン・画像の管理ルール: [site/assets/](site/assets/README.md)

## v0.2 構成と文章の確認

- [文章を一覧で読む](docs/COPY_DRAFT.md)
- [文章確認用HTML](design/copy-review.html)
- [専門担当への再構成指示](docs/RESTRUCTURE_BRIEF.txt)

施工写真→対応内容→短い原点の物語→現場の姿勢→任意のTRC紹介→地域・流れ・FAQ→問い合わせへ再構成。TRC紹介は確認版に文章案を表示し、正式公開は条件確認後。新しい物語と姿勢は確認版の案。

TRCとRBSの紹介根拠・採用情報は[公式調査メモ](docs/TRC_RESEARCH.md)。RBS正式名と公式サイト・YouTubeの案内先を確認版へ反映しています。

## v0.3：実務・TRC紹介の再配置

施工写真→対応内容→原点の物語→現在の実務とTRC/RBSとの関係→現場の進め方→相談に必要な情報の順へ変更。Nさんの実務が主文、TRCとRBSの紹介は下段の独立した枠です。最新の文章はdocs/COPY_DRAFT.md、確認画像はdesign/previews/。
