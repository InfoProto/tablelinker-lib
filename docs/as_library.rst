.. _as_library:

パッケージとして利用
====================

Tablelinker を Python アプリケーションやスクリプトに読み込むと、
表データの読み込みやクリーニングなどの処理を簡単に実装できます。

変換した表データは CSV ファイルとして保存したり、
一行ずつ取り出して Python コード内で利用できます。

より高度な使い方として、 `pandas <http://pandas.pydata.org/>`_
の DataFrame を Tablelinker に読み込んだり、
Tablelinker で変換した結果の表データを DataFrame に
変換することもできます。
詳細は :ref:`use_with_pandas` を参照してください。

- サンプルデータのダウンロード

    このページでは厚生労働省の「人口動態調査(2020年)」の
    `上巻_3-3-1_都道府県（特別区－指定都市再掲）別にみた人口動態総覧 <https://www.data.go.jp/data/dataset/mhlw_20211015_0019>`_ から
    ダウンロードできる ``ma030000.csv`` をサンプルとして利用します。

CSV を開く
----------

表データは :py:class:`~tablelinker.table.Table` クラスの
オブジェクトとして管理します。
CSV ファイルから Table オブジェクトを作成するコードの例を示します。

.. code-block:: python

    >>> from tablelinker import Table
    >>> table = Table("ma030000.csv")

.. note::

    CSV ファイルの文字エンコーディングが Shift JIS であったり、
    タブ区切りや先頭部分にコメントなどが含まれているような場合も、
    読み込む際に自動的に判定して対応します。

表データの表示
--------------

:py:class:`~tablelinker.table.Table` オブジェクトが管理している
CSV ファイルを表示するには、 :py:meth:`~tablelinker.table.Table.write`
メソッドを呼び出します。

``lines`` オプションパラメータで表示する
行数を制限できます（省略すると全行表示します）。

.. code-block:: python

    >>> table.write(lines=10)
    ,人口,出生数,死亡数,（再掲）,,自　然,死産数,,,周産期死亡数,,,婚姻件数,離婚件数
    ,,,,乳児死亡数,新生児,増減数,総数,自然死産,人工死産,総数,22週以後,早期新生児,,
    ,,,,,死亡数,,,,,,の死産数,死亡数,,
    全　国,123398962,840835,1372755,1512,704,-531920,17278,8188,9090,2664,2112,552,525507,193253
    01 北海道,5188441,29523,65078,59,25,-35555,728,304,424,92,75,17,20904,9070
    02 青森県,1232227,6837,17905,18,15,-11068,145,87,58,32,17,15,4032,1915
    03 岩手県,1203203,6718,17204,8,3,-10486,150,90,60,21,19,2,3918,1679
    04 宮城県,2280203,14480,24632,27,15,-10152,311,141,170,56,41,15,8921,3553
    05 秋田県,955659,4499,15379,9,4,-10880,98,63,35,18,15,3,2686,1213
    06 山形県,1060586,6217,15348,14,9,-9131,119,66,53,22,16,6,3530,1362

コンバータの適用
----------------

:py:class:`~tablelinker.table.Table` オブジェクトに
:ref:`convertor` を適用することで、さまざまな変換処理を行うことができます。
コンバータを適用するには :py:meth:`~tablelinker.table.Table.convert`
メソッドを呼び出します。

メソッドのパラメータとして、利用するコンバータ名を表す ``convertor`` と、
そのコンバータに渡すパラメータ ``params`` を指定する必要があります。

まず先頭の列名が空欄なので、列名を変更する
:py:class:`rename_col <tablelinker.convertors.basics.rename_col.RenameColConvertor>`
コンバータを利用して「都道府県名」に変更します。

.. code-block:: python

    >>> table = table.convert(
    ...     convertor='rename_col',
    ...     params={
    ...         'input_col_idx': 0,
    ...         'output_col_name': '都道府県名',
    ...    }
    ... )

