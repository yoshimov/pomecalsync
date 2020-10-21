PomeCalSync
===========

## 概要

　ポメラDM100, DM200のカレンダーメモを、指定したGoogleカレンダーに同期するツールです。
　動作確認はDM100で行っています。

## インストール

　以下の場所からダウンロードしたpomecalsync.exeを適当なフォルダに置いて実行してください。
　同じフォルダに設定ファイルやトークンなどが保存されます。

- <https://github.com/yoshimov/pomecalsync/releases>

## 使い方

　最初に使うときはブラウザが開いて、Googleカレンダーへのアクセス許可を求める画面が表示されますので、承認してください。二回目以降は承認作業は不要です。
　カレンダーへのアクセスが許可されると、お使いのGoogleカレンダーの一覧がリストで表示されます。ポメラをPCに接続してPCリンクモードにした後、メモの同期先のカレンダーを選択して「Start Sync」ボタンを押すとカレンダーメモがGoogleカレンダーに同期されます。

## 注意点

- メモは「memo」という名前の予定としてGoogleカレンダーに登録されます。
- Googleカレンダーに登録されたメモはポメラから削除されます。
- 直近３日間のメモは同期されません。
- Googleカレンダーのメモを変更しても、ポメラには反映されません。

## ビルド

　以下のコマンドで実行ファイルを作成できます。

> pyinstaller main.spec

## ライセンス

本ツールはMIT Licenseです。
自由に配布、改変してください。
