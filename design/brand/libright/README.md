# LIBRIGHT｜ロゴ制作・再編集資料（非公開の制作記録）

- `editable/`：シンボル・文字・組み合わせの編集用SVG各色15種類。文字部分の編集にはMontserrat weight 800とNoto Sans JP weight 700が必要。
- `brand-guide.pdf` / `brand-guide.txt`：色（RGB）、余白、最小サイズ、使用上の注意。PDFはRGBです（CMYKの代用ではありません）。
- `licenses-and-sources.txt` / `licenses/`：フォントの入手元、SIL OFL 1.1ライセンス原文、生成方法・未確認事項。
- `reference/selected-05-original.jpg`：クライアントが採用した「仕上げの一筆」の元画像。拡張子を実体のJPEGに合わせています。

Web・LPで表示する実ベクターSVGは `site/assets/brand/libright/logos/svg/` に15種類保存しています。編集作業は `editable/`、表示はアウトライン済みSVGを使ってください。

フォント本体、全16種のPDF書き出し、15種ずつの全PNG・JPEG書き出し、A4一覧のフル納品物は別途作成済みの `LIBRIGHT_Logo_Delivery.zip` にあります。容量と更新の重複を避けるためリポジトリにはWeb用主要素材と再編集資料を収録しています。

ブランドコンセプト（対外向け）：**傷を直す。その先の、晴れやかな暮らしまで。**

既存商標との類似性調査や商標登録可否の確認は未実施です。外部配布・公開や大量印刷前には必要な権利確認と実寸検証をしてください。

## LINE・Instagramアイコン

[アップロード用データ](social-icons/)に、同じSNSデザインの1024px PNGをLINE用・Instagram用の名前で保存しています。SVGと通常カラー透過素材も同梱。正式納品済み素材のバイト列を維持した複製で、使い方とSHA-256を添えています。

## liBright文字入りアイコン

[文字入りPNG](social-icons-with-text/)はユーザー指定でマークの下にliBright表記を加えた別バリエーション。LINE・Instagram用、1254px正方形。生成PNGで、アウトラインSVGではありません。既存の正式SVGとマークのみのアイコンはそのまま保管しています。

## SNSプロフィールアイコンのサイズ別書き出し

LINE 640×640px、LINE 1024×1024px、Instagram 640×640pxのPNGと、LINE用SVGを`site/assets/brand/libright/icons/`へ追加。既存の1024pxマーク単体・「liBright」文字入り版はそのまま保持。使用サイズと仕様の確認メモ：`social-icon-guide.txt`。
