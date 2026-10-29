# LIBRIGHT｜リブライト ロゴ・マーク

採用案「仕上げの一筆」。白黒を基調に、黄色 `#F3C63A` と赤 `#C54136` を差し色として使用します。

## フォルダ

- `logos/svg/`：シンボル・文字ロゴ・横組み・縦組み・日本語併記の5形態 × カラー・黒・白の15種類。文字までパス化された実ベクター。
- `logos/png/`：よく使う5種類の高解像度・背景透過PNG。LPでの通常表示はSVGを推奨。
- `icons/`：Instagram正方形画像とSVG/PNG/ICOのfavicon。16〜32pxのfaviconは判別性のため筆先を省略した専用版。

## 推奨する使い分け

- 白・淡色の背景：`logos/svg/horizontal-jp-color.svg` または `logos/svg/horizontal-color.svg`
- 暗い背景：`logos/svg/horizontal-jp-white.svg`
- 狭い表示：`logos/svg/symbol-color.svg`
- Instagram：`icons/instagram-1024.png`
- ブラウザタブ：`icons/favicon.svg`、予備として`favicon.ico`

ロゴの縦横比・色を勝手に変更しないこと。推奨最小幅や余白は`design/brand/libright/brand-guide.pdf`を参照してください。編集可能なSVGとフォント使用情報は`design/brand/libright/`にあります。

**実装状況：** ヘッダーに横組みカラー、冒頭にシンボル、濃色フッターに横組み白抜き、ブラウザタブに専用faviconを反映済み。`brand.assetsReady` はtrue。320〜1440pxで画像読み込み、横ロゴ幅220px以上、元の縦横比を確認済み。元のロゴファイルは変更していません。
