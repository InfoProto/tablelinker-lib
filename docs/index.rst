.. tablelinker documentation master file, created by
    sphinx-quickstart on Mon Jan 16 05:05:34 2023.
    You can adapt this file completely to your liking, but it should at least
    contain the root `toctree` directive.

Tablelinker ドキュメント
========================

Tablelinker は CSV 形式の表データを読み込み、
さまざまな :ref:`convertor` を適用して変換・加工し、
目的のフォーマットの表データを生成するツールです。

CSV の入力、変換、出力という処理はデータ解析の前処理として
頻繁に行われますが、個々の処理はそれほど難しくないため、
何度も同じようなコードが実装されています。
しかし実際の CSV データには、文字エンコーディングや
区切り文字の混在、作成時のミスによる列名の表記揺れや
列の入れ替わりといった細かい問題が含まれていることが多く、
その都度対応するコードを実装すると想定以上に
手間がかかることがあります。

Tablelinker はよく利用される変換処理をライブラリ化し、
オープンソースとして公開することで、データのクリーニングや
バリデーションといったデータ解析の前処理を共有し、
再利用を進めることを目標としています。

使い方1: Python パッケージとして利用する
----------------------------------------

Tablelinker パッケージを Python スクリプトに import することで、
CSV の読み込み、変換、出力機能を利用できます。

簡単な利用例を示します。

.. code-block:: python

    from tablelinker import Table
    table = Table("opendata.csv")   # csv を読み込み
    table = table.convert({         # コンバータで変換
        convertor="select_string_contains",  # コンバータ名
        params={                    # コンバータに渡すパラメータ
            "input_attr_idx": "所在地",  # 入力列指定
            "query": "千代田区"          # クエリ文字列
        }
    })
    table.save("clean_opendata.csv")

上記の例は、``opendata.csv`` を読み込み、「所在地」列に
「千代田区」を部分文字列として含む行だけを選択する処理を実行し
（見出し行は残ります）、結果を ``clean_opendata.csv`` に出力します。

Python スクリプトから直接 Table オブジェクトが管理している CSV データにアクセスすることもできるので、データ解析の前処理に必要な
CSV ファイルの読み込みや簡単な整形処理を Tablelinker で実装し、
それ以降の複雑な処理は独自に実装するといった使い方ができます。

使い方2: コマンドラインで利用する
---------------------------------

Tablelinker パッケージをモジュールとして実行すると、
CSV データを標準入力から受け取り、 JSON ファイルに記述した
タスクを実行し、結果の CSV データを標準出力に書き出す
コマンドのように利用できます。

実行例は次のようになります。

.. code-block:: bash

    $ cat opendata.csv | python -m tablelinker task.json > clean_opendata.csv

``task.json`` には適用したいコンバータと、
そのコンバータに渡すパラメータを JSON で記述します。

.. code-block:: json

    {
        "convertor":"select_string_contains",
        "params":{
            "input_attr_idx": "所在地",
            "query": "千代田区"
        }
    }

複数のコンバータとパラメータのペアを配列として列挙すれば、
複数のタスクを順番に適用することもできます。

一定時間ごとに更新される CSV データを何度も変換したい場合など、
一度手順を書いておけば簡単に繰り返し実行できます。

次のステップ
------------

インストール手順やコンバータの種類、より詳しい使い方については、
以下の文書を参照してください。

.. toctree::
    :maxdepth: 2
    :caption: 目次

    install
    as_library
    as_command
    convertor
    api