次に列の選択と並び替えを行う
:py:class:`reorder_cols <tablelinker.convertors.basics.reorder_col.ReorderColsConvertor>`
コンバータを利用して、「都道府県名」「人口」「出生数」「死亡数」の
4列を抜き出します。

.. code-block:: python

    >>> table = table.convert(
    ...     convertor='reorder_cols',
    ...     params={
    ...         'column_list':['都道府県名','人口','出生数','死亡数'],
    ...     })

.. note::

    利用できるコンバータおよびパラメータについては
    :ref:`convertor` を参照してください。

CSV ファイルに保存
------------------

変換した結果を :py:meth:`~tablelinker.table.Table.save()`
メソッドで CSV ファイルに保存します。

.. code-block:: python

    >>> table.save('ma030000_clean.csv')

保存した CSV ファイルは次のようになります。

.. code-block:: bash

    $ cat ma03000_clean.csv
    都道府県名,人口,出生数,死亡数
    ,,,
    ,,,
    全　国,123398962,840835,1372755
    01 北海道,5188441,29523,65078
    02 青森県,1232227,6837,17905
    03 岩手県,1203203,6718,17204
    04 宮城県,2280203,14480,24632
    05 秋田県,955659,4499,15379
    06 山形県,1060586,6217,15348
    ...

表データにアクセス
------------------

Python プログラム内で、Table オブジェクトが参照する表データに
ファイルを経由せずに直接アクセスしたい場合、
:py:meth:`~tablelinker.table.Table.open` メソッドで
``csv.reader`` オブジェクトを取得できます。

たとえば都道府県名が空欄の行をスキップするコードは次のように書けます。

.. code-block:: python

    >>> with table.open() as reader:
    ...     for rows in reader:
    ...         if rows[0] != '':
    ...             print(','.join(rows))
    ...
    都道府県名,人口,出生数,死亡数
    全　国,123398962,840835,1372755
    01 北海道,5188441,29523,65078
    02 青森県,1232227,6837,17905
    03 岩手県,1203203,6718,17204
    04 宮城県,2280203,14480,24632
    05 秋田県,955659,4499,15379
    06 山形県,1060586,6217,15348
    ...

.. _use_with_pandas:

Pandas 連携
-----------

Tablelinker のコンバータにはない複雑な変換処理を
実装する必要があったり、変換結果を Excel や RDBMS テーブルに
出力したい場合などは、 Pandas 連携機能を利用してください。

.. note::

    Excel ファイルや RDBMS の入出力に必要なライブラリ
    （xlrd, sqlalchemy など）を別途インストールする必要があります。

pandas.DataFrame から Table オブジェクトを作成するには
Table クラスメソッド
:py:meth:`~tablelinker.table.Table.fromPandas` を利用します。

.. code-block:: python

    >>> import pandas as pd
    >>> df = pd.DataFrame({
    ...     "都道府県名":["北海道", "青森県", "岩手県"],
    ...     "人口":[5188441, 1232227, 1203203],})
    >>> from tablelinker import Table
    >>> table = Table.fromPandas(df)
    >>> table.write()
    都道府県名,人口
    北海道,5188441
    青森県,1232227
    岩手県,1203203

Table オブジェクトから pandas.DataFrame を作成するには、
:py:meth:`~tablelinker.table.Table.toPandas` メソッドを呼び出します。

.. code-block:: python

    >>> new_df = table.toPandas()
    >>> new_df.columns
    Index(['都道府県名', '人口'], dtype='object')
    >>> new_df.to_json(force_ascii=False)
    '{"都道府県名":{"0":"北海道","1":"青森県","2":"岩手県"},"人口":{"0":5188441,"1":1232227,"2":1203203}}'

.. note::

    DataFrame オブジェクトが利用可能なメソッドは 
    `Pandas API reference (DataFrame) <https://pandas.pydata.org/docs/reference/frame.html>`_
    を参照してください。
