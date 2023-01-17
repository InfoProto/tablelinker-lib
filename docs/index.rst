.. tablelinker documentation master file, created by
    sphinx-quickstart on Mon Jan 16 05:05:34 2023.
    You can adapt this file completely to your liking, but it should at least
    contain the root `toctree` directive.

Tablelinker ドキュメント
========================

Tablelinker は CSV 形式の表データを読み込み、
さまざまな :ref:`convertor` を適用して変換・加工し、
目的のフォーマットの表データを生成するツールです。

CSV の入力、変換、出力という処理はデータの前処理として
頻繁に行われますが、個々の処理はそれほど難しくないため
何度も同じようなコードが実装されています。

Tablelinker はよく利用される変換処理をライブラリ化し、
オープンソースとして公開することで、より多くの処理を
集合知として共有することを目標としています。

使い方1: Python ライブラリ
--------------------------

Tablelinker パッケージを Python スクリプトに import することで、
CSV の読み込み、変換、出力機能を利用できます。

簡単な利用サンプルを示します。

.. code-block:: python

    from tablelinker import Table
    import tablelinker.convertors.basics as basic_convertors
    table = Table("opendata.csv")  # csv を読み込み
    table = table.convert({        # コンバータで変換
        "select_string_contains":{  # コンバータ名
            "input_attr_idx": "所在地",  # 入力列指定
            "query": "千代田区"          # クエリ文字列
    }})
    table.save("clean_opendata.csv")

上記の例は、"opendata.csv" を読み込み、"所在地" 列に
"千代田区" を部分文字列として含む行だけを選択する処理を実行し
（見出し行は残ります）、結果を "clean_opendata.csv" に出力します。


使い方2: コマンドライン
-----------------------

Tablelinker パッケージをモジュール実行すると、
CSV を標準入力から受け取り、 JSON で記述したタスクを実行し、
結果の CSV を標準出力に書き出すパイプコマンドとして利用できます。

実行例は次のようになります。

.. code-block:: bash

    $ cat opendata.csv | python -m tablelinker task.json > clean_opendata.csv

`task.json` には次のように記述します。

.. code-block:: json

    [{
        "convertor":"select_string_contains",
        "params":{
            "input_attr_idx": "所在地",
            "query": "千代田区"
        }
    }]

JSON ファイルに複数のコンバータを列挙すれば、順番に適用します。


インストール手順やコンバータの種類については、
以下の文書を参照してください。

.. toctree::
    :maxdepth: 2
    :caption: Contents:

    install
    aslibrary
    convertor


インデックス
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
