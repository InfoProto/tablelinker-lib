# tablelinker-lib

TableLinker をコマンドライン / プログラム組み込みで利用するためのライブラリ。

## インストール手順

Poetry を利用します。

```
$ poetry install
$ poetry shell
```

## コマンドラインで利用する場合

`pipe.py` を実行すると、標準入力から受け取った CSV をコンバータで変換し、
標準出力に送るパイプとして利用できます。

```
$ cat sample/sakurai_sightseeing_spots.csv | \
  python pipe.py sample/task.json
```

利用するコンバータと、コンバータに渡すパラメータは JSON ファイルに記述し、
pipe.py のパラメータで指定します。

## 組み込んで利用する場合

`sample.py` を参照してください。
