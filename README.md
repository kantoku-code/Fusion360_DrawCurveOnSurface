# **Fusion360_DrawCurveOnSurface**
Autodesk社 ソフト <b>"Fusion360" </b> のアドインです。

## 特徴:
スケッチ作業時に、指定した面上に線を描くためのコマンドです。


## 設置:
こちらの手順に従い、アドインとして「DrawCurveOnSurface」フォルダを追加してください。

[Fusion 360にアドインまたはスクリプトをインストールする方法](
https://knowledge.autodesk.com/ja/support/fusion-360/troubleshooting/caas/sfdcarticles/sfdcarticles/JPN/How-to-install-an-ADD-IN-and-Script-in-Fusion-360.html)

## 使用:
アドイン実行すると、スケッチ作業時の「スケッチ」タブの「作成」の一番下に「面上の線」
コマンドが追加されます

![追加コマンド](./images/toolpanel.png)

コマンド実行時は以下のダイアログが出ます。

![ダイアログ](./images/dialog.png)

予め線を描く面を選択し、境界の頂点を2ヶ所選択することで、2点間の最短を結ぶ線を
面上に描きます。

出来上がる線は「3Dジオメトリを含める」コマンドで作成したものと同等です。
コンテキストメニューの「リンクを解除」を行う事で、移動が可能となります。

![ダイアログ](./images/removeLink.png)


## 動作:
以下の環境にて確認。
+ Fusion360 Ver2.0.8156
+ Windows10 64bit Home

## ライセンス:
MIT

## 残された問題:
+ 境界上の点以外の選択を可能にする
+ プレビューの線が細い
+ Macでの動作未確認

## 謝辞:
+ こちらの便利な[フレームワーク](https://github.com/tapnair/Fusion360AddinSkeleton)を試用しました。
 Patrick Rainsberryさん、ありがとう。
+ [日本語フォーラム](https://forums.autodesk.com/t5/fusion-360-ri-ben-yu/bd-p/707)の皆さん、ありがとう。
+ アイコンが貧弱なので、センスの良い方提供して頂けると助かります・・・。