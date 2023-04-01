## 概要
MacでChatGPT付きの伺かっぽい倣かを動かす

## 環境構築
pythonとpoetryを用意する。
（省略）

仮想環境を構築する。
```
poetry install
```

## ビルド
下記コマンドでmac用の実行ファイル(appファイル)が作成できます。
```
poetry run pyinstaller main.spec
```

## 実行
ビルドしないでも環境構築後下記コマンドで実行できます。
```
poetry run python main.py
```


