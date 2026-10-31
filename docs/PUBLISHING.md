# LIBRIGHT LP 公開・更新手順

現在のリポジトリは https://github.com/lupisflora-n/libright 。公開URLは https://lupisflora-n.github.io/libright/ 。旧nkmc-repair-lpを所有者が改名した同一リポジトリ（GitHub ID 1438624039）であり、これまでの履歴とPages設定を引き継ぐ。

## 改名への対応（2026-10-31）

ユーザーは未使用だった別repoのlibrightを削除し、NKMC側をlibrightへ改名した。現行repoの同一ID、Public、has_pages=trueをAPIで確認。Git origin、publication.repository/deploymentRepository/siteUrl、canonical/OG/構造化データ/sitemapを新URLへ合わせた。

ローカル制作本体は /workspace/nkmc-repair-lp のまま。/workspace/libright-deploy は削除された旧別repoの古いコピーなので使用しない。誤って現行repoへpushしないよう、この古いコピーのoriginは削除した。既存の履歴を削除・上書きしない。

## 現在の配信方式

- 制作・公開元：lupisflora-n/libright、main、Public。
- .github/workflows/pages.ymlにより、mainのsite/scripts/tests/workflow変更をpushすると検証・release生成・GitHub Pages配信が実行される。
- Python 3.12、単体テスト、元写真のSHA検証付きビルドを実行。distだけをPages artifactとして配信する。
- Settings→PagesのSource: GitHub Actionsは設定済み。新しい公開先を作成したり、この初期設定を再びユーザーへ依頼したりしない。
- distはページ配信物17ファイルのみ。リポジトリ全体は配信しない。ただしリポジトリ自体はPublicなのでGit登録済み資料は閲覧可能。内部限定情報はGitへ追加しない。

## 更新手順

1. git originが https://github.com/lupisflora-n/libright.git であることを確認し、リモートの変更を取り込む。
2. site/content.json、template、CSS、JSを編集し、変更に必要な確認を実行する。
3. python scripts/build.py --mode release でdistを生成。確認用単体HTMLは --standalone-output design/release-preview.html を追加する。
4. mainへcommit/pushし、該当コミットのActions結果を確認する。
5. 実URLの表示・関連操作・原写真一致を確認。CSS/JSは内容ハッシュ付きURLを維持し、旧キャッシュを避ける。

LPのプレビューは写真入りの単体HTMLを基本とし、公開後は実URLも共有する。ブラウザ環境のプロキシCA信頼が使えない場合は、TLS検証を無効化せず、検証済みHTTPS応答をブラウザへ渡して確認した範囲を記録する。

## 維持する内容

- 写真6枚の元バイト・縦横比・全体表示を維持。加工・圧縮・形式変換禁止。
- 冒頭マーク演出2.4秒、スクロール時の写真フレーム950ms/前後140ms差、文章650msを維持。一度表示した箇所は再び隠さない。低減モーション等では通常表示。
- TRC/RBSの紹介2リンク、承認済み本文、コピー/代替、FAQ、Instagramプロフィール宛先を維持。OUR STORYは非掲載。
- 実績や第三者の個別承認を取得したという未確認の説明を追加しない。DM送信とSearch Consoleは未実施。

GitHub Pagesの利用条件に関する以前の確認記録と公開続行指示はPROJECT/WORKFLOWに保存済み。改名はGitHubによる個別適合承認を意味しない。
