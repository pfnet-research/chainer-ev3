# 概要
`chainer-ev3/simulator2d`ではEV3の２次元シミュレーターを提供します。EV3の動作、カメラやカラーセンサーのシミュレーションを行います。

# シミュレーターのセットアップ方法
## 事前準備
- コンソールを開いてコマンドラインベースでセットアップを行います。
- 用意したPCにgitのインストールを行ってください。

- pyenvのセットアップ
  ```
  $ git clone https://github.com/yyuu/pyenv.git ~/.pyenv
  $ echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.profile
  $ echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.profile
  $ echo 'eval "$(pyenv init -)"' >> ~/.profile
  ```

- pyenv-virtualenvのセットアップ

  ```
  $ git clone https://github.com/yyuu/pyenv-virtualenv.git ~/.pyenv/plugins/pyenv-virtualenv
  $ echo 'eval "$(pyenv virtualenv-init -)"' >> ~/.profile
  ```

- Python3のセットアップ

  Python3.6.8をインストール。
  ```
  $ source ~/.profile
  $ pyenv install 3.6.8
  ```
  
- レポジトリのクローンとpython仮想環境の構築
  ```
  $ cd
  $ git clone git@/pfnet-research/chainer-ev3.git

## サンプルコードを動作させるためのpython環境のセットアップ
- pythonの必要パッケージを仮想環境にインストールします。
  ```
  $ cd chainer-ev3/workspace
  $ pyenv virtualenv 3.6.8 chainer-ev3
  $ pyenv local chainer-ev3
  $ pip install --upgrade pip
  $ pip install -r requirements-sim.txt
  ```
  ※ pipでインストールするファイルはrequirements.txtではないことに注意してください。

- JupyterLabを起動します。
  ```
  $ cd ~/chainer-ev3/workspace
  $ jupyter lab
  ```
  次のような画面がブラウザに出てきたら成功です。
  ![my image](jupyterlab.png)
  
## シミュレーターのセットアップ
- JupyterLabを起動したコンソールとは別のコンソールを立ち上げて作業を行います。
- シミュレーターのセットアップを行います。 
  ```
  $ cd chainer-ev3/simulator2d
  $ pyenv virtualenv 3.6.8 simulator2d
  $ pyenv local simulator2d
  $ pip install -r requirements.txt
  $ python setup.py build_ext --inplace
  ```
  
- シミュレーターを起動します。
  ```
  $ python main.py
  ```
  以下のような画面が出てきたら成功です。
  ![my_image](simulator.png)
 

# シミュレーターの使い方
