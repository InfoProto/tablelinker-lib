.. _quick_start:

クイックスタート
================

使い方1: Python パッケージとして利用する
----------------------------------------

Tablelinker パッケージを Python スクリプトに import することで、
表データの読み込み、変換、出力機能を利用できます。

簡単な利用例を示します。

.. code-block:: python

    from tablelinker import Table
    table = Table("opendata.csv")   # csv を読み込み
    table = table.convert({         # コンバータで変換
        convertor="rename_col",     # コンバータ名
        params={                    # コンバータに渡すパラメータ
            "input_attr_idx": "市区町村コード",     # 入力列名
            "output_attr_name":
                "都道府県コード又は市区町村コード"  # 出力列名
        }
    })
    table.save("renamed_opendata.csv")

上記の例は、``opendata.csv`` を読み込み、「市区町村コード」列を
「都道府県コード又は市区町村コード」列に変更します（1行目の
列見出しを書き換えます）。
その結果を ``renamed_opendata.csv`` に出力します。

Python スクリプトから直接 Table オブジェクトが管理している CSV データにアクセスすることもできるので、ファイルの読み込みや
簡単な整形処理は Tablelinker で実装し、
それ以降の複雑な処理は独自に実装するといった使い方ができます。

使い方2: コマンドラインで利用する
---------------------------------

Tablelinker パッケージをモジュールとして実行すると、
表データを標準入力から受け取り、 JSON ファイルに記述した
タスクを実行し、結果の CSV データを標準出力に書き出す
コマンドのように利用できます。

実行例は次のようになります。

.. code-block:: bash

    $ cat opendata.xlsx | python -m tablelinker task.json > clean_opendata.csv

``task.json`` には適用したいコンバータと、
そのコンバータに渡すパラメータを JSON で記述します。

.. code-block:: json

    {
        "convertor":"rename_col",
        "params":{
            "input_attr_idx": "市区町村コード",
            "output_attr_name": "都道府県コード又は市区町村コード"
        }
    }

複数のコンバータを一つの JSON ファイルに書くこともできるので、
一定時間ごとに更新される CSV データを何度も変換したい場合など、
一度手順を書いておけば簡単に繰り返し実行できます。
