# NKMCリペアLP

LIBRIGHT（リブライト）のLP制作案件。工務店・建築会社からの継続的な補修依頼を最優先とする。

- 制作方針・決定事項: [docs/PROJECT.md](docs/PROJECT.md)
- 工程・現在地・次の作業: [docs/WORKFLOW.md](docs/WORKFLOW.md)
- 法人向け構成・原稿の初稿: [docs/COPY_DRAFT.md](docs/COPY_DRAFT.md)
- 施工写真の受領・観察台帳: [docs/PHOTO_REGISTER.md](docs/PHOTO_REGISTER.md)
- 最新の操作できる確認版（単体HTML）: [design/preview.html](design/preview.html)
- 初期の画面ラフ: [design/review.html](design/review.html)
- 検証結果と残る項目: [docs/QA_REPORT.md](docs/QA_REPORT.md)
- 差し替え・公開準備の引き継ぎ: [docs/UPDATE_GUIDE.md](docs/UPDATE_GUIDE.md)
- 別チャット用ロゴ制作依頼: [docs/LOGO_PROMPT.txt](docs/LOGO_PROMPT.txt)
- 制作中のロゴチャットへの追加ブリーフ: [docs/LOGO_CONCEPT_ADDENDUM.txt](docs/LOGO_CONCEPT_ADDENDUM.txt)
- 公開情報の差し替え用データ: [site/content.json](site/content.json)
- 参照資料と確認範囲: [docs/SOURCES.md](docs/SOURCES.md)

現段階は静的LPの確認版実装と表示・基本操作の検証まで完了。写真3組・計6枚は会話内で目視確認済みだが、サイトへ組み込む元画像の実ファイルは未取得のため配置枠を表示。
対外ブランドの軸は「傷を直す。その先の、晴れやかな暮らしまで。」。創業者の私的な背景は公開用ファイルや配布用ZIPへ含めない。
写真はユーザー指示により編集・変更禁止。元ファイルのまま、全体と縦横比を保って表示する。
ロゴ、公開リポジトリ、公開URLは未完成・未確定。公開用ビルドは確認事項がそろうまで停止する。
GitHubでのソース管理と無料公開が希望。GitHub Pagesの利用条件への適合性は確認事項として残す。

`docs/`、`design/` と `AGENTS.md` は内部制作記録・確認用資料。公開サイトにはそのまま配信しない。
`python scripts/build.py --mode review` で `site/content.json` の内容をHTMLへ反映する。相談文コピーとFAQを実装済み。
本番用は `python scripts/build.py --mode release`。未確定のまま公開しない。

## GitHub管理への移行

接続先はlupisflora-n。非公開リポジトリnkmc-repair-lpへの移行を準備中。現在の連携では新規作成権限が不足しており、リモートは未作成・未アップロード。空の非公開リポジトリ作成後にソースを登録する。
内部限定の創業背景ファイルは.gitignoreで除外する。Web公開の設定は未実施。
