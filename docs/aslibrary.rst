.. _as_library:

パッケージとして利用
====================

Tablelinker を Python アプリケーションやスクリプトに読み込み、
CSV ファイルの読み込みやクレンジング、変換処理を利用できます。

変換した結果の表データは `pandas <http://pandas.pydata.org/>`_ の
DataFrame に変換することもできるので、 CSV ファイル以外の
フォーマットで保存したり、RDB のテーブルを作成することもできます。

Table オブジェクト作成
----------------------

表データは: ref: `Table` クラスのオブジェクトとして管理します。
Table オブジェクトを作成するには、次の2つの方法があります。

- CSV ファイルを開く
- pandas.DataFrame から変換する

CSV ファイルから Table オブジェクトを作成するコードの例を示します。 ::

    from tablelinker import Table
    table = Table("sample/ma0300000.csv")

pandas.DataFrame から Table オブジェクトを作成するコードの例をしまします。 ::

    import pandas as pd
    from tablelinker import Table
    df = pd.DataFrame({
        "都道府県名": ["北海道", "青森県", "岩手県"],
        "人口": [5188441, 1232227, 1203203],
    })
    table = Table.fromPandas(df)

