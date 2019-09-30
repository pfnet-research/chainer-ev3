# ※現在はアフレル様よりGoogle Colabを利用した環境構築手順が提供されています。

# EV3の環境構築（自分のPCでビルドを行う場合）

- 準備するもの
  - PC （Windows/Mac OS/Ubuntu） 1台（コマンドライン環境の使えるもの）
  - micro SDカード （32GB) 1枚
  - micro SD カードリーダー 1個 (PCに備え付けの場合は不要）
  - 教育版レゴマインドストーム EV3
  
- 用意したPCにgitのインストールを行ってください。

- このレポジトリのクローンをします。
  ```
  $ git clone git@/pfnet-research/chainer-ev3.git
  ```
  
- ev3rt-beta7-2-release.zipを[こちら](https://dev.toppers.jp/trac_user/ev3pf/wiki/Download#%E3%83%80%E3%82%A6%E3%83%B3%E3%83%AD%E3%83%BC%E3%83%89)からPCへダウンロードして展開します。
  
- 用意したPCにEV3アプリの開発環境を構築します。環境構築方法はPCの各OSごとに異なります。
  - [MacOS](https://dev.toppers.jp/trac_user/ev3pf/wiki/DevEnvMac)
  - [Windows](https://dev.toppers.jp/trac_user/ev3pf/wiki/DevEnvWin)
  - [Ubuntu](https://dev.toppers.jp/trac_user/ev3pf/wiki/DevEnvLinux)

- chainer-ev3アプリのビルド、コピーを行います。
  ```
  $ cd /PATH/TO/ev3rt-beta7-2-release/hrp2/sdk/workspace
  $ cp -r /PATH/TO/chainer-ev3/ev3/chainer-ev3 ./
  $ make app=chainer-ev3
  $ cp app /PATH/TO/ev3rt-beta7-2-release/sdcard/ev3rt/apps/chainer-ev3
  ```
  
- SDカードへのアプリのコピー
  - `/PATH/TO/ev3rt-beta7-2-release/sdcard/*` 以下をSDカードへコピーします。
  
- EV3にSDカードを差し込み、アプリchainer-ev3が実行できるか確認してください。
