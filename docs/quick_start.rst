.. _quick_start:

クイックスタート
================

使い方1: コマンドラインで利用する
---------------------------------

Tablelinker パッケージをモジュールとして実行すると、
CSV や Excel の表データを読み込み、 JSON ファイルに記述したタスクを実行し、
結果を CSV データとして出力するコマンドとして利用できます。

実行例は次のようになります。

.. code-block:: bash

    $ python -m tablelinker -i opendata.xlsx -o clean_opendata.csv task.json

``task.json`` には適用したいコンバータと、
そのコンバータに渡すパラメータを次のような JSON で記述します。

.. code-block:: json

    {
        "convertor":"rename_col",
        "params":{
            "input_col_idx": "市区町村コード",
            "output_col_name": "都道府県コード又は市区町村コード"
        }
    }

複数のコンバータを一つの JSON ファイルに書くこともできるので、
一度手順を書いておけば簡単に繰り返して実行できます。


使い方2: Python パッケージとして利用する
----------------------------------------

Tablelinker パッケージを Python スクリプトに import することで、
表データの読み込み、変換、出力機能を利用できます。

簡単な利用例を示します。

.. code-block:: python

    from tablelinker import Table
    table = Table("opendata.xlsx")  # Excel ファイルを読み込み
    table = table.convert({         # コンバータで変換
        convertor="rename_col",     # コンバータ名
        params={                    # コンバータに渡すパラメータ
            "input_col_idx": "市区町村コード",      # 入力列名
            "output_col_name":
                "都道府県コード又は市区町村コード"  # 出力列名
        }
    })
    table.save("renamed_opendata.csv")

上記の例は、``opendata.xlsx`` を読み込み、「市区町村コード」列を
「都道府県コード又は市区町村コード」列に変更します。
その結果を ``renamed_opendata.csv`` に出力します。

Python スクリプトから直接 Table オブジェクトが管理している CSV データにアクセスすることもできるので、ファイルの読み込みや
簡単な整形処理は Tablelinker で実装し、
それ以降の複雑な処理は独自に実装するといった使い方ができます。
